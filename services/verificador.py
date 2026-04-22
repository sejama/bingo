def es_linea(carton):
    for i in range(3):
        completa = True
        for j in range(9):
            if carton.numeros[i][j] != "" and not carton.marcados[i][j]:
                completa = False
        if completa:
            return True
    return False


def es_bingo(carton):
    for i in range(3):
        for j in range(9):
            if carton.numeros[i][j] != "" and not carton.marcados[i][j]:
                return False
    return True