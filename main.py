import tkinter as tk

from ui.app import BingoApp
from ui.licencia_dialog import verificar_licencia_al_inicio

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    if not verificar_licencia_al_inicio(root):
        root.destroy()
    else:
        root.deiconify()
        app = BingoApp(root)
        root.mainloop()
