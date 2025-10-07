# calculadora_lineal/gui/views/dependencia_menu.py
import tkinter as tk
from tkinter import ttk, messagebox
from ....methods.vectors_mth.dependency import check_vector_dependency, check_matrix_dependency, check_polynomial_dependency
from .vector_input import VectorInput
from ....gui.step_viewer import StepViewer
from ...theme import COLORS, FONTS

class DependenciaView(tk.Frame):
    def __init__(self, parent, controller=None):
        super().__init__(parent, bg=COLORS["bg"])
        self.controller = controller
        self.entries = []
        self.step_viewer = StepViewer(self, height=180)
        self.step_viewer.pack(fill="both", expand=True, pady=10)
        self.current_method = tk.StringVar(value="Vectores")
        self.inputs_frame = tk.Frame(self, bg=COLORS["bg"])
        self.inputs_frame.pack(pady=10)
        self._build_ui()

    def _build_ui(self):
        # ComboBox para seleccionar método
        tk.Label(self, text="Seleccione tipo:", bg=COLORS["bg"], fg=COLORS["text"]).pack()
        combobox = ttk.Combobox(self, textvariable=self.current_method,
                                values=["Vectores", "Matrices", "Polinomios"], state="readonly")
        combobox.pack(pady=5)
        tk.Button(self, text="Generar entrada", command=self.generar_entrada).pack(pady=5)
        tk.Button(self, text="Resolver", command=self.resolver).pack(pady=5)

    def generar_entrada(self):
        for widget in self.inputs_frame.winfo_children():
            widget.destroy()
        self.entries = []
        metodo = self.current_method.get()

        if metodo == "Vectores":
            tk.Label(self.inputs_frame, text="Dimensión:").grid(row=0, column=0)
            self.dim_entry = tk.Entry(self.inputs_frame, width=5)
            self.dim_entry.grid(row=0, column=1)
            tk.Label(self.inputs_frame, text="Cantidad:").grid(row=0, column=2)
            self.count_entry = tk.Entry(self.inputs_frame, width=5)
            self.count_entry.grid(row=0, column=3)
            tk.Button(self.inputs_frame, text="Generar cuadros", command=self.generar_vectores).grid(row=0, column=4, padx=10)

        elif metodo == "Matrices":
            tk.Label(self.inputs_frame, text="Filas:").grid(row=0, column=0)
            self.rows_entry = tk.Entry(self.inputs_frame, width=5)
            self.rows_entry.grid(row=0, column=1)
            tk.Label(self.inputs_frame, text="Columnas:").grid(row=0, column=2)
            self.cols_entry = tk.Entry(self.inputs_frame, width=5)
            self.cols_entry.grid(row=0, column=3)
            tk.Label(self.inputs_frame, text="Cantidad de matrices:").grid(row=0, column=4)
            self.count_matrix_entry = tk.Entry(self.inputs_frame, width=5)
            self.count_matrix_entry.grid(row=0, column=5)
            tk.Button(self.inputs_frame, text="Generar cuadros", command=self.generar_matrices).grid(row=0, column=6, padx=10)

        elif metodo == "Polinomios":
            tk.Label(self.inputs_frame, text="Cantidad de polinomios:").grid(row=0, column=0)
            self.count_poly_entry = tk.Entry(self.inputs_frame, width=5)
            self.count_poly_entry.grid(row=0, column=1)
            tk.Button(self.inputs_frame, text="Generar cuadros", command=self.generar_polinomios).grid(row=0, column=2)

    def generar_vectores(self):
        for widget in self.inputs_frame.winfo_children()[5:]:
            widget.destroy()
        try:
            dim = int(self.dim_entry.get())
            count = int(self.count_entry.get())
        except:
            messagebox.showerror("Error", "Ingrese valores válidos")
            return
        for i in range(count):
            tk.Label(self.inputs_frame, text=f"v{i+1}:").grid(row=i+1, column=0)
            vec_input = VectorInput(self.inputs_frame, dim=dim)
            vec_input.grid(row=i+1, column=1, columnspan=4)
            self.entries.append(vec_input)

    def generar_matrices(self):
        # Aquí agregarías MatrixInput dinámicamente, similar a vectores
        pass

    def generar_polinomios(self):
        for widget in self.inputs_frame.winfo_children()[3:]:
            widget.destroy()
        try:
            count = int(self.count_poly_entry.get())
        except:
            messagebox.showerror("Error", "Ingrese valor válido")
            return
        for i in range(count):
            tk.Label(self.inputs_frame, text=f"p{i+1}(x):").grid(row=i+1, column=0)
            e = tk.Entry(self.inputs_frame, width=30)
            e.grid(row=i+1, column=1)
            self.entries.append(e)

    def resolver(self):
        self.step_viewer.clear()
        metodo = self.current_method.get()
        if metodo == "Vectores":
            vectors = [e.get_vector() for e in self.entries]
            resultado = check_vector_dependency(vectors)
        elif metodo == "Matrices":
            matrices = []  # recolectar de los cuadros
            resultado = check_matrix_dependency(matrices)
        elif metodo == "Polinomios":
            polynomials = [e.get().strip() for e in self.entries]
            resultado = check_polynomial_dependency(polynomials)
        self.step_viewer.add_step(f"Resultado: {resultado}", [[]])