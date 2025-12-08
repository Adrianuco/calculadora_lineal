# calculadora_lineal/gui/views/help/help.py
import tkinter as tk
from tkinter import ttk
from ...theme import COLORS, FONTS

class HelpView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg"])
        self.controller = controller

        self.selected_topic = tk.StringVar(value="Seleccione una opción aquí")

        self.help_texts = {
            "Enfoque": "¿En qué se enfoca el programa?"
            "\n\nEste programa está diseñado para facilitar cálculos lineales y análisis numérico, proporcionando herramientas eficientes para trabajar con matrices, vectores y otros conceptos matemáticos relacionados.",

            "Interfaz": "¿Como funciona la interfaz?"
            "\n\nEl programa está estructurado en varias secciones accesibles desde el menú principal. Cada sección ofrece funcionalidades específicas para diferentes tipos de cálculos y análisis. La interfaz es intuitiva y está diseñada para facilitar la navegación y el uso de las herramientas disponibles.",

            "Matrices": "¿Que métodos posee de Matrices?"
            "\n\nEn esta sección, se incluyen métodos para operaciones con matrices como suma, resta, multiplicación, determinantes, inversas, y más.",

            "Vectores": "¿Que métodos posee de Vectores?"
            "\n\nEn esta sección, se incluyen métodos para operaciones con vectores como suma, resta, producto escalar, y más.",

            "Análisis Numérico": "¿Que métodos posee de Análisis Numérico?"
            "\n\nEn esta sección, se incluyen métodos para errores, bisección, regla falsa, punto fijo, Newton Raphson, y más.",

            "Configuración": "¿Como funciona las configuraciones?"
            "\n\nEn esta sección, puedes ajustar las preferencias del programa, como estar en pantalla completo o cerrarlo.",

            "Creditos" : "Integrantes del Grupo C:"
            "\nAdriano Jezrael Almanza Sanchez \nIsaac Elias Aragon Alfaro \nJuan Carlos Castellón Rivera"
            "\n\nDocente: \nJose Andres Munguia Cortez"
            "\n\nFecha de Finalización: \nLunes 8 de diciembre del año 2025"
            "\n\n©UAM 2025",
        }

        self._build_ui()

    def _build_ui(self):
        top = tk.Frame(self, bg=COLORS["panel"])
        top.pack(fill="x", padx=12, pady=12)

        tk.Label(
            top,
            text="Secciones de Ayuda:",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=FONTS["normal"]
        ).pack(side="left")

        self.combo = ttk.Combobox(
            top,
            textvariable=self.selected_topic,
            values=list(self.help_texts.keys()),
            state="readonly",
            width=40
        )
        self.combo.pack(side="left", padx=10)
        self.combo.bind("<<ComboboxSelected>>", self._update_text)

        self.result_panel = tk.Frame(self, bg=COLORS["card"])
        self.result_panel.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.txt_result = tk.Text(
            self.result_panel,
            bg=COLORS["card"],
            fg=COLORS["text"],
            font=("Consolas", 15),
            wrap="word",
            bd=0
        )
        self.txt_result.pack(side="left", fill="both", expand=True, padx=8, pady=8)

        scroll_r = tk.Scrollbar(
            self.result_panel,
            command=self.txt_result.yview
        )
        self.txt_result.configure(yscrollcommand=scroll_r.set)
        scroll_r.pack(side="right", fill="y")

        self._update_text()

    def _update_text(self, event=None):
        topic = self.selected_topic.get()
        text = self.help_texts.get(topic, "No hay información disponible. Dirigase a la sección correspondiente de arriba para más detalles.")

        self.txt_result.configure(state="normal")
        self.txt_result.delete("1.0", tk.END)
        self.txt_result.insert("1.0", text)
        self.txt_result.configure(state="disabled")