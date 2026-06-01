import pytest
from models.carton import Carton


def _numeros_planos(carton):
    return [v for fila in carton.numeros for v in fila if v != ""]


def test_carton_tiene_15_numeros():
    c = Carton(1)
    assert len(_numeros_planos(c)) == 15


def test_carton_tiene_3_filas_9_columnas():
    c = Carton(1)
    assert len(c.numeros) == 3
    assert all(len(fila) == 9 for fila in c.numeros)


def test_cada_fila_tiene_5_numeros():
    for _ in range(20):
        c = Carton(1)
        for fila in c.numeros:
            nums = [v for v in fila if v != ""]
            assert len(nums) == 5, f"Fila {fila} tiene {len(nums)} números, se esperaban 5"


def test_cada_columna_tiene_entre_1_y_3_numeros():
    for _ in range(20):
        c = Carton(1)
        for col in range(9):
            nums = [c.numeros[fila][col] for fila in range(3) if c.numeros[fila][col] != ""]
            assert 1 <= len(nums) <= 3, f"Columna {col} tiene {len(nums)} números"


def test_numeros_en_decena_correcta():
    for _ in range(20):
        c = Carton(1)
        for col in range(9):
            inicio = col * 10 + 1
            fin = inicio + 9
            for fila in range(3):
                v = c.numeros[fila][col]
                if v != "":
                    assert inicio <= v <= fin, (
                        f"Col {col}: valor {v} fuera del rango {inicio}-{fin}"
                    )


def test_sin_numeros_duplicados_dentro_del_carton():
    for _ in range(20):
        c = Carton(1)
        nums = _numeros_planos(c)
        assert len(nums) == len(set(nums)), "El cartón tiene números duplicados"


def test_todos_los_numeros_entre_1_y_90():
    for _ in range(20):
        c = Carton(1)
        for n in _numeros_planos(c):
            assert 1 <= n <= 90


def test_marcados_inicialmente_en_falso():
    c = Carton(1)
    assert all(not c.marcados[i][j] for i in range(3) for j in range(9))


def test_marcar_numero_existente(carton1):
    carton1.marcar_numero(1)
    assert carton1.marcados[0][0] is True


def test_marcar_numero_inexistente_no_marca_nada(carton1):
    carton1.marcar_numero(99)
    assert all(not carton1.marcados[i][j] for i in range(3) for j in range(9))


def test_get_hash_es_reproducible(carton1):
    assert carton1.get_hash() == carton1.get_hash()


def test_get_hash_diferente_para_distintos_cartones(carton1, carton2):
    assert carton1.get_hash() != carton2.get_hash()


def test_get_hash_no_depende_del_id():
    from tests.conftest import FILAS_1
    c_a = Carton(1, numeros=[list(f) for f in FILAS_1])
    c_b = Carton(99, numeros=[list(f) for f in FILAS_1])
    assert c_a.get_hash() == c_b.get_hash()
