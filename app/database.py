import os
import psycopg2
from psycopg2.extras import RealDictCursor

""" Módulo para manejar la conexión a la base de datos PostgreSQL y ejecutar consultas SQL.
Proporciona funciones para abrir conexiones, ejecutar consultas con parámetros y manejar errores."""

# Evita que psycopg2 intente leer pgpass.conf, cuya codificación puede
# diferir de UTF-8 en sistemas Windows con configuración regional en español.
os.environ.setdefault('PGPASSFILE', os.devnull)

# Datos de conexión (son los de docker-compose.yml)
DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "vtt_database",
    "user":     "vtt_admin",
    "password": "vtt_password"
}

#Funciones

def get_connection():
    """Abre una conexión a la base de datos y devuelve el objeto de conexión."""
    return psycopg2.connect(**DB_CONFIG)

def execute_query(sql, params=None, fetchall=False, fetchone=False):
    """Ejecuta queries SQL con seguridad y manejo de errores.
    params: Evita las inyecciones SQL
    fetchall: si True, devuelve todas las filas
    fetchone: si True, devuelve solo la primera fila
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(sql, params)

            if fetchall:
                resultado = cursor.fetchall()
            elif fetchone:
                resultado = cursor.fetchone()
            else:
                resultado = None

            conn.commit()  # ← ahora siempre llega aquí
            return resultado

    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()