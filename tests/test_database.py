import pytest
from services.generador_cartones import generar_cartones
from db.database import (
    init_db,
    guardar_partida,
    listar_partidas,
    cargar_cartones_de_partida,
    obtener_proximo_numero_sorteo,
    crear_sorteo,
    cerrar_sorteo,
    guardar_numero_sorteo,
    guardar_ganadores_sorteo,
    obtener_historial_sorteos,
)


@pytest.fixture(autouse=True)
def db_temporal(tmp_path, monkeypatch):
    monkeypatch.setattr("db.database.DB_PATH", tmp_path / "test.sqlite3")
    init_db()


# --- Partidas ---

def test_guardar_y_listar_partida():
    cartones = generar_cartones(5)
    partida_id = guardar_partida(cartones)
    assert partida_id is not None
    partidas = listar_partidas()
    assert len(partidas) == 1
    assert partidas[0]["id"] == partida_id
    assert partidas[0]["cantidad_cartones"] == 5


def test_guardar_partida_sin_cartones_lanza_error():
    with pytest.raises(ValueError):
        guardar_partida([])


def test_listar_partidas_vacia():
    assert listar_partidas() == []


def test_multiples_partidas_ordenadas_por_id_desc():
    for cantidad in [3, 5, 7]:
        guardar_partida(generar_cartones(cantidad))
    partidas = listar_partidas()
    assert len(partidas) == 3
    assert partidas[0]["cantidad_cartones"] == 7  # la última guardada primero


# --- Cartones ---

def test_cargar_cartones_reproduce_numeros():
    cartones_orig = generar_cartones(10)
    partida_id = guardar_partida(cartones_orig)
    cartones_cargados = cargar_cartones_de_partida(partida_id)

    assert len(cartones_cargados) == 10
    for orig, cargado in zip(cartones_orig, cartones_cargados):
        assert orig.numeros == cargado.numeros


def test_cargar_cartones_partida_inexistente():
    assert cargar_cartones_de_partida(9999) == []


def test_cartones_cargados_sin_duplicados():
    cartones_orig = generar_cartones(20)
    partida_id = guardar_partida(cartones_orig)
    cargados = cargar_cartones_de_partida(partida_id)
    hashes = [c.get_hash() for c in cargados]
    assert len(hashes) == len(set(hashes))


# --- Sorteos ---

def test_proximo_numero_sorteo_inicial_es_1():
    cartones = generar_cartones(3)
    partida_id = guardar_partida(cartones)
    assert obtener_proximo_numero_sorteo(partida_id) == 1


def test_proximo_numero_sorteo_incrementa():
    cartones = generar_cartones(3)
    partida_id = guardar_partida(cartones)
    crear_sorteo(partida_id, 1)
    assert obtener_proximo_numero_sorteo(partida_id) == 2


def test_crear_y_cerrar_sorteo():
    cartones = generar_cartones(3)
    partida_id = guardar_partida(cartones)
    sorteo_id = crear_sorteo(partida_id, 1)
    assert sorteo_id is not None
    cerrar_sorteo(sorteo_id)  # no debe lanzar


def test_guardar_numeros_sorteo():
    cartones = generar_cartones(3)
    partida_id = guardar_partida(cartones)
    sorteo_id = crear_sorteo(partida_id, 1)
    guardar_numero_sorteo(sorteo_id, 42, orden_salida=1)
    guardar_numero_sorteo(sorteo_id, 17, orden_salida=2)
    historial = obtener_historial_sorteos(partida_id)
    assert 42 in historial[0]["numeros"]
    assert 17 in historial[0]["numeros"]


def test_guardar_ganadores_sorteo():
    cartones = generar_cartones(3)
    partida_id = guardar_partida(cartones)
    sorteo_id = crear_sorteo(partida_id, 1)
    guardar_ganadores_sorteo(sorteo_id, [(1, "Línea"), (2, "Cartón lleno")], numero_disparo=50)
    historial = obtener_historial_sorteos(partida_id)
    ganadores = historial[0]["ganadores"]
    assert (1, "Línea") in ganadores
    assert (2, "Cartón lleno") in ganadores


def test_historial_sorteos_vacio():
    cartones = generar_cartones(3)
    partida_id = guardar_partida(cartones)
    assert obtener_historial_sorteos(partida_id) == []


def test_numero_duplicado_en_sorteo_se_ignora():
    cartones = generar_cartones(3)
    partida_id = guardar_partida(cartones)
    sorteo_id = crear_sorteo(partida_id, 1)
    guardar_numero_sorteo(sorteo_id, 42, orden_salida=1)
    guardar_numero_sorteo(sorteo_id, 42, orden_salida=2)  # duplicado, debe ignorarse
    historial = obtener_historial_sorteos(partida_id)
    assert historial[0]["numeros"].count(42) == 1
