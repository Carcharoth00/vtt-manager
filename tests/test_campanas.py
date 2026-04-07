import pytest
from app.modelos.campanas import (
    crear_campana,
    añadir_miembro,
    obtener_campanas,
    obtener_campana_por_id,
    obtener_campanas_de_usuario,
    actualizar_campana,
    actualizar_rol,
    eliminar_campana,
    eliminar_miembro,
)
from app.modelos.usuarios import crear_usuario


class TestCrearCampana:
    def test_devuelve_campos_correctos(self, db_conn):
        c = crear_campana("Test Campaign")
        assert c["nombre"] == "Test Campaign"
        assert "id" in c
        assert c["estado"] == "activa"

    def test_estado_inicial_es_activa(self, db_conn):
        c = crear_campana("Another Campaign")
        assert c["estado"] == "activa"

    def test_crea_con_master(self, db_conn, usuario):
        c = crear_campana("Con Master", master_id=usuario["id"])
        detalle = obtener_campana_por_id(c["id"])
        roles = {m["id"]: m["rol"] for m in detalle["miembros"]}
        assert roles[usuario["id"]] == "master"

    def test_crea_sin_master(self, db_conn):
        c = crear_campana("Sin Master")
        detalle = obtener_campana_por_id(c["id"])
        assert detalle["miembros"] == []

    def test_descripcion_y_notas(self, db_conn):
        c = crear_campana("Desc Test", descripcion="Una desc", notas="Una nota")
        detalle = obtener_campana_por_id(c["id"])
        assert detalle["descripcion"] == "Una desc"
        assert detalle["notas"] == "Una nota"


class TestAnadirMiembro:
    def test_añade_jugador(self, db_conn, campana):
        jugador = crear_usuario("jugador1", "jugador1@test.com", "pass")
        resultado = añadir_miembro(campana["id"], jugador["id"], rol="jugador")
        assert resultado["rol"] == "jugador"

    def test_añade_master(self, db_conn, campana):
        nuevo = crear_usuario("master2", "master2@test.com", "pass")
        resultado = añadir_miembro(campana["id"], nuevo["id"], rol="master")
        assert resultado["rol"] == "master"

    def test_rol_invalido_lanza_excepcion(self, db_conn, campana, usuario):
        with pytest.raises(Exception):
            añadir_miembro(campana["id"], usuario["id"], rol="spectator")

    def test_miembro_duplicado_lanza_excepcion(self, db_conn, campana, usuario):
        with pytest.raises(Exception):
            añadir_miembro(campana["id"], usuario["id"], rol="jugador")

    def test_rol_por_defecto_es_jugador(self, db_conn, campana):
        nuevo = crear_usuario("defrol", "defrol@test.com", "pass")
        resultado = añadir_miembro(campana["id"], nuevo["id"])
        assert resultado["rol"] == "jugador"


class TestObtenerCampanas:
    def test_devuelve_lista(self, db_conn):
        result = obtener_campanas()
        assert isinstance(result, list)

    def test_nueva_campana_aparece_en_lista(self, db_conn):
        crear_campana("Visible Campaign")
        nombres = [c["nombre"] for c in obtener_campanas()]
        assert "Visible Campaign" in nombres

    def test_campos_presentes(self, db_conn):
        crear_campana("Fields Test")
        for c in obtener_campanas():
            for campo in ("id", "nombre", "estado", "fecha_creacion"):
                assert campo in c


class TestObtenerCampanaPorId:
    def test_devuelve_campana_correcta(self, db_conn, campana):
        encontrada = obtener_campana_por_id(campana["id"])
        assert encontrada["id"] == campana["id"]

    def test_incluye_lista_de_miembros(self, db_conn, campana):
        encontrada = obtener_campana_por_id(campana["id"])
        assert "miembros" in encontrada
        assert isinstance(encontrada["miembros"], list)

    def test_id_inexistente_devuelve_none(self, db_conn):
        assert obtener_campana_por_id("00000000-0000-0000-0000-000000000000") is None

    def test_miembros_tienen_campos_correctos(self, db_conn, campana):
        encontrada = obtener_campana_por_id(campana["id"])
        for m in encontrada["miembros"]:
            assert "id" in m
            assert "nombre_usuario" in m
            assert "rol" in m


class TestObtenerCampanasDeUsuario:
    def test_devuelve_lista(self, db_conn, usuario, campana):
        result = obtener_campanas_de_usuario(usuario["id"])
        assert isinstance(result, list)

    def test_incluye_campana_del_usuario(self, db_conn, usuario, campana):
        ids = [c["id"] for c in obtener_campanas_de_usuario(usuario["id"])]
        assert campana["id"] in ids

    def test_incluye_rol(self, db_conn, usuario, campana):
        campanas = obtener_campanas_de_usuario(usuario["id"])
        roles = {c["id"]: c["rol"] for c in campanas}
        assert roles[campana["id"]] == "master"

    def test_usuario_sin_campanas_devuelve_lista_vacia(self, db_conn):
        nuevo = crear_usuario("sin_campanas", "sinc@test.com", "pass")
        assert obtener_campanas_de_usuario(nuevo["id"]) == []


class TestActualizarCampana:
    def test_actualizar_nombre(self, db_conn, campana):
        updated = actualizar_campana(campana["id"], nombre="Nuevo Nombre")
        assert updated["nombre"] == "Nuevo Nombre"

    def test_actualizar_estado_a_pausada(self, db_conn, campana):
        updated = actualizar_campana(campana["id"], estado="pausada")
        assert updated["estado"] == "pausada"

    def test_actualizar_estado_a_finalizada(self, db_conn, campana):
        updated = actualizar_campana(campana["id"], estado="finalizada")
        assert updated["estado"] == "finalizada"

    def test_estado_invalido_lanza_excepcion(self, db_conn, campana):
        with pytest.raises(Exception):
            actualizar_campana(campana["id"], estado="archivada")

    def test_actualizar_sin_parametros_mantiene_valores(self, db_conn, campana):
        updated = actualizar_campana(campana["id"])
        assert updated["nombre"] == campana["nombre"]


class TestActualizarRol:
    def test_cambia_de_master_a_jugador(self, db_conn, campana, usuario):
        updated = actualizar_rol(campana["id"], usuario["id"], "jugador")
        assert updated["rol"] == "jugador"

    def test_cambia_de_jugador_a_master(self, db_conn, campana):
        jugador = crear_usuario("jugador_rol", "jugadorrol@test.com", "pass")
        añadir_miembro(campana["id"], jugador["id"], rol="jugador")
        updated = actualizar_rol(campana["id"], jugador["id"], "master")
        assert updated["rol"] == "master"

    def test_rol_invalido_lanza_excepcion(self, db_conn, campana, usuario):
        with pytest.raises(Exception):
            actualizar_rol(campana["id"], usuario["id"], "admin")


class TestEliminarCampana:
    def test_campana_eliminada_no_aparece(self, db_conn):
        c = crear_campana("To Delete")
        eliminar_campana(c["id"])
        assert obtener_campana_por_id(c["id"]) is None

    def test_eliminar_campana_elimina_miembros_en_cascada(self, db_conn, usuario):
        c = crear_campana("Cascade Test", master_id=usuario["id"])
        eliminar_campana(c["id"])
        ids = [x["id"] for x in obtener_campanas_de_usuario(usuario["id"])]
        assert c["id"] not in ids

    def test_eliminar_id_inexistente_no_lanza_excepcion(self, db_conn):
        eliminar_campana("00000000-0000-0000-0000-000000000000")


class TestEliminarMiembro:
    def test_miembro_eliminado_no_aparece_en_campana(self, db_conn, campana):
        jugador = crear_usuario("del_jugador", "deljug@test.com", "pass")
        añadir_miembro(campana["id"], jugador["id"])
        eliminar_miembro(campana["id"], jugador["id"])
        detalle = obtener_campana_por_id(campana["id"])
        ids = [m["id"] for m in detalle["miembros"]]
        assert jugador["id"] not in ids

    def test_campana_permanece_tras_eliminar_miembro(self, db_conn, campana):
        jugador = crear_usuario("rem_jugador", "remjug@test.com", "pass")
        añadir_miembro(campana["id"], jugador["id"])
        eliminar_miembro(campana["id"], jugador["id"])
        assert obtener_campana_por_id(campana["id"]) is not None
