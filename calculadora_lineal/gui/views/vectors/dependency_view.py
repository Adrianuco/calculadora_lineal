# calculadora_lineal/gui/views/vectors/dependency_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from fractions import Fraction
from ....methods.matrix_mth.gauss_jordan import matrix_to_fraction, pretty_frac
from ....methods.vectors_mth.dependency import (
    check_vector_dependency,
    check_matrix_dependency,
    check_polynomial_dependency,
    to_fraction,
)
from .vector_input import VectorInput
from ....gui.step_viewer import StepViewer
from ...theme import COLORS, FONTS


def safe_pretty(val):
    """Convierte un valor en una fracción o lo deja como texto legible."""
    if isinstance(val, (int, float, Fraction)):
        return pretty_frac(Fraction(val))
    try:
        return pretty_frac(Fraction(str(val)))
    except Exception:
        return str(val)


def safe_fraction(value):
    """Convierte de forma segura un valor a Fraction, evitando errores por cadenas vacías o no numéricas."""
    if value in ("", None):
        return Fraction(0)
    try:
        return Fraction(str(value))
    except Exception:
        return Fraction(0)


class DependenciaView(tk.Frame):
    def __init__(self, parent, controller=None):
        super().__init__(parent, bg=COLORS["bg"])
        self.controller = controller
        self.entries = []
        self.current_method = tk.StringVar(value="Vectores")

        self.step_viewer = StepViewer(self, height=180)
        self.step_viewer.pack(fill="both", expand=True, pady=10)

        self.inputs_frame = tk.Frame(self, bg=COLORS["bg"])
        self.inputs_frame.pack(pady=10)
        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text="Seleccione tipo:", bg=COLORS["bg"], fg=COLORS["text"]).pack()
        combobox = ttk.Combobox(
            self,
            textvariable=self.current_method,
            values=["Vectores", "Matrices", "Polinomios"],
            state="readonly"
        )
        combobox.pack(pady=5)

        btn_frame = tk.Frame(self, bg=COLORS["bg"])
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Generar entrada", font=FONTS["normal"],
                  fg=COLORS["text"], bg=COLORS["card"], relief="flat",
                  command=self.generar_entrada).pack(side="left", padx=5)

        tk.Button(btn_frame, text="Resolver", font=FONTS["normal"],
                  fg=COLORS["text"], bg=COLORS["card"], relief="flat",
                  command=self.resolver).pack(side="left", padx=5)

    def generar_entrada(self):
        for widget in self.inputs_frame.winfo_children():
            widget.destroy()
        self.entries = []

        metodo = self.current_method.get()
        if metodo == "Vectores":
            tk.Label(self.inputs_frame, text="Dimensión:", bg=COLORS["bg"], fg=COLORS["text"]).grid(row=0, column=0)
            self.dim_entry = tk.Entry(self.inputs_frame, width=5)
            self.dim_entry.grid(row=0, column=1)

            tk.Label(self.inputs_frame, text="Cantidad:", bg=COLORS["bg"], fg=COLORS["text"]).grid(row=0, column=2)
            self.count_entry = tk.Entry(self.inputs_frame, width=5)
            self.count_entry.grid(row=0, column=3)

            tk.Button(self.inputs_frame, text="Generar cuadros", bg=COLORS["card"], fg=COLORS["text"],
                      relief="flat", command=self.generar_vectores).grid(row=0, column=4, padx=5)

        elif metodo == "Matrices":
            tk.Label(self.inputs_frame, text="Filas:", bg=COLORS["bg"], fg=COLORS["text"]).grid(row=0, column=0)
            self.rows_entry = tk.Entry(self.inputs_frame, width=5)
            self.rows_entry.grid(row=0, column=1)

            tk.Label(self.inputs_frame, text="Columnas:", bg=COLORS["bg"], fg=COLORS["text"]).grid(row=0, column=2)
            self.cols_entry = tk.Entry(self.inputs_frame, width=5)
            self.cols_entry.grid(row=0, column=3)

            tk.Label(self.inputs_frame, text="Cantidad:", bg=COLORS["bg"], fg=COLORS["text"]).grid(row=0, column=4)
            self.count_matrix_entry = tk.Entry(self.inputs_frame, width=5)
            self.count_matrix_entry.grid(row=0, column=5)

            tk.Button(
                self.inputs_frame,
                text="Generar cuadros",
                bg=COLORS["card"],
                fg=COLORS["text"],
                relief="flat",
                command=self.generar_matrices
            ).grid(row=0, column=6, padx=5)

        elif metodo == "Polinomios":
            tk.Label(self.inputs_frame, text="Cantidad de polinomios:", bg=COLORS["bg"], fg=COLORS["text"]).grid(row=0, column=0)
            self.count_poly_entry = tk.Entry(self.inputs_frame, width=5)
            self.count_poly_entry.grid(row=0, column=1)
            tk.Button(self.inputs_frame, text="Generar cuadros", bg=COLORS["card"], fg=COLORS["text"],
                      relief="flat", command=self.generar_polinomios).grid(row=0, column=2, padx=5)

    def generar_vectores(self):
        for widget in self.inputs_frame.winfo_children()[5:]:
            widget.destroy()
        try:
            dim = int(self.dim_entry.get())
            count = int(self.count_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Ingrese valores válidos")
            return

        self.entries = []
        for i in range(count):
            tk.Label(self.inputs_frame, text=f"v{i+1}:", bg=COLORS["bg"], fg=COLORS["text"]).grid(row=i+1, column=0)
            vec_input = VectorInput(self.inputs_frame, dim=dim)
            vec_input.grid(row=i+1, column=1, columnspan=4, pady=2)
            self.entries.append(vec_input)

    def generar_matrices(self):
        for widget in self.inputs_frame.winfo_children()[6:]:
            widget.destroy()
        try:
            rows = int(self.rows_entry.get())
            cols = int(self.cols_entry.get())
            count = int(self.count_matrix_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Ingrese valores válidos para filas, columnas y cantidad")
            return

        self.entries = []
        for i in range(count):
            tk.Label(self.inputs_frame, text=f"M{i+1}:", bg=COLORS["bg"], fg=COLORS["text"]).grid(row=i+1, column=0)
            mat_frame = tk.Frame(self.inputs_frame, bg=COLORS["bg"])
            mat_frame.grid(row=i+1, column=1, columnspan=cols, pady=2)

            mat_entries = []
            for r in range(rows):
                row_entries = []
                for c in range(cols):
                    e = tk.Entry(mat_frame, width=5)
                    e.grid(row=r, column=c, padx=2, pady=2)
                    row_entries.append(e)
                mat_entries.append(row_entries)
            self.entries.append(mat_entries)

    def generar_polinomios(self):
        for widget in self.inputs_frame.winfo_children()[3:]:
            widget.destroy()
        try:
            count = int(self.count_poly_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Ingrese cantidad válida")
            return

        self.entries = []
        for i in range(count):
            tk.Label(self.inputs_frame, text=f"p{i+1}(x):", bg=COLORS["bg"], fg=COLORS["text"]).grid(row=i+1, column=0)
            e = tk.Entry(self.inputs_frame, width=30)
            e.grid(row=i+1, column=1, pady=2)
            self.entries.append(e)

    def resolver(self):
        self.step_viewer.clear()
        metodo = self.current_method.get()

        try:
            # Obtener datos según tipo
            if metodo == "Vectores":
                vectors = [[safe_fraction(v) for v in e.get_vector()] for e in self.entries]
                pasos, conclusion = check_vector_dependency(vectors)

            elif metodo == "Matrices":
                matrices = []
                for mat_entries in self.entries:
                    mat = []
                    for row_entries in mat_entries:
                        fila = [safe_fraction(e.get().strip()) for e in row_entries]
                        mat.append(fila)
                    matrices.append(mat)
                pasos, conclusion = check_matrix_dependency(matrices)

            elif metodo == "Polinomios":
                polynomials = [e.get().strip() or "0" for e in self.entries]
                pasos, conclusion = check_polynomial_dependency(polynomials)

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al resolver: {e}")
            return

        # Mostrar los pasos
        for paso in pasos:
            titulo = paso.get("titulo", "")
            desc = paso.get("desc", "")
            matrix = paso.get("matrix", None)

            if titulo:
                self.step_viewer.add_text(titulo)

            if matrix:
                # Convertir todo a Fraction antes de pasar a pretty_frac
                matrix_for_display = [
                    [safe_fraction(val) for val in row]
                    for row in matrix
                ]
                self.step_viewer.add_step(desc or "", matrix_for_display)
            elif desc:
                self.step_viewer.add_text(desc)