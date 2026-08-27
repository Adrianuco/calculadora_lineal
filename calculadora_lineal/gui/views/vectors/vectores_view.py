# calculadora_lineal/gui/vectores_view.py
import tkinter as tk
from tkinter import messagebox
from ..matrix.matrix_input import MatrixInput
from ...step_viewer import StepViewer
from ....methods.matrix_mth.gauss_jordan import gauss_jordan, analyze_rref, pretty_frac

class VectoresView(tk.Frame):
    """
    Pantalla para verificar combinación lineal:
    Dados k vectores u1..uk (en R^d) y v, comprobar si existe c's tales que sum c_i u_i = v.
    Internamente generamos la matriz aumentada (d x (k+1)) y llamamos a gauss_jordan.
    """
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, bg="#0D1B2A", *args, **kwargs)
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

        main = tk.Frame(self, bg="#0D1B2A")
        main.pack(fill="both", expand=True, padx=8, pady=8)

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
        # Col headers: u1, u2, ..., uk, v
        headers = [f"u{j+1}" for j in range(k)] + ["v"]
        self.matrix_widget = MatrixInput(self.left, rows=d, cols=k, include_rhs=True, col_headers=headers)
        self.matrix_widget.pack(padx=6, pady=6)
        self.step_viewer.clear()

    def resolver(self):
        if not self.matrix_widget:
            messagebox.showwarning("Atención", "Primero genere los vectores.")
            return
        try:
            A = self.matrix_widget.get_matrix(parse=True)  # d x (k+1)
        except Exception as e:
            messagebox.showerror("Error al leer vectores", str(e))
            return

        A_rref, pasos = gauss_jordan(A, record_steps=True)
        self.step_viewer.clear()
        for p in pasos:
            self.step_viewer.add_step(p["descripcion"], p["matriz"])

        info = analyze_rref(A_rref)
        if info["tipo"] == "inconsistente":
            self.step_viewer.add_step("Conclusión: El vector v NO es combinación lineal de u1..uk (inconsistente).", A_rref)
        elif info["tipo"] == "única":
            coeffs = info["solucion"]
            coeffs_str = ", ".join([f"c{j+1} = {pretty_frac(c)}" for j, c in enumerate(coeffs)])
            self.step_viewer.add_step("Conclusión: Sí es combinación linear. Coeficientes (únicos): " + coeffs_str, A_rref)
        else:
            free = info["free_vars"]
            self.step_viewer.add_step("Conclusión: Sí es combinación linear (hay infinitas combinaciones). Variables libres: " + ", ".join(f"x{f+1}" for f in free), A_rref)
            for var_idx, expr in info["expresiones"].items():
                self.step_viewer.add_step(f"c{var_idx+1} = {expr}", A_rref)