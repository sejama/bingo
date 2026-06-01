from services.verificador import es_bingo, es_linea


# --- es_linea ---

def test_linea_falso_sin_marcados(carton1):
    assert es_linea(carton1) is False


def test_linea_verdadero_al_completar_fila_0(carton1):
    # Fila 0: 1, 21, 51, 61, 81
    for n in [1, 21, 51, 61, 81]:
        carton1.marcar_numero(n)
    assert es_linea(carton1) is True


def test_linea_verdadero_al_completar_fila_1(carton1):
    # Fila 1: 3, 31, 41, 71, 83
    for n in [3, 31, 41, 71, 83]:
        carton1.marcar_numero(n)
    assert es_linea(carton1) is True


def test_linea_verdadero_al_completar_fila_2(carton1):
    # Fila 2: 11, 23, 43, 63, 85
    for n in [11, 23, 43, 63, 85]:
        carton1.marcar_numero(n)
    assert es_linea(carton1) is True


def test_linea_falso_con_fila_incompleta(carton1):
    for n in [1, 21, 51, 61]:  # falta 81
        carton1.marcar_numero(n)
    assert es_linea(carton1) is False


# --- es_bingo ---

def test_bingo_falso_sin_marcados(carton1):
    assert es_bingo(carton1) is False


def test_bingo_falso_con_solo_una_linea(carton1):
    for n in [1, 21, 51, 61, 81]:
        carton1.marcar_numero(n)
    assert es_bingo(carton1) is False


def test_bingo_verdadero_con_todos_marcados(carton1):
    todos = [1, 3, 11, 21, 23, 31, 41, 43, 51, 61, 63, 71, 81, 83, 85]
    for n in todos:
        carton1.marcar_numero(n)
    assert es_bingo(carton1) is True


def test_bingo_falso_falta_un_numero(carton1):
    todos = [1, 3, 11, 21, 23, 31, 41, 43, 51, 61, 63, 71, 81, 83]  # falta 85
    for n in todos:
        carton1.marcar_numero(n)
    assert es_bingo(carton1) is False
