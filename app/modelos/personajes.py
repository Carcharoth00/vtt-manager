from app.database import execute_query

# CREATE ----------------
def crear_personaje(campana_id, usuario_id, nombre, raza=None,
                    clase=None, notas=None):
    """Crea un personaje y sus estadísticas iniciales automáticamente."""
    from app.database import get_connection
    from psycopg2.extras import RealDictCursor

    conn = None
    try:
        conn = get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:

            # Inserta el personaje
            cursor.execute("""
                INSERT INTO personajes
                    (campana_id, usuario_id, nombre, raza, clase, notas)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, nombre, raza, clase, nivel, experiencia
            """, (campana_id, usuario_id, nombre, raza, clase, notas))
            personaje = cursor.fetchone()

            # Inserta las estadísticas usando el id recién creado
            cursor.execute("""
                INSERT INTO estadisticas (personaje_id)
                VALUES (%s)
            """, (personaje['id'],))

            conn.commit()
            return personaje

    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

# READ ----------------
def obtener_personajes_de_campana(campana_id):
    """Devuelve todos los personajes de una campaña (vista del master)."""
    sql = """
        SELECT p.id, p.nombre, p.raza, p.clase, p.nivel,
               p.imagen_ruta, u.nombre_usuario AS jugador
        FROM personajes p
        LEFT JOIN usuarios u ON p.usuario_id = u.id
        WHERE p.campana_id = %s
        ORDER BY p.nombre
    """
    return execute_query(sql, params=(campana_id,), fetchall=True)

def obtener_personajes_de_usuario(campana_id, usuario_id):
    """Devuelve los personajes de un jugador en una campaña concreta."""
    sql = """
        SELECT id, nombre, raza, clase, nivel, experiencia, imagen_ruta, notas
        FROM personajes
        WHERE campana_id = %s AND usuario_id = %s
    """
    return execute_query(sql, params=(campana_id, usuario_id), fetchall=True)

def obtener_personaje_completo(personaje_id):
    """Devuelve un personaje con sus estadísticas e inventario."""
    sql = """
        SELECT p.*, e.fuerza, e.destreza, e.constitucion,
               e.inteligencia, e.sabiduria, e.carisma,
               e.vida_max, e.vida_actual
        FROM personajes p
        LEFT JOIN estadisticas e ON p.id = e.personaje_id
        WHERE p.id = %s
    """
    personaje = execute_query(sql, params=(personaje_id,), fetchone=True)

    if personaje:
        sql_inv = """
            SELECT id, nombre_objeto, tipo, descripcion, cantidad
            FROM inventario
            WHERE personaje_id = %s
        """
        personaje['inventario'] = execute_query(
            sql_inv,
            params=(personaje_id,),
            fetchall=True
        )
    return personaje

# UPDATE ----------------
def actualizar_personaje(personaje_id, nombre=None, raza=None,
                         clase=None, nivel=None, experiencia=None,
                         imagen_ruta=None, notas=None):
    """Actualiza los datos de un personaje."""
    sql = """
        UPDATE personajes
        SET nombre      = COALESCE(%s, nombre),
            raza        = COALESCE(%s, raza),
            clase       = COALESCE(%s, clase),
            nivel       = COALESCE(%s, nivel),
            experiencia = COALESCE(%s, experiencia),
            imagen_ruta = COALESCE(%s, imagen_ruta),
            notas       = COALESCE(%s, notas)
        WHERE id = %s
        RETURNING id, nombre, raza, clase, nivel, experiencia
    """
    return execute_query(
        sql,
        params=(nombre, raza, clase, nivel, experiencia,
                imagen_ruta, notas, personaje_id),
        fetchone=True
    )

def actualizar_estadisticas(personaje_id, fuerza=None, destreza=None,
                             constitucion=None, inteligencia=None,
                             sabiduria=None, carisma=None,
                             vida_max=None, vida_actual=None):
    """Actualiza las estadísticas de un personaje."""
    sql = """
        UPDATE estadisticas
        SET fuerza       = COALESCE(%s, fuerza),
            destreza     = COALESCE(%s, destreza),
            constitucion = COALESCE(%s, constitucion),
            inteligencia = COALESCE(%s, inteligencia),
            sabiduria    = COALESCE(%s, sabiduria),
            carisma      = COALESCE(%s, carisma),
            vida_max     = COALESCE(%s, vida_max),
            vida_actual  = COALESCE(%s, vida_actual)
        WHERE personaje_id = %s
        RETURNING *
    """
    return execute_query(
        sql,
        params=(fuerza, destreza, constitucion, inteligencia,
                sabiduria, carisma, vida_max, vida_actual, personaje_id),
        fetchone=True
    )

def añadir_objeto(personaje_id, nombre_objeto, tipo=None,
                  descripcion=None, cantidad=1):
    """Añade un objeto al inventario de un personaje."""
    sql = """
        INSERT INTO inventario
            (personaje_id, nombre_objeto, tipo, descripcion, cantidad)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id, nombre_objeto, tipo, cantidad
    """
    return execute_query(
        sql,
        params=(personaje_id, nombre_objeto, tipo, descripcion, cantidad),
        fetchone=True
    )

# DELETE ----------------
def eliminar_personaje(personaje_id):
    """Elimina un personaje y todo lo asociado (CASCADE)."""
    sql = "DELETE FROM personajes WHERE id = %s"
    execute_query(sql, params=(personaje_id,))

def eliminar_objeto(objeto_id):
    """Elimina un objeto del inventario."""
    sql = "DELETE FROM inventario WHERE id = %s"
    execute_query(sql, params=(objeto_id,))
