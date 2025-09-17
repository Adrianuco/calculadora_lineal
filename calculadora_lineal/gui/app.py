# algebra_lineal/gui/app.py
import tkinter as tk
from tkinter import ttk
from .theme import COLORS, FONTS

class AlgebraApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Configuración base de la ventana
        self.title("Calculadora de Álgebra Lineal")
        self.geometry("1000x600")
        self.configure(bg=COLORS["bg"])

        # Sidebar
        self.sidebar = tk.Frame(self, bg=COLORS["sidebar"], width=200)
        self.sidebar.pack(side="left", fill="y")

        # Contenedor principal (donde cambian las pantallas)
        self.container = tk.Frame(self, bg=COLORS["bg"])
        self.container.pack(side="right", expand=True, fill="both")

        # Menú lateral
        self.menu_items = {
            "Inicio": None,
            "Matrices": None,
            "Vectores": None,
            "Análisis Numérico": None,
            "Ajustes": None,
            "Ayuda": None,
        }
        self.active_button = None
        self.create_sidebar()

        # Pantalla inicial
        self.show_screen("Inicio")

    def create_sidebar(self):
        for name in self.menu_items.keys():
            btn = tk.Button(
                self.sidebar,
                text=name,
                font=FONTS["subtitle"],
                fg=COLORS["text"],
                bg=COLORS["sidebar"],
                bd=0,
                relief="flat",
                activebackground=COLORS["sidebar_active"],
                activeforeground=COLORS["text"],
                command=lambda n=name: self.show_screen(n)
            )
            btn.pack(fill="x", pady=2)
            self.menu_items[name] = btn

    def show_screen(self, name):
        # Reset colores de todos los botones
        for btn in self.menu_items.values():
            btn.configure(bg=COLORS["sidebar"], relief="flat")

        # Activar el botón actual
        self.menu_items[name].configure(bg=COLORS["sidebar_active"], relief="sunken")

        # Limpiar contenido
        for widget in self.container.winfo_children():
            widget.destroy()

        # Render según pantalla
        if name == "Inicio":
            self.show_home()
        elif name == "Matrices":
            self.show_matrices()
        else:
            self.show_placeholder(name)

    def show_home(self):
        frame = tk.Frame(self.container, bg=COLORS["bg"])
        frame.pack(expand=True, fill="both")

        lbl = tk.Label(
            frame,
            text="Bienvenido a la Calculadora de Álgebra Lineal",
            font=FONTS["title"],
            fg=COLORS["text"],
            bg=COLORS["bg"],
        )
        lbl.pack(pady=20)

        sub = tk.Label(
            frame,
            text="(Placeholder para logo e info básica)",
            font=FONTS["normal"],
            fg=COLORS["accent"],
            bg=COLORS["bg"],
        )
        sub.pack()

    def show_matrices(self):
        frame = tk.Frame(self.container, bg=COLORS["bg"])
        frame.pack(expand=True, fill="both")

        lbl = tk.Label(
            frame,
            text="Operaciones con Matrices",
            font=FONTS["title"],
            fg=COLORS["text"],
            bg=COLORS["bg"],
        )
        lbl.pack(pady=20)

        sub = tk.Label(
            frame,
            text="Aquí irá el ingreso dinámico de matrices",
            font=FONTS["normal"],
            fg=COLORS["accent"],
            bg=COLORS["bg"],
        )
        sub.pack()

    def show_placeholder(self, name):
        frame = tk.Frame(self.container, bg=COLORS["bg"])
        frame.pack(expand=True, fill="both")

        lbl = tk.Label(
            frame,
            text=f"Pantalla de {name} (en construcción)",
            font=FONTS["title"],
            fg=COLORS["text"],
            bg=COLORS["bg"],
        )
        lbl.pack(pady=20)


if __name__ == "__main__":
    app = AlgebraApp()
    app.mainloop()