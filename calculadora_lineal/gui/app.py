# algebra_lineal/gui/app.py
import os
import tkinter as tk
from tkinter import ttk
from .theme import COLORS, FONTS
from PIL import Image, ImageTk 

# Importamos los menús principales de matrices y vectores
from .views.matrix.matrix_menu import MatrixMenu
from .views.vectors.vector_menu import VectorMenu
from .views.analysis.analysis_menu import AnalysisMenu
from .views.matrix.matrices_view import MatricesView
from .views.vectors.dependency_view import DependenciaView

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

    from PIL import Image, ImageTk
    def create_sidebar(self):
        ICON_SIZE = (36, 36)
        LABEL_HEIGHT = 80
        SIDEBAR_WIDTH = 100  # ancho fijo de la sidebar

        def load_icon(path, fallback_emoji):
            try:
                img = Image.open(path).convert("RGBA").resize(ICON_SIZE, Image.LANCZOS)
                return ImageTk.PhotoImage(img)
            except Exception:
                return None

        current_dir = os.path.dirname(__file__)

        menu_def = [
            ("Inicio", os.path.join(current_dir, "assets/icons/home.png"), "🏠"),
            ("Matrices", os.path.join(current_dir, "assets/icons/matrix.png"), "🧮"),
            ("Vectores", os.path.join(current_dir, "assets/icons/vectors.png"), "🧭"),
            ("Análisis Numérico", os.path.join(current_dir, "assets/icons/analysis.png"), "📊"),
            ("Ajustes", os.path.join(current_dir, "assets/icons/settings.png"), "⚙️"),
            ("Ayuda", os.path.join(current_dir, "assets/icons/help.png"), "❔"),
        ]

        # Limpiamos sidebar si había algo antes
        for widget in self.sidebar.winfo_children():
            widget.destroy()

        self.menu_items = {}
        self.sidebar_icons = {}  # mantener referencia de imágenes

        for name, icon_path, emoji in menu_def:
            lbl_frame = tk.Frame(self.sidebar, bg=COLORS["sidebar"], width=SIDEBAR_WIDTH, height=LABEL_HEIGHT)
            lbl_frame.pack_propagate(False)  # evitar que el frame cambie de tamaño
            lbl_frame.pack(fill="x", pady=2)

            icon_img = load_icon(icon_path, emoji)
            if icon_img:
                lbl = tk.Label(
                    lbl_frame,
                    image=icon_img,
                    text=name,
                    compound="top",
                    font=FONTS["normal"],
                    fg=COLORS["text"],
                    bg=COLORS["sidebar"],
                    width=SIDEBAR_WIDTH,
                    height=LABEL_HEIGHT,
                    anchor="n"
                )
                self.sidebar_icons[name] = icon_img
            else:
                lbl = tk.Label(
                    lbl_frame,
                    text=f"{emoji}\n{name}",
                    font=FONTS["icon"],
                    fg=COLORS["text"],
                    bg=COLORS["sidebar"],
                    width=SIDEBAR_WIDTH,
                    height=LABEL_HEIGHT,
                    anchor="n"
                )

            lbl.pack(expand=True, fill="both")

            # Hover
            lbl.bind("<Enter>", lambda e, l=lbl: l.configure(bg=COLORS["sidebar_btn"]))
            lbl.bind("<Leave>", lambda e, l=lbl: l.configure(bg=COLORS["sidebar"]))

            # Click: cambiar pantalla y marcar activo
            def on_click(event, n=name, l=lbl):
                self.show_screen(n)
                for b in self.menu_items.values():
                    b.configure(bg=COLORS["sidebar"])
                l.configure(bg=COLORS["sidebar_active"])

            lbl.bind("<Button-1>", on_click)

            self.menu_items[name] = lbl

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
        elif name == "Vectores":
            self.show_vectores()
        elif name == "Análisis Numérico":
            self.show_anaylisis()
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
        # Limpiar contenido
        for widget in self.container.winfo_children():
            widget.destroy()
        frame = MatrixMenu(self.container, self)
        frame.pack(fill="both", expand=True)
    
    def show_matrices_view(self):
        # limpia el contenedor
        for widget in self.container.winfo_children():
            widget.destroy()

        # carga la pantalla de Gauss-Jordan
        frame = MatricesView(self.container)
        frame.pack(expand=True, fill="both")

    def show_matrix_operations_view(self):
        for widget in self.container.winfo_children():
            widget.destroy()

        from .views.matrix.matrix_operations_view import MatrixOperationsView
        frame = MatrixOperationsView(self.container, self)
        frame.pack(expand=True, fill="both")

    def show_inverse_view(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        from .views.matrix.matrix_inverse_view import MatrixInverseView
        frame = MatrixInverseView(self.container, controller=self)
        frame.pack(fill="both", expand=True)
    
    def show_vectores(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        frame = VectorMenu(self.container, self) 
        frame.pack(fill="both", expand=True)

    def show_vector_operations(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        from .views.vectors.vector_operations import VectorOperations
        frame = VectorOperations(self.container, self)
        frame.pack(expand=True, fill="both")

    def show_vector_linear_comb(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        from .views.vectors.vector_linear_comb import VectorsLinearComb
        frame = VectorsLinearComb(self.container, self)
        frame.pack(expand=True, fill="both")

    def show_vector_equations(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        from .views.vectors.vector_equations import VectorEquations
        frame = VectorEquations(self.container, self)
        frame.pack(expand=True, fill="both")

    def show_dependencia_view(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        frame = DependenciaView(self.container, self)
        frame.pack(expand=True, fill="both")

    def show_determinant_view(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        from .views.matrix.determinant_view import DeterminantView
        frame = DeterminantView(self.container, self)
        frame.pack(expand=True, fill="both")

    def show_anaylisis(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        frame = AnalysisMenu(self.container, self)
        frame.pack(expand=True, fill="both")

    def show_errors_view(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        from .views.analysis.errors_view import ErrorsView
        frame = ErrorsView(self.container, self)
        frame.pack(expand=True, fill="both")

    def show_bisection_false_view(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        from .views.analysis.bisection_false_view import BisectionFalseView
        frame = BisectionFalseView(self.container, self)
        frame.pack(expand=True, fill="both")

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

    def show_solution_view(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        from .views.matrix.solution_view import SolutionView
        frame = SolutionView(self.container, self)
        frame.pack(expand=True, fill="both")

if __name__ == "__main__":
    app = AlgebraApp()
    app.mainloop()