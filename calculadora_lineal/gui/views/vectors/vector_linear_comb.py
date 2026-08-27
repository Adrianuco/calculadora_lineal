# calculadora_lineal/gui/views/vectors/vectors_linear_comb.py
import tkinter as tk
from tkinter import messagebox
from ..matrix.matrix_input import MatrixInput
from ...step_viewer import StepViewer
from ....methods.vectors_mth.linear_comb import check_linear_combination  # método que implementaremos

class VectorsLinearComb(tk.Frame):
    """
    Pantalla para verificar combinación lineal de vectores.
    Dada una lista de vectores u1..uk y un vector v, comprueba si existe c1..ck tales que sum c_i u_i = v.
    """
    def __init__(self, master, controller, *args, **kwargs):
        super().__init__(master, bg="#0D1B2A", *args, **kwargs)
        self.controller = controller
        self._build_ui()

    def _build_ui(self):
        controls = tk.Frame(self, bg="#0D1B2A")
        controls.pack(fill="x", padx=10, pady=8)

        tk.Label(controls, text="Dimensión (d):", fg="white", bg="#0D1B2A").grid(row=0, column=0)
        self.ent_dim = tk.Entry(controls, width=4)
        self.ent_dim.grid(row=0, column=1, padx=6)

        tk.Label(controls, text="Cantidad de vectores (k):", fg="white", bg="#0D1B2A").grid(row=0, column=2, padx=(12,0))
        self.ent_k = tk.Entry(controls, width=4)
        self.ent_k.grid(row=0, column=3, padx=6)

        btn_gen = tk.Button(controls, text="Generar (u1..uk y v)", command=self.generar)
        btn_gen.grid(row=0, column=4, padx=8)

        btn_res = tk.Button(controls, text="Verificar combinación lineal", command=self.resolver)
        btn_res.grid(row=0, column=5, padx=6)

        # Panel principal
        main = tk.Frame(self, bg="#0D1B2A")
        main.pack(fill="both", expand=True, padx=8, pady=8)

        # izquierda -> matriz, derecha -> pasos
        self.left = tk.Frame(main, bg="#0D1B2A")
        self.left.pack(side="left", fill="both", expand=False)
        self.right = tk.Frame(main, bg="#0D1B2A")
        self.right.pack(side="right", fill="both", expand=True)

        self.matrix_widget = None
        self.step_viewer = StepViewer(self.right)
        self.step_viewer.pack(fill="both", expand=True)

    def generar(self):
        try:
            d = int(self.ent_dim.get())
            k = int(self.ent_k.get())
            if d <= 0 or k <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Error", "Ingrese dimensión y cantidad de vectores válidos (enteros > 0).")
            return

        if self.matrix_widget:
            self.matrix_widget.destroy()
        headers = [f"u{j+1}" for j in range(k)] + ["v"]
        self.matrix_widget = MatrixInput(self.left, rows=d, cols=k, include_rhs=True, col_headers=headers)
        self.matrix_widget.pack(padx=6, pady=6)
        self.step_viewer.clear()

    def resolver(self):
        if not self.matrix_widget:
            messagebox.showwarning("Atención", "Primero genere los vectores.")
            return

        try:
            A = self.matrix_widget.get_matrix(parse=True)
        except Exception as e:
            messagebox.showerror("Error al leer vectores", str(e))
            return

        # Llamamos al método externo
        result = check_linear_combination(A)  # implementaremos este método en methods/vectors.py

        # Mostrar pasos
        self.step_viewer.clear()
        for paso in result.get("steps", []):
            if paso.get("type") == "matrix":
                self.step_viewer.add_step(paso["desc"], paso["matrix"])
            else:  # texto plano
                self.step_viewer.add_text(paso["desc"])

        # Mostrar conclusión
        conclusion = result.get("conclusion", "No se pudo determinar la combinación lineal.")
        self.step_viewer.add_step("Conclusión: " + conclusion, A)