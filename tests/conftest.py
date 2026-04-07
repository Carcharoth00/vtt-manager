import pytest
import psycopg2
from psycopg2.extras import RealDictCursor
import app.database as db_module


class _NoCommitConnection:
    """Envuelve una conexión real e inutiliza commit() y close()."""

    def __init__(self, real_conn):
        self._conn = real_conn

    def commit(self):
        pass

    def close(self):
        pass

    def __getattr__(self, name):
        return getattr(self._conn, name)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


@pytest.fixture()
def db_conn(monkeypatch):
    real_conn = psycopg2.connect(**db_module.DB_CONFIG)
    real_conn.autocommit = False
    proxy = _NoCommitConnection(real_conn)

    monkeypatch.setattr(db_module, "get_connection", lambda: proxy)

    def _execute_query(sql, params=None, fetchall=False, fetchone=False):
        with proxy.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            if fetchall:
                return cur.fetchall()
            if fetchone:
                return cur.fetchone()
            return None

    monkeypatch.setattr(db_module, "execute_query", _execute_query)

    yield proxy

    real_conn.rollback()
    real_conn.close()


@pytest.fixture()
def usuario(db_conn):
    from app.modelos.usuarios import crear_usuario
    return crear_usuario("test_user", "test@example.com", "password123")


@pytest.fixture()
def campana(db_conn, usuario):
    from app.modelos.campanas import crear_campana
    return crear_campana(
        nombre="Campaña de prueba",
        descripcion="Descripción de prueba",
        master_id=usuario["id"],
    )


@pytest.fixture()
def personaje(db_conn, campana, usuario):
    from app.modelos.personajes import crear_personaje
    return crear_personaje(
        campana_id=campana["id"],
        usuario_id=usuario["id"],
        nombre="Héroe de prueba",
        raza="Humano",
        clase="Guerrero",
    )
