import pytest
from models.carton import Carton

# Cartón 1 — válido, estructura real de bingo (3 filas × 9 cols, 15 números)
#      C0   C1   C2   C3   C4   C5   C6   C7   C8
# R0: [ 1,   "",  21,  "",   "",  51,  61,   "",  81]
# R1: [ 3,   "",   "",  31,  41,   "",   "",  71,  83]
# R2: ["",  11,  23,   "",  43,   "",  63,   "",  85]
FILAS_1 = [
    [1,  "",  21, "",  "",  51, 61, "",  81],
    [3,  "",  "",  31, 41, "",  "",  71, 83],
    ["", 11, 23, "",  43, "",  63, "",  85],
]

# Cartón 2 — distinto al 1, sin números en común
#      C0   C1   C2   C3   C4   C5   C6   C7   C8
# R0: [ 2,  14,   "",   "",  44,   "",   "",  74,  84]
# R1: ["",   "",  24,  34,   "",  54,  64,   "",  86]
# R2: [ 4,   "",   "",  36,   "",  56,   "",  76,  88]
FILAS_2 = [
    [2,  14, "",  "",  44, "",  "",  74, 84],
    ["", "",  24, 34, "",  54, 64, "",  86],
    [4,  "",  "",  36, "",  56, "",  76, 88],
]


@pytest.fixture
def carton1():
    return Carton(1, numeros=[list(f) for f in FILAS_1])


@pytest.fixture
def carton2():
    return Carton(2, numeros=[list(f) for f in FILAS_2])
