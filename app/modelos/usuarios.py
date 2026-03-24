from app.database import execute_query
import hashlib # Para encriptar contraseñas

def hash_password(password):
    """Encripta la contraseña usando SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

# CREATE ----------------
def crear_usuario(nombre_usuario, email, password):
    """Crea un nuevo usuario. Devuelve el usuario creado."""
    sql = """
        INSERT INTO usuarios (nombre_usuario, email, contrasena_hash)
        VALUES (%s, %s, %s)
        RETURNING id, nombre_usuario, email, fecha_registro
    """
    return execute_query(
        sql,
        params=(nombre_usuario, email, hash_password(password)),
        fetchone=True
    )

# READ ----------------

def obtener_usuarios():
    """devuelve una lista de todos los usuarios registrados."""
    sql = "SELECT id, nombre_usuario, email, fecha_registro FROM usuarios;"
    return execute_query(sql, fetchall=True)

def obtener_usuario_por_id(usuario_id):
    """Devuelve un usuario por su ID."""
    sql = """
        SELECT id, nombre_usuario, email, fecha_registro
        FROM usuarios WHERE id = %s
    """
    return execute_query(sql, params=(usuario_id,), fetchone=True)

def verificar_login(nombre_usuario, password):
    """Verifica las credenciales. Devuelve el usuario si las credenciales son correctas, o None si no lo son."""
    sql = """
        SELECT id, nombre_usuario, email
        FROM usuarios
        WHERE nombre_usuario = %s AND contrasena_hash  = %s"""
    
    return execute_query(
        sql,
        params=(nombre_usuario, hash_password(password)),
        fetchone=True
    )

# UPDATE ----------------
def actualizar_usuario(usuario_id, nombre_usuario=None, email=None):
    """Actualiza nombre y/o email de un usuario."""
    sql = """
        UPDATE usuarios
        SET nombre_usuario = COALESCE(%s, nombre_usuario),
            email          = COALESCE(%s, email)
        WHERE id = %s
        RETURNING id, nombre_usuario, email
    """
    return execute_query(
        sql,
        params=(nombre_usuario, email, usuario_id),
        fetchone=True
    )

def actualizar_contrasena(usuario_id, nueva_contrasena):
    """Actualiza la contraseña de un usuario."""
    sql = """
        UPDATE usuarios
        SET contrasena_hash = %s
        WHERE id = %s
        RETURNING id, nombre_usuario, email
    """
    return execute_query(
        sql,
        params=(hash_password(nueva_contrasena), usuario_id),
        fetchone=True
    )

# DELETE ----------------
def eliminar_usuario(usuario_id):
    """Elimina un usuario por su ID."""
    sql = "DELETE FROM usuarios WHERE id = %s"
    execute_query(sql, params=(usuario_id,))