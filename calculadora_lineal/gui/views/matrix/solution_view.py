# calculadora_lineal/gui/views/matrix/solution_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from ...theme import COLORS, FONTS

from .matrix_input import MatrixInput
from ...step_viewer import StepViewer
from ....methods.matrix_mth.solution_set import describe_solution_set
from ....methods.matrix_mth.gauss_jordan import pretty_frac

class SolutionView(tk.Frame):
    """
    Pantalla para calcular y mostrar el conjunto solución de un sistema lineal.
    Permite elegir filas y número de variables; crea la matriz aumentada (A | b).
    Muestra A, x, b antes de reducir, pasos de Gauss-Jordan (si se solicitan)
    y la descripción final del conjunto solución.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg"])
        self.controller = controller

        # Título
        lbl_title = tk.Label(self, text="Conjunto Solución de un Sistema Lineal",
                             font=("Segoe UI", 18, "bold"), bg=COLORS["bg"], fg=COLORS.get("text", "black"))
        lbl_title.pack(pady=(10,6))

        lbl_desc = tk.Label(self,
                            text="Ingrese la matriz aumentada (A | b). Seleccione filas (ecuaciones) y número de variables.",
                            font=("Segoe UI", 10),
                            bg=COLORS["bg"],
                            fg=COLORS.get("muted", "#888"))
        lbl_desc.pack(pady=(0, 10))

        # Controles para dimensiones
        dims = tk.Frame(self, bg=COLORS["bg"])
        dims.pack(pady=(0,8))

        tk.Label(dims, text="Filas (ecuaciones):", bg=COLORS["bg"], fg=COLORS.get("text")).grid(row=0, column=0, padx=4)
        self.rows_var = tk.IntVar(value=3)
        self.spin_rows = tk.Spinbox(dims, from_=1, to=40, width=4, textvariable=self.rows_var)
        self.spin_rows.grid(row=0, column=1, padx=4)

        tk.Label(dims, text="Variables (n):", bg=COLORS["bg"], fg=COLORS.get("text")).grid(row=0, column=2, padx=8)
        self.vars_var = tk.IntVar(value=3)
        self.spin_vars = tk.Spinbox(dims, from_=1, to=40, width=4, textvariable=self.vars_var)
        self.spin_vars.grid(row=0, column=3, padx=4)

        btn_create = ttk.Button(dims, text="Crear matriz (A | b)", command=self.create_matrix_input)
        btn_create.grid(row=0, column=4, padx=(10,0))

        # Contenedor para MatrixInput
        self.input_holder = tk.Frame(self, bg=COLORS["bg"])
        self.input_holder.pack(pady=(6, 10))

        # inicialmente creamos una matriz por defecto
        self.matrix_input = None
        self.create_matrix_input()

        # Botones acciones
        actions = tk.Frame(self, bg=COLORS["bg"])
        actions.pack(pady=(6,12))

        btn_calc = ttk.Button(actions, text="Calcular conjunto solución", command=self.compute_solution)
        btn_calc.pack(side="left", padx=6)

        btn_clear = ttk.Button(actions, text="Limpiar", command=self.clear_all)
        btn_clear.pack(side="left", padx=6)

        # Viewer para pasos y resultados
        self.viewer = StepViewer(self)
        self.viewer.pack(fill="both", expand=True, padx=10, pady=6)

    # -------------------------
    def create_matrix_input(self):
        """Crea (o recrea) el MatrixInput basado en las dimensiones elegidas."""
        for w in self.input_holder.winfo_children():
            w.destroy()
        rows = int(self.rows_var.get())
        nvars = int(self.vars_var.get())
        try:
            self.matrix_input = MatrixInput(self.input_holder, rows=rows, cols=nvars, include_rhs=True)
            self.matrix_input.pack()
        except TypeError:
            # fallback si tu MatrixInput no soporta include_rhs
            self.matrix_input = MatrixInput(self.input_holder, rows=rows, cols=nvars + 1)
            self.matrix_input.pack()

    def clear_all(self):
        """Limpia entradas y viewer."""
        if self.matrix_input:
            try:
                self.matrix_input.clear()
            except Exception:
                for w in self.input_holder.winfo_children():
                    w.destroy()
                self.create_matrix_input()
        self.viewer.clear()

    # -------------------------
    def _format_vector_str(self, vec):
        return "[" + "  ".join(pretty_frac(v) for v in vec) + "]"

    def _format_matrix_for_step(self, M):
        return M

    def compute_solution(self):
        if not self.matrix_input:
            messagebox.showwarning("Atención", "Primero cree la matriz (clic en 'Crear matriz').")
            return
        try:
            A_aug = self.matrix_input.get_matrix(parse=True)
        except Exception as e:
            messagebox.showerror("Error", f"Error al leer la matriz: {e}")
            return
        if not A_aug or not A_aug[0]:
            messagebox.showwarning("Aviso", "Ingrese una matriz válida.")
            return

        # Separar A y b
        try:
            A = [row[:-1] for row in A_aug]
            b = [row[-1] for row in A_aug]
        except Exception:
            messagebox.showerror("Error", "La matriz debe ser aumentada (última columna = b).")
            return

        nvars = len(A[0])

        # Mostrar Ax = b antes de reducir
        self.viewer.clear()
        self.viewer.add_text("────────── Sistema (antes de reducir) ──────────")
        self.viewer.add_step("A (coeficientes):", self._format_matrix_for_step(A))
        self.viewer.add_text("x = " + "[" + "  ".join(f"x{i+1}" for i in range(nvars)) + "]")
        b_col = [[val] for val in b]
        self.viewer.add_step("b (términos independientes):", self._format_matrix_for_step(b_col))

        # Calcular conjunto solución
        try:
            result = describe_solution_set(A_aug, include_steps=True)
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un problema al calcular la solución: {e}")
            return

        # Mostrar pasos
        steps = result.get("steps") or []
        if steps:
            self.viewer.add_text("────── Pasos (Gauss–Jordan) ──────")
            for paso in steps:
                desc = paso.get("descripcion", "")
                mat = paso.get("matriz", [])
                if mat:
                    self.viewer.add_step(desc, self._format_matrix_for_step(mat))
                else:
                    self.viewer.add_text(desc)

        # RREF
        A_rref = result.get("A_rref") or []
        if A_rref:
            self.viewer.add_step("Matriz en forma reducida (RREF):", self._format_matrix_for_step(A_rref))

        # Conjunto Solución final
        self.viewer.add_text("────────── Conjunto Solución ──────────")
        # Renombramos las líneas generales
        general_lines = result.get("general_solution_lines") or []
        cleaned_lines = []
        for line in general_lines:
            if isinstance(line, str):
                line = line.replace("Forma vectorial (núcleo)", "Conjunto Solución")
            cleaned_lines.append(line)
        for ln in cleaned_lines:
            self.viewer.add_text(ln)


        # Consistencia
        if result.get("consistent") is False:
            self.viewer.add_text("⚠️  El sistema es inconsistente (no tiene solución).")