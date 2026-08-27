import tkinter as tk
from ...theme import COLORS, FONTS

class VectorOperations(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["panel"])
        self.controller = controller

        title = tk.Label(self, text="Operaciones con Vectores", 
                         font=FONTS["title"], fg=COLORS["text"], bg=COLORS["panel"])
        title.pack(pady=20)

        # Selector de operación
        tk.Label(self, text="Seleccione operación:", 
                 font=FONTS["normal"], fg=COLORS["text"], bg=COLORS["panel"]).pack(pady=10)

        self.op_var = tk.StringVar(value="suma")
        options = [("Suma", "suma"), ("Resta", "resta"), ("Multiplicación", "mult")]
        for text, val in options:
            tk.Radiobutton(self, text=text, variable=self.op_var, value=val,
                           font=FONTS["normal"], fg=COLORS["text"], bg=COLORS["panel"],
                           selectcolor=COLORS["card"]).pack(anchor="w", padx=20)
        
        # Placeholder para inputs (luego hacemos dinámico)
        tk.Label(self, text="[Aquí irán las entradas de vectores e implementación]",
                 font=FONTS["normal"], fg=COLORS["muted"], bg=COLORS["panel"]).pack(pady=20)