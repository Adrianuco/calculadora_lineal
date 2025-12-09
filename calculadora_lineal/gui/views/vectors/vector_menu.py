# calculadora_lineal/gui/views/vectors/vector_menu.py
import tkinter as tk
from ...theme import COLORS, FONTS

class VectorMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["panel"])
        self.controller = controller

        title = tk.Label(self, text="Operaciones con Vectores", 
                         font=FONTS["title"], fg=COLORS["text"], bg=COLORS["panel"])
        title.pack(pady=20)

        buttons = [
            ("Combinación lineal", controller.show_vector_linear_comb),
            ("Ecuaciones vectoriales", controller.show_vector_equations),
            ("Dependencia Lineal", lambda: controller.show_dependencia_view())
        ]

        for text, cmd in buttons:
            btn = tk.Button(self, text=text, font=FONTS["normal"],
                            fg=COLORS["text"], bg=COLORS["card"],
                            activebackground=COLORS["sidebar_active"],
                            activeforeground=COLORS["text"],
                            relief="flat", padx=10, pady=5,
                            command=cmd)
            btn.pack(pady=10, ipadx=10, ipady=5)