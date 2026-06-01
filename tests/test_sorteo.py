from services.sorteo import Sorteo


def test_saca_numeros_en_rango_1_90():
    s = Sorteo()
    for _ in range(90):
        n = s.sacar_numero()
        assert 1 <= n <= 90


def test_no_repite_numeros():
    s = Sorteo()
    salidos = [s.sacar_numero() for _ in range(90)]
    assert len(salidos) == len(set(salidos))


def test_saca_exactamente_90_numeros():
    s = Sorteo()
    salidos = [s.sacar_numero() for _ in range(90)]
    assert sorted(salidos) == list(range(1, 91))


def test_retorna_none_cuando_se_agotan():
    s = Sorteo()
    for _ in range(90):
        s.sacar_numero()
    assert s.sacar_numero() is None


def test_disponibles_decrece_con_cada_extraccion():
    s = Sorteo()
    for i in range(1, 91):
        assert len(s.numeros_disponibles) == 91 - i
        s.sacar_numero()
