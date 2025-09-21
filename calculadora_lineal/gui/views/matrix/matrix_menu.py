# calculadora_lineal/gui/views/matrix_menu.py
import tkinter as tk
from ...theme import COLORS, FONTS

class MatrixMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg"])
        self.controller = controller

        title = tk.Label(
            self,
            text="Menú de Matrices",
            font=FONTS["title"],
            fg=COLORS["text"],
            bg=COLORS["bg"]
        )
        title.pack(pady=20)

        btn_gauss = tk.Button(
            self,
            text="Gauss-Jordan",
            font=FONTS["normal"],
            bg=COLORS["accent"],
            fg="white",
            relief="flat",
            command=lambda: self.controller.show_matrices_view()
        )
        btn_gauss.pack(pady=10, ipadx=10, ipady=5)