import random
from itertools import combinations

class Carton:
    def __init__(self, id, numeros=None):
        self.id = id
        self.numeros = numeros if numeros is not None else self.generar_carton()
        self.marcados = [[False]*9 for _ in range(3)]

    def generar_carton(self):
        carton = [["" for _ in range(9)] for _ in range(3)]

        # 15 números por cartón: 1 por columna (9) + 6 extras.
        cantidades_por_columna = [1] * 9
        extras = 6
        while extras > 0:
            col = random.randint(0, 8)
            if cantidades_por_columna[col] < 3:
                cantidades_por_columna[col] += 1
                extras -= 1

        filas_por_columna = self._asignar_filas(cantidades_por_columna)

        for col, filas in enumerate(filas_por_columna):
            inicio = col * 10 + 1
            fin = inicio + 9
            numeros = sorted(random.sample(range(inicio, fin + 1), len(filas)))

            for fila, numero in zip(sorted(filas), numeros):
                carton[fila][col] = numero

        return carton

    def _asignar_filas(self, cantidades_por_columna):
        opciones = {
            1: list(combinations([0, 1, 2], 1)),
            2: list(combinations([0, 1, 2], 2)),
            3: [tuple([0, 1, 2])],
        }

        columnas = sorted(range(9), key=lambda c: cantidades_por_columna[c], reverse=True)
        restantes_fila = [5, 5, 5]
        asignacion = [None] * 9

        def backtrack(idx):
            if idx == len(columnas):
                return restantes_fila == [0, 0, 0]

            col = columnas[idx]
            cantidad = cantidades_por_columna[col]

            for filas in opciones[cantidad]:
                if any(restantes_fila[f] == 0 for f in filas):
                    continue

                for f in filas:
                    restantes_fila[f] -= 1

                columnas_restantes = len(columnas) - idx - 1
                if all(0 <= restantes_fila[f] <= columnas_restantes for f in range(3)):
                    asignacion[col] = filas
                    if backtrack(idx + 1):
                        return True
                    asignacion[col] = None

                for f in filas:
                    restantes_fila[f] += 1

            return False

        if not backtrack(0):
            raise Exception("No se pudo construir una distribución válida para el cartón")

        return asignacion

    def marcar_numero(self, numero):
        for i in range(3):
            for j in range(9):
                if self.numeros[i][j] == numero:
                    self.marcados[i][j] = True

    def get_hash(self):
        numeros = []

        for fila in self.numeros:
            for val in fila:
                if val != "":
                    numeros.append(val)

        # ordenamos para que el orden visual no afecte
        return tuple(sorted(numeros))