# calculadora_lineal/gui/views/analysis_menu.py
import tkinter as tk
from ...theme import COLORS, FONTS

class AnalysisMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg"])
        self.controller = controller

        title = tk.Label(
            self,
            text="Menú de Análisis Numérico",
            font=FONTS["title"],
            fg=COLORS["text"],
            bg=COLORS["bg"]
        )
        title.pack(pady=20)

        btn_errors = tk.Button(
            self,
            text="Errores",
            font=FONTS["normal"],
            bg=COLORS["accent"],
            fg="white",
            relief="flat",
            command=lambda: self.controller.show_errors_view()
        )
        btn_errors.pack(pady=10, ipadx=10, ipady=5)