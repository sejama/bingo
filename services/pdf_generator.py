from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from pathlib import Path

def dibujar_carton(c, carton, x, y, ancho, alto, partida_id=None):
    cell_w = ancho / 9
    cell_h = alto / 3

    # ID del cartón
    id_font_size = 8 if ancho < 180 else 10
    c.setFont("Helvetica-Bold", id_font_size)
    if partida_id is None:
        titulo = f"Cartón #{carton.id}"
    else:
        titulo = f"Cartón #{carton.id} - Partida #{partida_id}"
    c.drawString(x, y + alto + 4, titulo)

    # dibujar grilla
    for fila in range(3):
        for col in range(9):
            px = x + col * cell_w
            py = y + (2 - fila) * cell_h

            c.rect(px, py, cell_w, cell_h)

            valor = carton.numeros[fila][col]
            if valor != "":
                numero_font_size = max(6, min(10, int(cell_h * 0.45)))
                c.setFont("Helvetica", numero_font_size)
                c.drawCentredString(
                    px + cell_w / 2,
                    py + cell_h / 2 - (numero_font_size * 0.35),
                    str(valor)
                )


def _calcular_layout_a4(width, height):
    margen_x = 20
    margen_y = 20
    gap_x = 10
    gap_y = 16

    # Mantener cartones legibles pero lo más compactos posible.
    min_carton_w = 95
    min_carton_h = 62

    ancho_util = width - (2 * margen_x)
    alto_util = height - (2 * margen_y)

    mejor = None

    for cols in range(2, 8):
        carton_w = (ancho_util - (cols - 1) * gap_x) / cols
        if carton_w < min_carton_w:
            continue

        for rows in range(2, 12):
            carton_h = (alto_util - (rows - 1) * gap_y) / rows
            if carton_h < min_carton_h:
                continue

            capacidad = cols * rows
            candidato = (capacidad, rows, cols, carton_w, carton_h, margen_x, margen_y, gap_x, gap_y)

            if mejor is None or candidato[0] > mejor[0]:
                mejor = candidato

    if mejor is None:
        # Fallback conservador si algo sale fuera de rango.
        cols, rows = 2, 4
        carton_w = (ancho_util - (cols - 1) * gap_x) / cols
        carton_h = (alto_util - (rows - 1) * gap_y) / rows
        return rows, cols, carton_w, carton_h, margen_x, margen_y, gap_x, gap_y

    _, rows, cols, carton_w, carton_h, margen_x, margen_y, gap_x, gap_y = mejor
    return rows, cols, carton_w, carton_h, margen_x, margen_y, gap_x, gap_y


def exportar_cartones_pdf(cartones, archivo=None, partida_id=None):
    if archivo is None:
        if partida_id is None:
            archivo = "./exports/cartones.pdf"
        else:
            archivo = f"./exports/cartones_partida_{partida_id}.pdf"

    Path(archivo).parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(archivo, pagesize=A4)

    width, height = A4

    rows, cols, carton_w, carton_h, margen_x, margen_y, gap_x, gap_y = _calcular_layout_a4(width, height)
    cartones_por_pagina = rows * cols

    contador = 0

    for carton in cartones:
        indice_en_pagina = contador % cartones_por_pagina
        row = indice_en_pagina // cols
        col = indice_en_pagina % cols

        x = margen_x + col * (carton_w + gap_x)
        y_top = height - margen_y - row * (carton_h + gap_y)
        y = y_top - carton_h

        dibujar_carton(c, carton, x, y, carton_w, carton_h, partida_id=partida_id)

        contador += 1

        if contador % cartones_por_pagina == 0:
            c.showPage()

    c.save()
    return archivo