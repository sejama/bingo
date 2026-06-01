import tkinter as tk
from tkinter import messagebox

from services.licencia import activar_clave, verificar_inicio


def verificar_licencia_al_inicio(root: tk.Tk) -> bool:
    """
    Chequea la licencia antes de mostrar la app.
    Retorna True si puede continuar, False si debe cerrarse.
    """
    puede, mensaje, _ = verificar_inicio()

    if puede:
        if "gracia" in mensaje.lower():
            messagebox.showwarning(
                "Modo sin conexión",
                mensaje,
                parent=root,
            )
        return True

    # Licencia revocada (no pedir clave de nuevo)
    if "revocada" in mensaje.lower() or "expiró" in mensaje.lower():
        messagebox.showerror("Licencia inválida", mensaje, parent=root)
        return False

    # Sin licencia registrada: mostrar diálogo de activación
    return _mostrar_dialogo_activacion(root)


def _mostrar_dialogo_activacion(root: tk.Tk) -> bool:
    resultado = {"ok": False}

    dialogo = tk.Toplevel(root)
    dialogo.title("Activación de licencia")
    dialogo.geometry("400x200")
    dialogo.resizable(False, False)
    dialogo.grab_set()
    dialogo.protocol("WM_DELETE_WINDOW", lambda: _cerrar(dialogo, resultado, root))

    tk.Label(
        dialogo,
        text="Bingo Escolar",
        font=("Arial", 14, "bold"),
    ).pack(pady=(18, 4))

    tk.Label(
        dialogo,
        text="Ingresá tu clave de licencia para continuar:",
        font=("Arial", 10),
    ).pack(pady=(0, 10))

    frame = tk.Frame(dialogo)
    frame.pack()

    entry = tk.Entry(frame, width=26, font=("Arial", 12))
    entry.pack(side="left", padx=(0, 8))
    entry.focus_set()

    label_estado = tk.Label(dialogo, text="", fg="red", font=("Arial", 9))
    label_estado.pack(pady=(6, 0))

    def activar():
        clave = entry.get().strip()
        if not clave:
            label_estado.config(text="Ingresá una clave")
            return

        btn_activar.config(state="disabled", text="Validando...")
        dialogo.update()

        valida, msg = activar_clave(clave)
        btn_activar.config(state="normal", text="Activar")

        if valida:
            resultado["ok"] = True
            dialogo.destroy()
        else:
            label_estado.config(text=msg)
            entry.select_range(0, tk.END)

    entry.bind("<Return>", lambda _e: activar())

    btn_activar = tk.Button(frame, text="Activar", command=activar, width=10)
    btn_activar.pack(side="left")

    root.wait_window(dialogo)
    return resultado["ok"]


def _cerrar(dialogo: tk.Toplevel, resultado: dict, root: tk.Tk) -> None:
    if not resultado["ok"]:
        if messagebox.askyesno(
            "Salir",
            "Sin licencia válida la app no puede iniciarse.\n¿Querés salir?",
            parent=dialogo,
        ):
            dialogo.destroy()
            root.destroy()
