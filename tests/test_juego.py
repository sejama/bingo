import pytest
from models.juego import Juego
from tests.conftest import FILAS_1, FILAS_2
from models.carton import Carton


def _juego_con_dos_cartones():
    c1 = Carton(1, numeros=[list(f) for f in FILAS_1])
    c2 = Carton(2, numeros=[list(f) for f in FILAS_2])
    j = Juego([c1, c2], proximo_numero_sorteo=1)
    j.iniciar_nuevo_sorteo()
    return j, c1, c2


# --- Validaciones básicas ---

def test_registrar_sin_sorteo_iniciado(carton1):
    j = Juego([carton1])
    with pytest.raises(ValueError, match="iniciar un sorteo"):
        j.registrar_numero(5)


def test_registrar_numero_fuera_de_rango_menor(carton1):
    j = Juego([carton1], auto_iniciar=True)
    with pytest.raises(ValueError):
        j.registrar_numero(0)


def test_registrar_numero_fuera_de_rango_mayor(carton1):
    j = Juego([carton1], auto_iniciar=True)
    with pytest.raises(ValueError):
        j.registrar_numero(91)


def test_registrar_numero_duplicado(carton1):
    j = Juego([carton1], auto_iniciar=True)
    j.registrar_numero(1)
    with pytest.raises(ValueError, match="ya fue ingresado"):
        j.registrar_numero(1)


def test_registrar_numero_no_entero(carton1):
    j = Juego([carton1], auto_iniciar=True)
    with pytest.raises(ValueError):
        j.registrar_numero("5")


# --- Detección de ganadores ---

def test_sin_ganadores_al_inicio():
    j, _, _ = _juego_con_dos_cartones()
    resultado = j.registrar_numero(90)  # número que no está en ningún cartón
    assert resultado == []


def test_detecta_linea_en_carton_correcto():
    j, c1, c2 = _juego_con_dos_cartones()
    # Fila 0 del cartón 1: 1, 21, 51, 61, 81
    for n in [1, 21, 51, 61, 81]:
        ganadores = j.registrar_numero(n)
    assert any(g[0] == c1.id and g[1] == "Línea" for g in ganadores)
    assert not any(g[0] == c2.id for g in ganadores)


def test_detecta_bingo_en_carton_correcto():
    j, c1, _ = _juego_con_dos_cartones()
    todos_c1 = [1, 3, 11, 21, 23, 31, 41, 43, 51, 61, 63, 71, 81, 83, 85]
    ganadores_acumulados = []
    for n in todos_c1:
        ganadores_acumulados.extend(j.registrar_numero(n))
    assert any(g[0] == c1.id and g[1] == "Cartón lleno" for g in ganadores_acumulados)


def test_linea_y_bingo_no_se_reporten_dos_veces():
    j, c1, _ = _juego_con_dos_cartones()
    todos_c1 = [1, 3, 11, 21, 23, 31, 41, 43, 51, 61, 63, 71, 81, 83, 85]
    lineas = 0
    bingos = 0
    for n in todos_c1:
        for gid, premio in j.registrar_numero(n):
            if gid == c1.id and premio == "Línea":
                lineas += 1
            if gid == c1.id and premio == "Cartón lleno":
                bingos += 1
    assert lineas == 1
    assert bingos == 1


# --- Flujo de sorteos ---

def test_nuevo_sorteo_sin_numeros_previos(carton1):
    j = Juego([carton1], auto_iniciar=True)
    # No hubo números → se puede iniciar otro
    j.reiniciar()
    assert j.sorteo_actual["numero"] == 2


def test_nuevo_sorteo_con_ganadores_previos():
    j, _, _ = _juego_con_dos_cartones()
    for n in [1, 21, 51, 61, 81]:
        j.registrar_numero(n)
    # Hubo números y ganadores → se puede reiniciar
    j.reiniciar()
    assert j.sorteo_actual["numero"] == 2


def test_nuevo_sorteo_sin_ganadores_lanza_error():
    j, _, _ = _juego_con_dos_cartones()
    j.registrar_numero(90)  # número sin ganador
    with pytest.raises(ValueError):
        j.reiniciar()


def test_reiniciar_limpia_marcados(carton1):
    j = Juego([carton1], auto_iniciar=True)
    # Completar fila 0 para tener ganador y poder reiniciar
    for n in [1, 21, 51, 61, 81]:
        j.registrar_numero(n)
    assert carton1.marcados[0][0] is True
    j.reiniciar()
    assert all(not carton1.marcados[i][k] for i in range(3) for k in range(9))


def test_reiniciar_limpia_numeros_sorteados(carton1):
    j = Juego([carton1], auto_iniciar=True)
    for n in [1, 21, 51, 61, 81]:
        j.registrar_numero(n)
    j.reiniciar()
    assert j.numeros_sorteados == []


# --- puede_cerrar_lote ---

def test_puede_cerrar_sin_sorteo(carton1):
    j = Juego([carton1])
    assert j.puede_cerrar_lote() is True


def test_puede_cerrar_sorteo_sin_numeros(carton1):
    j = Juego([carton1], auto_iniciar=True)
    assert j.puede_cerrar_lote() is True


def test_no_puede_cerrar_con_numeros_sin_ganadores(carton1):
    j = Juego([carton1], auto_iniciar=True)
    j.registrar_numero(90)
    assert j.puede_cerrar_lote() is False


def test_puede_cerrar_con_numeros_y_ganadores():
    j, _, _ = _juego_con_dos_cartones()
    for n in [1, 21, 51, 61, 81]:
        j.registrar_numero(n)
    assert j.puede_cerrar_lote() is True
