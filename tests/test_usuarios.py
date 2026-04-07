import pytest
from app.modelos.usuarios import (
    crear_usuario,
    obtener_usuarios,
    obtener_usuario_por_id,
    verificar_login,
    actualizar_usuario,
    actualizar_contrasena,
    eliminar_usuario,
)


class TestCrearUsuario:
    def test_devuelve_campos_correctos(self, db_conn):
        u = crear_usuario("alice", "alice@test.com", "secret")
        assert u["nombre_usuario"] == "alice"
        assert u["email"] == "alice@test.com"
        assert "id" in u
        assert "fecha_registro" in u

    def test_no_devuelve_contrasena(self, db_conn):
        u = crear_usuario("bob", "bob@test.com", "secret")
        assert "contrasena_hash" not in u

    def test_nombre_duplicado_lanza_excepcion(self, db_conn):
        crear_usuario("dup_user", "first@test.com", "secret")
        with pytest.raises(Exception):
            crear_usuario("dup_user", "second@test.com", "secret")

    def test_email_duplicado_lanza_excepcion(self, db_conn):
        crear_usuario("user_a", "shared@test.com", "secret")
        with pytest.raises(Exception):
            crear_usuario("user_b", "shared@test.com", "secret")


class TestObtenerUsuarios:
    def test_devuelve_lista(self, db_conn):
        result = obtener_usuarios()
        assert isinstance(result, list)

    def test_nuevo_usuario_aparece_en_lista(self, db_conn):
        crear_usuario("listuser", "list@test.com", "pass")
        usuarios = obtener_usuarios()
        nombres = [u["nombre_usuario"] for u in usuarios]
        assert "listuser" in nombres

    def test_campos_no_incluyen_contrasena(self, db_conn):
        crear_usuario("safeuser", "safe@test.com", "pass")
        for u in obtener_usuarios():
            assert "contrasena_hash" not in u


class TestObtenerUsuarioPorId:
    def test_devuelve_usuario_correcto(self, db_conn):
        creado = crear_usuario("byid", "byid@test.com", "pass")
        encontrado = obtener_usuario_por_id(creado["id"])
        assert encontrado["id"] == creado["id"]
        assert encontrado["nombre_usuario"] == "byid"

    def test_id_inexistente_devuelve_none(self, db_conn):
        resultado = obtener_usuario_por_id("00000000-0000-0000-0000-000000000000")
        assert resultado is None


class TestVerificarLogin:
    def test_credenciales_correctas(self, db_conn):
        crear_usuario("loginuser", "login@test.com", "mypassword")
        result = verificar_login("loginuser", "mypassword")
        assert result is not None
        assert result["nombre_usuario"] == "loginuser"

    def test_contrasena_incorrecta_devuelve_none(self, db_conn):
        crear_usuario("loginuser2", "login2@test.com", "correct")
        assert verificar_login("loginuser2", "wrong") is None

    def test_usuario_inexistente_devuelve_none(self, db_conn):
        assert verificar_login("no_existe", "cualquier_cosa") is None

    def test_no_devuelve_contrasena_en_resultado(self, db_conn):
        crear_usuario("safelogin", "safelogin@test.com", "pass")
        result = verificar_login("safelogin", "pass")
        assert "contrasena_hash" not in result


class TestActualizarUsuario:
    def test_actualizar_nombre(self, db_conn):
        u = crear_usuario("old_name", "old@test.com", "pass")
        updated = actualizar_usuario(u["id"], nombre_usuario="new_name")
        assert updated["nombre_usuario"] == "new_name"

    def test_actualizar_email(self, db_conn):
        u = crear_usuario("emailuser", "old@test.com", "pass")
        updated = actualizar_usuario(u["id"], email="new@test.com")
        assert updated["email"] == "new@test.com"

    def test_actualizar_sin_parametros_mantiene_valores(self, db_conn):
        u = crear_usuario("unchanged", "unchanged@test.com", "pass")
        updated = actualizar_usuario(u["id"])
        assert updated["nombre_usuario"] == "unchanged"

    def test_nombre_duplicado_lanza_excepcion(self, db_conn):
        crear_usuario("existing", "existing@test.com", "pass")
        u2 = crear_usuario("other", "other@test.com", "pass")
        with pytest.raises(Exception):
            actualizar_usuario(u2["id"], nombre_usuario="existing")


class TestActualizarContrasena:
    def test_nueva_contrasena_funciona(self, db_conn):
        u = crear_usuario("passuser", "passuser@test.com", "old_pass")
        actualizar_contrasena(u["id"], "new_pass")
        assert verificar_login("passuser", "old_pass") is None
        assert verificar_login("passuser", "new_pass") is not None

    def test_devuelve_datos_de_usuario(self, db_conn):
        u = crear_usuario("passuser2", "passuser2@test.com", "pass")
        result = actualizar_contrasena(u["id"], "newpass")
        assert result["id"] == u["id"]


class TestEliminarUsuario:
    def test_usuario_eliminado_no_aparece(self, db_conn):
        u = crear_usuario("todelete", "delete@test.com", "pass")
        eliminar_usuario(u["id"])
        assert obtener_usuario_por_id(u["id"]) is None

    def test_eliminar_id_inexistente_no_lanza_excepcion(self, db_conn):
        eliminar_usuario("00000000-0000-0000-0000-000000000000")
