import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Evita que psycopg2 intente leer pgpass.conf, cuya codificación puede
# diferir de UTF-8 en sistemas Windows con configuración regional en español.
os.environ.setdefault('PGPASSFILE', os.devnull)

load_dotenv()

DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     int(os.getenv("DB_PORT", 5432)),
    "dbname":   os.getenv("DB_NAME"),
    "user":     os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
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