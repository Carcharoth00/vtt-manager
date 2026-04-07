import pytest
from app.modelos.personajes import (
    crear_personaje,
    añadir_objeto,
    obtener_personajes_de_campana,
    obtener_personajes_de_usuario,
    obtener_personaje_completo,
    actualizar_personaje,
    actualizar_estadisticas,
    eliminar_personaje,
    eliminar_objeto,
)
from app.modelos.usuarios import crear_usuario
from app.modelos.campanas import crear_campana


class TestCrearPersonaje:
    def test_devuelve_campos_correctos(self, db_conn, campana, usuario):
        p = crear_personaje(campana["id"], usuario["id"], "Gandalf")
        assert p["nombre"] == "Gandalf"
        assert "id" in p
        assert p["nivel"] == 1
        assert p["experiencia"] == 0

    def test_crea_estadisticas_iniciales(self, db_conn, campana, usuario):
        p = crear_personaje(campana["id"], usuario["id"], "Frodo")
        completo = obtener_personaje_completo(p["id"])
        for stat in ("fuerza", "destreza", "constitucion",
                     "inteligencia", "sabiduria", "carisma"):
            assert completo[stat] == 10

    def test_acepta_raza_y_clase(self, db_conn, campana, usuario):
        p = crear_personaje(campana["id"], usuario["id"], "Legolas",
                            raza="Elfo", clase="Arquero")
        assert p["raza"] == "Elfo"
        assert p["clase"] == "Arquero"

    def test_inventario_inicial_vacio(self, db_conn, campana, usuario):
        p = crear_personaje(campana["id"], usuario["id"], "Bilbo")
        completo = obtener_personaje_completo(p["id"])
        assert completo["inventario"] == []


class TestAnadirObjeto:
    def test_añade_objeto_basico(self, db_conn, personaje):
        obj = añadir_objeto(personaje["id"], "Espada corta")
        assert obj["nombre_objeto"] == "Espada corta"
        assert "id" in obj

    def test_cantidad_por_defecto_es_uno(self, db_conn, personaje):
        obj = añadir_objeto(personaje["id"], "Poción")
        assert obj["cantidad"] == 1

    def test_cantidad_personalizada(self, db_conn, personaje):
        obj = añadir_objeto(personaje["id"], "Flechas", cantidad=20)
        assert obj["cantidad"] == 20

    def test_objeto_aparece_en_personaje_completo(self, db_conn, personaje):
        añadir_objeto(personaje["id"], "Escudo")
        completo = obtener_personaje_completo(personaje["id"])
        nombres = [o["nombre_objeto"] for o in completo["inventario"]]
        assert "Escudo" in nombres

    def test_cantidad_cero_es_valida(self, db_conn, personaje):
        obj = añadir_objeto(personaje["id"], "Monedas gastadas", cantidad=0)
        assert obj["cantidad"] == 0

    def test_cantidad_negativa_lanza_excepcion(self, db_conn, personaje):
        with pytest.raises(Exception):
            añadir_objeto(personaje["id"], "Negativo", cantidad=-1)


class TestObtenerPersonajesDeCampana:
    def test_devuelve_lista(self, db_conn, campana):
        result = obtener_personajes_de_campana(campana["id"])
        assert isinstance(result, list)

    def test_nuevo_personaje_aparece(self, db_conn, campana, usuario):
        crear_personaje(campana["id"], usuario["id"], "Aragorn")
        nombres = [p["nombre"] for p in obtener_personajes_de_campana(campana["id"])]
        assert "Aragorn" in nombres

    def test_incluye_nombre_jugador(self, db_conn, campana, usuario):
        crear_personaje(campana["id"], usuario["id"], "Strider")
        for p in obtener_personajes_de_campana(campana["id"]):
            assert "jugador" in p

    def test_campana_sin_personajes_devuelve_lista_vacia(self, db_conn):
        c = crear_campana("Vacía")
        assert obtener_personajes_de_campana(c["id"]) == []


class TestObtenerPersonajesDeUsuario:
    def test_devuelve_lista(self, db_conn, campana, usuario):
        result = obtener_personajes_de_usuario(campana["id"], usuario["id"])
        assert isinstance(result, list)

    def test_incluye_personaje_creado(self, db_conn, campana, usuario):
        crear_personaje(campana["id"], usuario["id"], "Mi Personaje")
        nombres = [p["nombre"] for p in
                   obtener_personajes_de_usuario(campana["id"], usuario["id"])]
        assert "Mi Personaje" in nombres

    def test_no_incluye_personajes_de_otro_usuario(self, db_conn, campana, usuario):
        otro = crear_usuario("otro_user", "otro@test.com", "pass")
        crear_personaje(campana["id"], otro["id"], "Personaje Ajeno")
        nombres = [p["nombre"] for p in
                   obtener_personajes_de_usuario(campana["id"], usuario["id"])]
        assert "Personaje Ajeno" not in nombres

    def test_campos_devueltos(self, db_conn, campana, usuario):
        crear_personaje(campana["id"], usuario["id"], "Campos Test")
        for p in obtener_personajes_de_usuario(campana["id"], usuario["id"]):
            for campo in ("id", "nombre", "raza", "clase", "nivel", "experiencia"):
                assert campo in p


class TestObtenerPersonajeCompleto:
    def test_devuelve_estadisticas(self, db_conn, personaje):
        completo = obtener_personaje_completo(personaje["id"])
        for stat in ("fuerza", "destreza", "constitucion",
                     "inteligencia", "sabiduria", "carisma",
                     "vida_max", "vida_actual"):
            assert stat in completo

    def test_devuelve_inventario(self, db_conn, personaje):
        completo = obtener_personaje_completo(personaje["id"])
        assert "inventario" in completo
        assert isinstance(completo["inventario"], list)

    def test_id_inexistente_devuelve_none(self, db_conn):
        assert obtener_personaje_completo("00000000-0000-0000-0000-000000000000") is None

    def test_inventario_refleja_objetos_añadidos(self, db_conn, personaje):
        añadir_objeto(personaje["id"], "Vara Mágica", tipo="Arma")
        completo = obtener_personaje_completo(personaje["id"])
        tipos = [o["tipo"] for o in completo["inventario"]]
        assert "Arma" in tipos


class TestActualizarPersonaje:
    def test_actualizar_nombre(self, db_conn, personaje):
        updated = actualizar_personaje(personaje["id"], nombre="Nuevo Nombre")
        assert updated["nombre"] == "Nuevo Nombre"

    def test_actualizar_nivel(self, db_conn, personaje):
        updated = actualizar_personaje(personaje["id"], nivel=5)
        assert updated["nivel"] == 5

    def test_actualizar_experiencia(self, db_conn, personaje):
        updated = actualizar_personaje(personaje["id"], experiencia=1500)
        assert updated["experiencia"] == 1500

    def test_nivel_cero_lanza_excepcion(self, db_conn, personaje):
        with pytest.raises(Exception):
            actualizar_personaje(personaje["id"], nivel=0)

    def test_experiencia_negativa_lanza_excepcion(self, db_conn, personaje):
        with pytest.raises(Exception):
            actualizar_personaje(personaje["id"], experiencia=-1)

    def test_actualizar_sin_parametros_mantiene_valores(self, db_conn, personaje):
        updated = actualizar_personaje(personaje["id"])
        assert updated["nombre"] == personaje["nombre"]

    def test_actualizar_raza_y_clase(self, db_conn, personaje):
        updated = actualizar_personaje(personaje["id"], raza="Elfo", clase="Mago")
        assert updated["raza"] == "Elfo"
        assert updated["clase"] == "Mago"


class TestActualizarEstadisticas:
    def test_actualizar_fuerza(self, db_conn, personaje):
        updated = actualizar_estadisticas(personaje["id"], fuerza=18)
        assert updated["fuerza"] == 18

    def test_actualizar_multiples_stats(self, db_conn, personaje):
        updated = actualizar_estadisticas(personaje["id"], destreza=20, carisma=15)
        assert updated["destreza"] == 20
        assert updated["carisma"] == 15

    def test_stat_por_encima_de_30_lanza_excepcion(self, db_conn, personaje):
        with pytest.raises(Exception):
            actualizar_estadisticas(personaje["id"], fuerza=31)

    def test_stat_en_cero_lanza_excepcion(self, db_conn, personaje):
        with pytest.raises(Exception):
            actualizar_estadisticas(personaje["id"], fuerza=0)

    def test_limites_validos(self, db_conn, personaje):
        updated = actualizar_estadisticas(personaje["id"], fuerza=1, destreza=30)
        assert updated["fuerza"] == 1
        assert updated["destreza"] == 30

    def test_actualizar_vida(self, db_conn, personaje):
        updated = actualizar_estadisticas(personaje["id"], vida_max=50, vida_actual=30)
        assert updated["vida_max"] == 50
        assert updated["vida_actual"] == 30

    def test_vida_actual_cero_es_valida(self, db_conn, personaje):
        updated = actualizar_estadisticas(personaje["id"], vida_actual=0)
        assert updated["vida_actual"] == 0

    def test_vida_actual_negativa_lanza_excepcion(self, db_conn, personaje):
        with pytest.raises(Exception):
            actualizar_estadisticas(personaje["id"], vida_actual=-1)


class TestEliminarPersonaje:
    def test_personaje_eliminado_no_aparece(self, db_conn, campana, usuario):
        p = crear_personaje(campana["id"], usuario["id"], "A Borrar")
        eliminar_personaje(p["id"])
        assert obtener_personaje_completo(p["id"]) is None

    def test_eliminar_personaje_elimina_inventario(self, db_conn, campana, usuario):
        p = crear_personaje(campana["id"], usuario["id"], "Con Items")
        añadir_objeto(p["id"], "Item Efímero")
        eliminar_personaje(p["id"])
        assert obtener_personaje_completo(p["id"]) is None

    def test_eliminar_id_inexistente_no_lanza_excepcion(self, db_conn):
        eliminar_personaje("00000000-0000-0000-0000-000000000000")


class TestEliminarObjeto:
    def test_objeto_eliminado_no_aparece_en_inventario(self, db_conn, personaje):
        obj = añadir_objeto(personaje["id"], "Objeto a Borrar")
        eliminar_objeto(obj["id"])
        completo = obtener_personaje_completo(personaje["id"])
        ids = [o["id"] for o in completo["inventario"]]
        assert obj["id"] not in ids

    def test_personaje_permanece_tras_eliminar_objeto(self, db_conn, personaje):
        obj = añadir_objeto(personaje["id"], "Poción")
        eliminar_objeto(obj["id"])
        assert obtener_personaje_completo(personaje["id"]) is not None

    def test_eliminar_id_inexistente_no_lanza_excepcion(self, db_conn):
        eliminar_objeto("00000000-0000-0000-0000-000000000000")
