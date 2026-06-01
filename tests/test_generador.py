import pytest
from services.generador_cartones import (
    generar_cartones,
    validar_cantidad_cartones,
    MAX_CARTONES_SIN_REPETICION,
)


def test_genera_la_cantidad_pedida():
    for cantidad in [1, 10, 50, 100]:
        cartones = generar_cartones(cantidad)
        assert len(cartones) == cantidad


def test_ids_son_consecutivos_desde_1():
    cartones = generar_cartones(10)
    assert [c.id for c in cartones] == list(range(1, 11))


def test_sin_cartones_repetidos_lote_chico():
    cartones = generar_cartones(50)
    hashes = [c.get_hash() for c in cartones]
    assert len(hashes) == len(set(hashes)), "Hay cartones duplicados en el lote"


def test_sin_cartones_repetidos_lote_mediano():
    cartones = generar_cartones(500)
    hashes = [c.get_hash() for c in cartones]
    assert len(hashes) == len(set(hashes)), "Hay cartones duplicados en el lote"


def test_sin_cartones_repetidos_lote_grande():
    cartones = generar_cartones(2000)
    hashes = [c.get_hash() for c in cartones]
    assert len(hashes) == len(set(hashes)), "Hay cartones duplicados en el lote"


def test_sin_cartones_repetidos_15000():
    cartones = generar_cartones(15000)
    hashes = [c.get_hash() for c in cartones]
    assert len(hashes) == len(set(hashes)), "Hay cartones duplicados en el lote de 15000"
    assert len(cartones) == 15000


def test_cada_carton_tiene_15_numeros():
    cartones = generar_cartones(20)
    for c in cartones:
        nums = [v for fila in c.numeros for v in fila if v != ""]
        assert len(nums) == 15


def test_validar_cantidad_cero():
    with pytest.raises(ValueError):
        validar_cantidad_cartones(0)


def test_validar_cantidad_negativa():
    with pytest.raises(ValueError):
        validar_cantidad_cartones(-5)


def test_validar_cantidad_excede_maximo():
    with pytest.raises(ValueError):
        validar_cantidad_cartones(MAX_CARTONES_SIN_REPETICION + 1)


def test_validar_cantidad_valida_no_lanza():
    validar_cantidad_cartones(1)
    validar_cantidad_cartones(100)
    validar_cantidad_cartones(MAX_CARTONES_SIN_REPETICION)
