from models.carton import Carton

# Máximo teórico bajo las reglas actuales:
# - 15 números por cartón
# - cada columna (decena) con 1 a 3 números
# - unicidad por los 15 números ordenados
MAX_CARTONES_SIN_REPETICION = 6147236812500000


def validar_cantidad_cartones(cantidad):
    if cantidad <= 0:
        raise ValueError("La cantidad de cartones debe ser mayor que cero")

    if cantidad > MAX_CARTONES_SIN_REPETICION:
        raise ValueError(
            "La cantidad excede el máximo teórico sin repetición "
            f"({MAX_CARTONES_SIN_REPETICION:,})."
        )

def generar_cartones(cantidad):
    validar_cantidad_cartones(cantidad)

    cartones = []
    hashes = set()

    intentos = 0
    max_intentos = cantidad * 10  # seguridad

    while len(cartones) < cantidad and intentos < max_intentos:
        c = Carton(len(cartones) + 1)
        h = c.get_hash()

        if h not in hashes:
            hashes.add(h)
            cartones.append(c)

        intentos += 1

    if len(cartones) < cantidad:
        raise Exception("No se pudieron generar suficientes cartones únicos")

    return cartones