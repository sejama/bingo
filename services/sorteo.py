import random

class Sorteo:
    def __init__(self):
        self.numeros_disponibles = list(range(1, 91))
        self.numeros_salidos = []

    def sacar_numero(self):
        if not self.numeros_disponibles:
            return None

        numero = random.choice(self.numeros_disponibles)
        self.numeros_disponibles.remove(numero)
        self.numeros_salidos.append(numero)

        return numero