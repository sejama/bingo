import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog

from services.generador_cartones import (
    generar_cartones,
    validar_cantidad_cartones,
    MAX_CARTONES_SIN_REPETICION,
)
from services.pdf_generator import exportar_cartones_pdf
from models.juego import Juego
from db.database import (
    init_db,
    guardar_partida,
    listar_partidas,
    cargar_cartones_de_partida,
    obtener_proximo_numero_sorteo,
    crear_sorteo,
    cerrar_sorteo,
    guardar_ganadores_sorteo,
    guardar_numero_sorteo,
    obtener_historial_sorteos,
)

class BingoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bingo Escolar")
        self.root.geometry("960x720")
        self.root.minsize(900, 680)

        self.juego = None
        self.partida_id = None
        self.cartones_generados = []
        self.partida_cargada_para_sorteo = False
        self.sorteo_db_id = None

        init_db()

        titulo = tk.Label(root, text="Control de Bingo", font=("Arial", 20, "bold"))
        titulo.pack(pady=(10, 6))

        contenedor = tk.Frame(root)
        contenedor.pack(pady=6)

        tk.Label(contenedor, text="Cantidad de cartones:").grid(row=0, column=0, sticky="e", padx=6, pady=6)
        self.cantidad_var = tk.StringVar(value="50")
        self.entry_cantidad = tk.Entry(contenedor, width=10, textvariable=self.cantidad_var)
        self.entry_cantidad.grid(row=0, column=1, padx=6, pady=6)
        self.entry_cantidad.bind("<KeyRelease>", self.on_cantidad_change)
        self.entry_cantidad.bind("<FocusOut>", self.on_cantidad_focus_out)

        texto_maximo = f"Máximo sin repetición: {MAX_CARTONES_SIN_REPETICION:,}"
        tk.Label(contenedor, text=texto_maximo).grid(row=0, column=2, sticky="w", padx=6, pady=6)
        self.label_validacion_cantidad = tk.Label(contenedor, text="", fg="green")
        self.label_validacion_cantidad.grid(row=1, column=2, sticky="w", padx=6, pady=6)

        tk.Label(contenedor, text="Número del bolillero:").grid(row=1, column=0, sticky="e", padx=6, pady=6)
        self.entry_numero = tk.Entry(contenedor, width=10)
        self.entry_numero.grid(row=1, column=1, padx=6, pady=6)

        self.label = tk.Label(root, text="Número ingresado: -", font=("Arial", 18))
        self.label.pack(pady=8)

        self.label_estado = tk.Label(root, text="Cartones generados: 0 | Números cargados: 0")
        self.label_estado.pack(pady=(0, 6))

        self.label_etapa = tk.Label(root, text="Etapa: 1) Generar cartones", fg="blue")
        self.label_etapa.pack(pady=(0, 6))

        frame_numeros = tk.LabelFrame(root, text="Números salidos del sorteo (hasta 90)", padx=8, pady=6)
        frame_numeros.pack(fill="x", padx=12, pady=(0, 8))

        self.listbox_numeros = tk.Listbox(frame_numeros, height=4)
        self.listbox_numeros.grid(row=0, column=0, sticky="nsew")

        scroll_numeros = tk.Scrollbar(frame_numeros, orient="vertical", command=self.listbox_numeros.yview)
        scroll_numeros.grid(row=0, column=1, sticky="ns")
        self.listbox_numeros.config(yscrollcommand=scroll_numeros.set)

        frame_numeros.columnconfigure(0, weight=1)
        frame_numeros.rowconfigure(0, weight=1)

        frame_historial = tk.LabelFrame(root, text="Historial de sorteos (números y ganadores)", padx=8, pady=6)
        frame_historial.pack(fill="both", expand=False, padx=12, pady=(0, 8))

        self.text_historial = tk.Text(frame_historial, height=3, width=90, state="disabled")
        self.text_historial.grid(row=0, column=0, sticky="nsew")

        scroll_historial = tk.Scrollbar(frame_historial, orient="vertical", command=self.text_historial.yview)
        scroll_historial.grid(row=0, column=1, sticky="ns")
        self.text_historial.config(yscrollcommand=scroll_historial.set)

        frame_historial.columnconfigure(0, weight=1)
        frame_historial.rowconfigure(0, weight=1)

        botones = tk.Frame(root)
        botones.pack(pady=4)

        self.btn_generar = tk.Button(botones, text="Generar cartones", command=self.generar)
        self.btn_generar.grid(row=0, column=0, padx=6)

        self.btn_registrar = tk.Button(botones, text="Registrar número", command=self.registrar_numero)
        self.btn_registrar.grid(row=0, column=1, padx=6)

        self.btn_reiniciar = tk.Button(botones, text="Reiniciar partida", command=self.reiniciar)
        self.btn_reiniciar.grid(row=0, column=2, padx=6)

        self.btn_pdf = tk.Button(botones, text="Exportar PDF", command=self.exportar_pdf)
        self.btn_pdf.grid(row=0, column=3, padx=6)

        frame_partidas = tk.LabelFrame(root, text="Partidas guardadas", padx=8, pady=6)
        frame_partidas.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.listbox_partidas = tk.Listbox(frame_partidas, height=5)
        self.listbox_partidas.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=(0, 8), pady=(0, 8))

        scroll_partidas = tk.Scrollbar(frame_partidas, orient="vertical", command=self.listbox_partidas.yview)
        scroll_partidas.grid(row=0, column=2, sticky="ns", pady=(0, 8))
        self.listbox_partidas.config(yscrollcommand=scroll_partidas.set)

        frame_partidas.columnconfigure(0, weight=1)
        frame_partidas.rowconfigure(0, weight=1)

        self.btn_refrescar = tk.Button(frame_partidas, text="Refrescar partidas", command=self.cargar_lista_partidas)
        self.btn_refrescar.grid(row=1, column=0, sticky="w")

        self.btn_cargar_partida = tk.Button(frame_partidas, text="Cargar partida seleccionada", command=self.cargar_partida)
        self.btn_cargar_partida.grid(row=1, column=1, sticky="e")

        self.btn_cerrar_lote = tk.Button(frame_partidas, text="Cerrar lote cargado", command=self.cerrar_lote_cargado)
        self.btn_cerrar_lote.grid(row=2, column=1, sticky="e", pady=(6, 0))

        self._partidas_cache = []
        self.validar_cantidad_ui()
        self.cargar_lista_partidas()
        self.actualizar_estado_flujo()
        self.actualizar_historial_sorteos_ui()

    def actualizar_historial_sorteos_ui(self):
        self.text_historial.config(state="normal")
        self.text_historial.delete("1.0", tk.END)

        if not self.partida_id:
            self.text_historial.insert(tk.END, "Sin partida seleccionada")
            self.text_historial.config(state="disabled")
            return

        historial = obtener_historial_sorteos(self.partida_id)
        if not historial:
            self.text_historial.insert(tk.END, f"Partida #{self.partida_id}: sin sorteos registrados")
            self.text_historial.config(state="disabled")
            return

        for sorteo in historial:
            numeros = ", ".join(str(n) for n in sorteo["numeros"]) if sorteo["numeros"] else "Sin números"
            if sorteo["ganadores"]:
                ganadores = "; ".join([f"Cartón {c} ({p})" for c, p in sorteo["ganadores"]])
            else:
                ganadores = "Sin ganadores"

            linea = (
                f"Sorteo #{sorteo['numero_sorteo']} | "
                f"Números: {numeros} | "
                f"Ganadores: {ganadores}\n"
            )
            self.text_historial.insert(tk.END, linea)

        self.text_historial.config(state="disabled")

    def limpiar_historial_sorteos_ui(self):
        self.text_historial.config(state="normal")
        self.text_historial.delete("1.0", tk.END)
        self.text_historial.insert(tk.END, "Sin partida seleccionada")
        self.text_historial.config(state="disabled")

    def actualizar_estado_flujo(self):
        hay_cartones = bool(self.cartones_generados)
        en_sorteo = self.partida_cargada_para_sorteo and self.juego is not None
        sorteo_iniciado = en_sorteo and self.juego.sorteo_actual is not None
        numero_sorteo = self.juego.sorteo_actual["numero"] if sorteo_iniciado else None

        if en_sorteo:
            if sorteo_iniciado:
                self.label_etapa.config(
                    text=(
                        f"Etapa: 3) Sorteo manual activo | Partida #{self.partida_id} "
                        f"| Sorteo #{numero_sorteo}"
                    ),
                    fg="blue",
                )
            else:
                self.label_etapa.config(
                    text=f"Etapa: 3) Partida #{self.partida_id} cargada | Iniciá un nuevo sorteo",
                    fg="blue",
                )
        elif hay_cartones:
            self.label_etapa.config(
                text=(
                    f"Etapa: 2) PDF listo | Partida guardada #{self.partida_id}. "
                    "Para sorteo, cargá una partida"
                ),
                fg="blue",
            )
        else:
            self.label_etapa.config(text="Etapa: 1) Generar cartones", fg="blue")

        self.btn_pdf.config(state="normal" if hay_cartones else "disabled")
        self.btn_registrar.config(state="normal" if sorteo_iniciado else "disabled")
        self.btn_reiniciar.config(state="normal" if en_sorteo else "disabled")
        self.btn_cargar_partida.config(state="disabled" if en_sorteo else "normal")
        self.btn_cerrar_lote.config(state="normal" if en_sorteo else "disabled")
        if en_sorteo:
            self.btn_generar.config(state="disabled")

        if en_sorteo and not sorteo_iniciado:
            self.btn_reiniciar.config(text="Iniciar sorteo")
        elif en_sorteo:
            self.btn_reiniciar.config(text="Nuevo sorteo")
        else:
            self.btn_reiniciar.config(text="Reiniciar partida")

    def on_cantidad_change(self, _event):
        self.validar_cantidad_ui()

    def on_cantidad_focus_out(self, _event):
        self.validar_cantidad_ui(mostrar_error=True)

    def validar_cantidad_ui(self, mostrar_error=False):
        if self.partida_cargada_para_sorteo and self.juego is not None:
            self.btn_generar.config(state="disabled")
            self.label_validacion_cantidad.config(
                text="Hay una partida cargada: no se puede generar otro lote",
                fg="red",
            )
            return False

        texto = self.cantidad_var.get().strip()

        if not texto:
            self.btn_generar.config(state="disabled")
            self.label_validacion_cantidad.config(text="Ingresá una cantidad", fg="red")
            return False

        try:
            cantidad = int(texto)
            validar_cantidad_cartones(cantidad)
        except ValueError as error:
            self.btn_generar.config(state="disabled")
            self.label_validacion_cantidad.config(text=str(error), fg="red")
            if mostrar_error:
                messagebox.showerror("Error", str(error))
            return False

        self.btn_generar.config(state="normal")
        self.label_validacion_cantidad.config(text="Cantidad válida", fg="green")
        return True

    def actualizar_lista_numeros(self):
        self.listbox_numeros.delete(0, tk.END)
        if self.partida_cargada_para_sorteo and self.juego and self.juego.sorteo_actual and self.juego.numeros_sorteados:
            for orden, numero in enumerate(self.juego.numeros_sorteados, start=1):
                self.listbox_numeros.insert(tk.END, f"{orden:02d}) {numero}")
        else:
            self.listbox_numeros.insert(tk.END, "Sin números cargados")

    def generar(self):
        try:
            if self.partida_cargada_para_sorteo and self.juego is not None:
                messagebox.showwarning(
                    "Error",
                    "Hay una partida cargada. Para generar cartones, cerrá el lote actual con el botón 'Cerrar lote cargado'.",
                )
                return

            if not self.validar_cantidad_ui(mostrar_error=True):
                return

            cantidad = int(self.entry_cantidad.get())
            validar_cantidad_cartones(cantidad)
            cartones = generar_cartones(cantidad)
            self.partida_id = guardar_partida(cartones)
            self.cartones_generados = cartones
            self.juego = None
            self.partida_cargada_para_sorteo = False
            self.label.config(text="Número ingresado: -")
            self.label_estado.config(text=f"Cartones generados: {len(cartones)} | Números cargados: 0")
            self.actualizar_lista_numeros()
            self.cargar_lista_partidas()
            self.actualizar_estado_flujo()
            self.actualizar_historial_sorteos_ui()
            messagebox.showinfo("OK", f"Se generaron {cantidad} cartones\nPartida guardada con ID {self.partida_id}")
        except ValueError as error:
            messagebox.showerror("Error", str(error))
        except Exception as error:
            messagebox.showerror("Error", str(error))

    def registrar_numero(self):
        if not self.partida_cargada_para_sorteo or not self.juego:
            messagebox.showwarning("Error", "Para sorteo manual, primero cargá una partida")
            return

        try:
            numero = int(self.entry_numero.get())
            ganadores = self.juego.registrar_numero(numero)

            if self.sorteo_db_id is None:
                self.sorteo_db_id = crear_sorteo(self.partida_id, self.juego.sorteo_actual["numero"])

            guardar_numero_sorteo(
                self.sorteo_db_id,
                numero,
                orden_salida=len(self.juego.numeros_sorteados),
            )

            if ganadores:
                guardar_ganadores_sorteo(self.sorteo_db_id, ganadores, numero_disparo=numero)
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return

        self.label.config(text=f"Número ingresado: {numero}")
        self.label_estado.config(
            text=f"Cartones generados: {len(self.juego.cartones)} | Números cargados: {len(self.juego.numeros_sorteados)}"
        )
        self.actualizar_lista_numeros()
        self.actualizar_historial_sorteos_ui()

        if ganadores:
            texto = "\n".join([f"Cartón {g[0]} - {g[1]}" for g in ganadores])
            messagebox.showinfo("Ganadores", texto)
        else:
            messagebox.showinfo("OK", "Número registrado sin ganadores nuevos")

    def reiniciar(self):
        if not self.partida_cargada_para_sorteo or not self.juego:
            messagebox.showwarning("Error", "Para reiniciar sorteo, primero cargá una partida")
            return

        try:
            self.juego.reiniciar()
            if self.sorteo_db_id is not None:
                cerrar_sorteo(self.sorteo_db_id)
            self.sorteo_db_id = crear_sorteo(self.partida_id, self.juego.sorteo_actual["numero"])
        except ValueError as error:
            messagebox.showwarning("Regla de sorteo", str(error))
            return

        self.label.config(text="Número ingresado: -")
        self.label_estado.config(
            text=f"Cartones generados: {len(self.juego.cartones)} | Números cargados: 0"
        )
        self.entry_numero.delete(0, tk.END)
        self.actualizar_lista_numeros()
        self.actualizar_estado_flujo()
        self.actualizar_historial_sorteos_ui()
        messagebox.showinfo("OK", f"Sorteo iniciado (Sorteo #{self.juego.sorteo_actual['numero']})")

    def exportar_pdf(self):
        if not self.cartones_generados:
            messagebox.showwarning("Error", "Primero generá cartones")
            return

        nombre_sugerido = (
            f"cartones_partida_{self.partida_id}.pdf"
            if self.partida_id is not None
            else "cartones.pdf"
        )

        ruta_destino = filedialog.asksaveasfilename(
            title="Guardar cartones PDF",
            defaultextension=".pdf",
            initialfile=nombre_sugerido,
            filetypes=[("PDF", "*.pdf")],
        )

        if not ruta_destino:
            return

        archivo = exportar_cartones_pdf(
            self.cartones_generados,
            archivo=ruta_destino,
            partida_id=self.partida_id,
        )
        messagebox.showinfo("OK", f"PDF generado correctamente\nArchivo: {archivo}")

    def cargar_lista_partidas(self):
        self._partidas_cache = listar_partidas()
        self.listbox_partidas.delete(0, tk.END)

        if not self._partidas_cache:
            self.listbox_partidas.insert(tk.END, "No hay partidas guardadas")
            return

        for partida in self._partidas_cache:
            texto = (
                f"ID {partida['id']} | Fecha: {partida['fecha_creacion']} | "
                f"Cartones: {partida['cantidad_cartones']}"
            )
            self.listbox_partidas.insert(tk.END, texto)

    def cargar_partida(self):
        if self.partida_cargada_para_sorteo and self.juego is not None:
            messagebox.showwarning(
                "Error",
                "Ya hay un lote cargado. Primero cerralo con 'Cerrar lote cargado' para poder cargar otro.",
            )
            return

        if not self._partidas_cache:
            messagebox.showwarning("Error", "No hay partidas disponibles para cargar")
            return

        seleccion = self.listbox_partidas.curselection()
        if not seleccion:
            messagebox.showwarning("Error", "Seleccioná una partida")
            return

        index = seleccion[0]
        if index >= len(self._partidas_cache):
            messagebox.showwarning("Error", "Seleccioná una partida válida")
            return

        partida = self._partidas_cache[index]
        cartones = cargar_cartones_de_partida(partida["id"])

        if not cartones:
            messagebox.showerror("Error", "La partida seleccionada no tiene cartones")
            return

        self.partida_id = partida["id"]
        proximo_numero_sorteo = obtener_proximo_numero_sorteo(self.partida_id)
        self.juego = Juego(cartones, proximo_numero_sorteo=proximo_numero_sorteo)
        self.cartones_generados = cartones
        self.partida_cargada_para_sorteo = True
        self.sorteo_db_id = None
        self.label.config(text="Número ingresado: -")
        self.label_estado.config(
            text=f"Cartones generados: {len(cartones)} | Números cargados: 0"
        )
        self.entry_cantidad.delete(0, tk.END)
        self.entry_cantidad.insert(0, str(len(cartones)))
        self.validar_cantidad_ui()
        self.entry_numero.delete(0, tk.END)
        self.actualizar_lista_numeros()
        self.actualizar_estado_flujo()
        self.actualizar_historial_sorteos_ui()

        messagebox.showinfo("OK", f"Partida {self.partida_id} cargada")

    def cerrar_lote_cargado(self):
        if not self.partida_cargada_para_sorteo:
            messagebox.showinfo("Info", "No hay lote cargado para cerrar")
            return

        if self.juego and not self.juego.puede_cerrar_lote():
            messagebox.showwarning(
                "Regla de sorteo",
                "No podés cerrar el lote: el sorteo actual ya tiene números cargados y todavía no tiene ganadores",
            )
            return

        self.juego = None
        self.partida_cargada_para_sorteo = False
        if self.sorteo_db_id is not None:
            cerrar_sorteo(self.sorteo_db_id)
            self.sorteo_db_id = None
        self.label.config(text="Número ingresado: -")
        self.label_estado.config(
            text=f"Cartones generados: {len(self.cartones_generados)} | Números cargados: 0"
        )
        self.entry_numero.delete(0, tk.END)
        self.actualizar_lista_numeros()
        self.validar_cantidad_ui()
        self.actualizar_estado_flujo()
        self.limpiar_historial_sorteos_ui()
        messagebox.showinfo("OK", "Lote cerrado. Ya podés generar nuevos cartones")