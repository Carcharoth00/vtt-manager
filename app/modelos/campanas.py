from app.database import execute_query

# CREATE ----------------
def crear_campana(nombre, descripcion=None, notas=None,
                  master_id=None):
    """Crea una campaña y opcionalmente añade al master en la misma transacción."""
    from app.database import get_connection
    from psycopg2.extras import RealDictCursor

    conn = None
    try:
        conn = get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:

            cursor.execute("""
                INSERT INTO campanas (nombre, descripcion, notas)
                VALUES (%s, %s, %s)
                RETURNING id, nombre, estado, fecha_creacion
            """, (nombre, descripcion, notas))
            campana = cursor.fetchone()

            # Si se proporciona un master, lo añade en la misma transacción
            if master_id:
                cursor.execute("""
                    INSERT INTO campanas_usuarios (campana_id, usuario_id, rol)
                    VALUES (%s, %s, 'master')
                """, (campana['id'], master_id))

            conn.commit()
            return campana

    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

def añadir_miembro(campana_id, usuario_id, rol='jugador'):
    """Añade un usuario a una campaña con un rol."""
    sql = """
        INSERT INTO campanas_usuarios (campana_id, usuario_id, rol)
        VALUES (%s, %s, %s)
        RETURNING campana_id, usuario_id, rol
    """
    return execute_query(
        sql,
        params=(campana_id, usuario_id, rol),
        fetchone=True
    )

# READ ----------------
def obtener_campanas():
    """Devuelve todas las campañas."""
    sql = """
        SELECT id, nombre, estado, descripcion, notas, fecha_creacion
        FROM campanas
        ORDER BY fecha_creacion DESC
    """
    return execute_query(sql, fetchall=True)

def obtener_campana_por_id(campana_id):
    """Devuelve una campaña con su lista de miembros."""
    sql = """
        SELECT id, nombre, estado, descripcion, notas, fecha_creacion
        FROM campanas WHERE id = %s
    """
    campana = execute_query(sql, params=(campana_id,), fetchone=True)

    if campana:
        # Consulta adicional para traer los miembros de esa campaña
        sql_miembros = """
            SELECT u.id, u.nombre_usuario, cu.rol
            FROM usuarios u
            JOIN campanas_usuarios cu ON u.id = cu.usuario_id
            WHERE cu.campana_id = %s
        """
        campana['miembros'] = execute_query(
            sql_miembros,
            params=(campana_id,),
            fetchall=True
        )
    return campana

def obtener_campanas_de_usuario(usuario_id):
    """Devuelve todas las campañas en las que participa un usuario."""
    sql = """
        SELECT c.id, c.nombre, c.estado, cu.rol
        FROM campanas c
        JOIN campanas_usuarios cu ON c.id = cu.campana_id
        WHERE cu.usuario_id = %s
        ORDER BY c.fecha_creacion DESC
    """
    return execute_query(sql, params=(usuario_id,), fetchall=True)

# UPDATE ----------------
def actualizar_campana(campana_id, nombre=None, estado=None,
                       descripcion=None, notas=None):
    """Actualiza los datos de una campaña."""
    sql = """
        UPDATE campanas
        SET nombre      = COALESCE(%s, nombre),
            estado      = COALESCE(%s, estado),
            descripcion = COALESCE(%s, descripcion),
            notas       = COALESCE(%s, notas)
        WHERE id = %s
        RETURNING id, nombre, estado, descripcion, notas
    """
    return execute_query(
        sql,
        params=(nombre, estado, descripcion, notas, campana_id),
        fetchone=True
    )

def actualizar_rol(campana_id, usuario_id, nuevo_rol):
    """Actualiza el rol de un usuario en una campaña."""
    sql = """
        UPDATE campanas_usuarios
        SET rol = %s
        WHERE campana_id = %s AND usuario_id = %s
        RETURNING campana_id, usuario_id, rol
    """
    return execute_query(
        sql,
        params=(nuevo_rol, campana_id, usuario_id),
        fetchone=True
    )

# DELETE ----------------
def eliminar_campana(campana_id):
    """Elimina una campaña y todo lo que contiene (CASCADE)."""
    sql = "DELETE FROM campanas WHERE id = %s"
    execute_query(sql, params=(campana_id,))

def eliminar_miembro(campana_id, usuario_id):
    """Elimina un usuario de una campaña."""
    sql = """
        DELETE FROM campanas_usuarios
        WHERE campana_id = %s AND usuario_id = %s
    """
    execute_query(sql, params=(campana_id, usuario_id))