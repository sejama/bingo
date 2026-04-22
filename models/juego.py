from collections import defaultdict
from services.verificador import es_linea, es_bingo

class Juego:
    def __init__(self, cartones, proximo_numero_sorteo=1, auto_iniciar=False):
        self.cartones = cartones
        self.numeros_sorteados = []
        self.premios_reportados = defaultdict(set)
        self.sorteos = []
        self.sorteo_actual = None
        self.proximo_numero_sorteo = proximo_numero_sorteo

        # índice: numero -> lista de (carton, fila, col)
        self.indice = defaultdict(list)

        self._construir_indice()
        if auto_iniciar:
            self.iniciar_nuevo_sorteo()
    
    def _construir_indice(self):
        for carton in self.cartones:
            for i in range(3):
                for j in range(9):
                    valor = carton.numeros[i][j]
                    if valor != "":
                        self.indice[valor].append((carton, i, j))

    def _limpiar_marcados(self):
        for carton in self.cartones:
            carton.marcados = [[False] * 9 for _ in range(3)]

    def iniciar_nuevo_sorteo(self):
        if self.sorteo_actual is not None:
            hubo_numeros = len(self.sorteo_actual["numeros"]) > 0
            hubo_ganadores = len(self.sorteo_actual["ganadores"]) > 0
            if hubo_numeros and not hubo_ganadores:
                raise ValueError("No se puede iniciar un nuevo sorteo: el sorteo actual todavía no tiene ganadores")

        self._limpiar_marcados()
        self.premios_reportados.clear()

        sorteo = {
            "numero": self.proximo_numero_sorteo,
            "numeros": [],
            "ganadores": set(),
        }
        self.sorteos.append(sorteo)
        self.sorteo_actual = sorteo
        self.numeros_sorteados = self.sorteo_actual["numeros"]
        self.proximo_numero_sorteo += 1

    def puede_cerrar_lote(self):
        if self.sorteo_actual is None:
            return True

        hubo_numeros = len(self.sorteo_actual["numeros"]) > 0
        hubo_ganadores = len(self.sorteo_actual["ganadores"]) > 0
        return (not hubo_numeros) or hubo_ganadores

    def registrar_numero(self, numero):
        if self.sorteo_actual is None:
            raise ValueError("Primero debés iniciar un sorteo")

        if not isinstance(numero, int):
            raise ValueError("El número debe ser un entero")

        if numero < 1 or numero > 90:
            raise ValueError("El número debe estar entre 1 y 90")

        if numero in self.numeros_sorteados:
            raise ValueError("Ese número ya fue ingresado")

        self.numeros_sorteados.append(numero)

        for carton, fila, col in self.indice.get(numero, []):
            carton.marcados[fila][col] = True

        ganadores = []

        for carton in self.cartones:
            premios = self.premios_reportados[carton.id]

            if es_linea(carton) and "linea" not in premios:
                premios.add("linea")
                ganadores.append((carton.id, "Línea"))

            if es_bingo(carton) and "bingo" not in premios:
                premios.add("bingo")
                ganadores.append((carton.id, "Cartón lleno"))

        for ganador in ganadores:
            self.sorteo_actual["ganadores"].add(ganador)

        return ganadores

    def reiniciar(self):
        self.iniciar_nuevo_sorteo()