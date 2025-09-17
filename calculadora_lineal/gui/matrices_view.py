# calculadora_lineal/gui/matrices_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from .widgets.matrix_input import MatrixInput
from .step_viewer import StepViewer
from ..metodos.gauss_jordan import gauss_jordan, analyze_rref, pretty_frac, to_fraction

class MatricesView(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, bg="#0D1B2A", *args, **kwargs)
        self._build_ui()

    def _build_ui(self):
        # Panel superior: controls
        controls = tk.Frame(self, bg="#0D1B2A")
        controls.pack(fill="x", padx=10, pady=10)

        tk.Label(controls, text="Filas (ecuaciones):", fg="white", bg="#0D1B2A").grid(row=0, column=0, sticky="w")
        self.ent_rows = tk.Entry(controls, width=4)
        self.ent_rows.grid(row=0, column=1, padx=6)

        tk.Label(controls, text="Variables:", fg="white", bg="#0D1B2A").grid(row=0, column=2, sticky="w", padx=(12,0))
        self.ent_vars = tk.Entry(controls, width=4)
        self.ent_vars.grid(row=0, column=3, padx=6)

        btn_gen = tk.Button(controls, text="Generar matriz", command=self.generar_matriz)
        btn_gen.grid(row=0, column=4, padx=10)

        btn_solve = tk.Button(controls, text="Resolver (Gauss-Jordan)", command=self.resolver)
        btn_solve.grid(row=0, column=5, padx=6)

        # Toggle final format
        self.show_frac = tk.BooleanVar(value=True)
        tk.Checkbutton(controls, text="Final en fracciones (si off -> decimales)", variable=self.show_frac, bg="#0D1B2A", fg="white").grid(row=0, column=6, padx=8)

        # Área principal: izquierda -> grid, derecha -> steps
        main = tk.Frame(self, bg="#0D1B2A")
        main.pack(fill="both", expand=True, padx=10, pady=8)

        self.left = tk.Frame(main, bg="#0D1B2A")
        self.left.pack(side="left", fill="both", expand=False)

        self.right = tk.Frame(main, bg="#0D1B2A")
        self.right.pack(side="right", fill="both", expand=True)

        # Placeholder
        self.matrix_widget = None
        self.step_viewer = StepViewer(self.right)
        self.step_viewer.pack(fill="both", expand=True)

    def generar_matriz(self):
        try:
            n = int(self.ent_rows.get())
            m = int(self.ent_vars.get())
            if n <= 0 or m <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Error", "Ingrese filas y variables válidos (enteros > 0).")
            return

        if self.matrix_widget:
            self.matrix_widget.destroy()
        headers = [f"x{j+1}" for j in range(m)] + ["b"]
        self.matrix_widget = MatrixInput(self.left, rows=n, cols=m, include_rhs=True, col_headers=headers)
        self.matrix_widget.pack(padx=6, pady=6)

        # limpiar pasos
        self.step_viewer.clear()

    def resolver(self):
        if not self.matrix_widget:
            messagebox.showwarning("Atención", "Primero genere la matriz.")
            return
        try:
            A = self.matrix_widget.get_matrix(parse=True)
        except Exception as e:
            messagebox.showerror("Error al leer matriz", str(e))
            return

        # Llamar gauss_jordan
        A_rref, pasos = gauss_jordan(A, record_steps=True)

        # Mostrar pasos en step_viewer
        self.step_viewer.clear()
        for p in pasos:
            self.step_viewer.add_step(p["descripcion"], p["matriz"])

        # Análisis final
        info = analyze_rref(A_rref)
        if info["tipo"] == "inconsistente":
            self.step_viewer.add_step("Resultado: El sistema NO tiene solución (inconsistente).", A_rref)
        elif info["tipo"] == "única":
            # mostrar solución (según toggle fracción/decimal)
            sol = info["solucion"]
            if self.show_frac.get():
                sol_strs = [pretty_frac(x) for x in sol]
            else:
                sol_strs = [f"{float(x):.6g}" for x in sol]
            desc = "Resultado: solución única -> " + ", ".join([f"x{j+1} = {s}" for j, s in enumerate(sol_strs)])
            self.step_viewer.add_step(desc, A_rref)
        else:  # infinitas
            free = info["free_vars"]
            desc = f"Resultado: infinitas soluciones. Variables libres: {', '.join('x'+str(f+1) for f in free)}"
            self.step_viewer.add_step(desc, A_rref)
            # añadir expresiones
            for var_idx, expr in info["expresiones"].items():
                self.step_viewer.add_step(f"x{var_idx+1} = {expr}", A_rref)