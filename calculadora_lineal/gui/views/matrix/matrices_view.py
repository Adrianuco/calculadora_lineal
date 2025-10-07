# calculadora_lineal/gui/matrices_view.py
import tkinter as tk
from tkinter import ttk, messagebox, Frame, Label, Button
from .matrix_input import MatrixInput
from ...step_viewer import StepViewer
from ....methods.matrix_mth.gauss_jordan import gauss_jordan, analyze_rref, pretty_frac, to_fraction
from calculadora_lineal.methods.matrix_mth.multiplication import matrix_multiply, pretty_frac, handle_vector_warning, is_column_vector

class MatricesView(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, bg="#0D1B2A", *args, **kwargs)
        self._build_ui()

    def _build_ui(self):
        from ...theme import COLORS, FONTS

        # Panel superior: controles de dimensión y método
        controls = tk.Frame(self, bg=COLORS["panel"])
        controls.pack(fill="x", padx=12, pady=12)

        # Dimensiones
        dims = tk.Frame(controls, bg=COLORS["panel"])
        dims.pack(side="left")
        tk.Label(dims, text="Filas:", fg=COLORS["text"], bg=COLORS["panel"], font=FONTS["normal"]).pack(side="left")
        self.ent_rows = tk.Entry(dims, width=4, justify="center", font=FONTS["normal"])
        self.ent_rows.pack(side="left", padx=4)
        tk.Label(dims, text="Variables:", fg=COLORS["text"], bg=COLORS["panel"], font=FONTS["normal"]).pack(side="left", padx=(10,0))
        self.ent_vars = tk.Entry(dims, width=4, justify="center", font=FONTS["normal"])
        self.ent_vars.pack(side="left", padx=4)

        # Selector de método

        # Botones de acción
        actions = tk.Frame(controls, bg=COLORS["panel"])
        actions.pack(side="right")
        self.btn_gen = tk.Button(actions, text="Generar matriz", font=FONTS["normal"], bg=COLORS["accent"], fg="#062235", bd=0, padx=12, pady=8, command=self.generar_matriz)
        self.btn_gen.pack(side="left", padx=8)
        self.btn_solve = tk.Button(actions, text="Resolver", font=FONTS["normal"], bg=COLORS["accent"], fg="#062235", bd=0, padx=12, pady=8, command=self.resolver)
        self.btn_solve.pack(side="left", padx=8)

        # Panel principal: izquierda -> matriz + conclusiones, derecha -> pasos
        main = tk.Frame(self, bg=COLORS["bg"])
        main.pack(fill="both", expand=True, padx=12, pady=8)

        # Columna izquierda
        self.left_col = tk.Frame(main, bg=COLORS["bg"])
        self.left_col.pack(side="left", fill="both", expand=False, padx=(0,8))

        # Matriz
        self.matrix_container = tk.Frame(self.left_col, bg=COLORS["bg"])
        self.matrix_container.pack(fill="both", expand=False)
        self.matrix_widget = None

        # Conclusiones (panel fijo debajo de la matriz) -> ahora con Text (solo-lectura) + scrollbar
        self.conclusions_panel = tk.Frame(self.left_col, bg=COLORS["card"], bd=0, relief="flat")
        self.conclusions_panel.pack(fill="both", pady=(8,0), padx=0)

        self.txt_conclusions = tk.Text(
            self.conclusions_panel,
            height=16,   # más alto
            width=50,    # más ancho
            bg=COLORS["card"],
            fg=COLORS["text"],
            bd=0,
            wrap="word",
            font=("Consolas", 13)  # fuente monospace y más grande
        )
        self.txt_conclusions.pack(side="left", fill="both", expand=True, padx=(8,0), pady=8)

        # Scrollbar para el panel de conclusiones
        scroll_c = tk.Scrollbar(self.conclusions_panel, command=self.txt_conclusions.yview)
        self.txt_conclusions.configure(yscrollcommand=scroll_c.set)
        scroll_c.pack(side="right", fill="y", padx=(0,8), pady=8)

        # lo dejamos en modo solo lectura hasta que lo actualicemos en resolver()
        self.txt_conclusions.configure(state="disabled")

        # Columna derecha: StepViewer
        self.right_col = tk.Frame(main, bg=COLORS["bg"])
        self.right_col.pack(side="right", fill="both", expand=True)
        self.step_viewer = StepViewer(self.right_col)
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
        self.matrix_widget = MatrixInput(self.matrix_container, rows=n, cols=m, include_rhs=True, col_headers=headers)
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

        # Llamar gauss_jordan (devuelve matriz RREF y pasos)
        A_rref, pasos = gauss_jordan(A, record_steps=True)

        # Mostrar pasos en step_viewer
        self.step_viewer.clear()
        for p in pasos:
            self.step_viewer.add_step(p["descripcion"], p["matriz"])

        # --- Análisis propio a partir de A_rref ---
        n_rows = len(A_rref)
        n_cols = len(A_rref[0]) if n_rows else 0
        n_vars = max(0, n_cols - 1)  # columnas de variables (excluyendo RHS)

        # 1) detectar filas inconsistentes (0 ... 0 | b != 0)
        inconsistent = False
        for i in range(n_rows):
            all_zero = True
            for j in range(n_vars):
                if A_rref[i][j] != 0:
                    all_zero = False
                    break
            if all_zero and (n_cols > 0) and (A_rref[i][n_vars] != 0):
                inconsistent = True
                break

        # 2) detectar pivotes: por cada fila, tomar el primer elemento no nulo en columnas de variables
        pivot_cols = []
        row_of_pivot = {}  # col -> fila
        for i in range(n_rows):
            for j in range(n_vars):
                if A_rref[i][j] != 0:
                    if j not in pivot_cols:
                        pivot_cols.append(j)
                        row_of_pivot[j] = i
                    break

        pivot_cols_sorted = sorted(pivot_cols)
        free_vars = [j for j in range(n_vars) if j not in pivot_cols_sorted]

        # Construir salida textual
        lines = []

        # Mostrar pivotes (1-indexado para el usuario)
        if pivot_cols_sorted:
            lines.append("Los Pivotes se encuentran en las columnas: " + ", ".join(str(p+1) for p in pivot_cols_sorted))
        else:
            lines.append("Pivotes: —")

        if inconsistent:
            lines.append("\nResultado: El sistema NO tiene solución (inconsistente).")
        else:
            if len(free_vars) == 0:
                # Solución única
                lines.append("\nResultado: Solución única.")
                # obtener solución directamente de filas pivote
                sol = [0] * n_vars
                for j in range(n_vars):
                    if j in row_of_pivot:
                        r = row_of_pivot[j]
                        sol[j] = A_rref[r][n_vars]
                    else:
                        sol[j] = 0
                lines.append("Solución:")
                for idx, val in enumerate(sol):
                    lines.append(f"  x{idx+1} = {pretty_frac(val)}")

                if pivot_cols_sorted:
                    lines.append("\nVariables básicas: " + ", ".join(f"x{p+1}" for p in pivot_cols_sorted))
            else:
                # Infinitas soluciones
                lines.append("\nResultado: Infinitas soluciones.")
                lines.append("Variables libres: " + ", ".join(f"x{f+1}" for f in free_vars))
                if pivot_cols_sorted:
                    lines.append("Variables básicas: " + ", ".join(f"x{p+1}" for p in pivot_cols_sorted))

                # asignar parámetros t1, t2, ... a variables libres
                param_map = {free_var: f"t{idx+1}" for idx, free_var in enumerate(free_vars)}

                lines.append("\nExpresiones (variables básicas en función de parámetros)")
                # para cada variable, mostrar su expresión
                for j in range(n_vars):
                    if j in free_vars:
                        lines.append(f"  x{j+1} = {param_map[j]}")
                    elif j in pivot_cols_sorted:
                        r = row_of_pivot[j]
                        rhs = A_rref[r][n_vars]  # término independiente
                        parts = []
                        # empezamos por RHS si no es cero
                        if rhs != 0:
                            parts.append(pretty_frac(rhs))
                        # coeficientes para cada variable libre (x_k)
                        for k in free_vars:
                            coeff = -A_rref[r][k]  # x_j = rhs - sum(A[r][k]*x_k) -> coeff para t := -A[r][k]
                            if coeff == 0:
                                continue
                            # formatear el término
                            if coeff == 1:
                                term = f"+ {param_map[k]}"
                            elif coeff == -1:
                                term = f"- {param_map[k]}"
                            else:
                                if coeff > 0:
                                    term = f"+ {pretty_frac(coeff)}*{param_map[k]}"
                                else:
                                    term = f"- {pretty_frac(-coeff)}*{param_map[k]}"
                            parts.append(term)
                        # unir partes cuidando el signo inicial
                        expr = " ".join(parts).strip()
                        if expr.startswith("+ "):
                            expr = expr[2:]
                        if expr == "":
                            expr = "0"
                        lines.append(f"  x{j+1} = {expr}")

        # Escribir todo en el panel de conclusiones (Text widget)
        concl_text = "\n".join(lines)

        self.txt_conclusions.configure(state="normal")
        self.txt_conclusions.delete("1.0", tk.END)
        self.txt_conclusions.insert(tk.END, concl_text + "\n\n")

        # Añadir preview de la matriz final (RREF) con monospace para mejor alineación
        try:
            self.txt_conclusions.insert(tk.END, "Matriz final:\n")

            # formateo tabular: cada columna mismo ancho
            str_matrix = [[pretty_frac(x) for x in row] for row in A_rref]
            col_widths = [max(len(str_matrix[i][j]) for i in range(len(str_matrix)))
                        for j in range(len(str_matrix[0]))]

            for row in str_matrix:
                row_str = "  ".join(val.rjust(col_widths[j]) for j, val in enumerate(row))
                self.txt_conclusions.insert(tk.END, row_str + "\n")
        except Exception:
            # en caso de que pretty_frac falle por algún tipo inesperado, proteger
            self.txt_conclusions.insert(tk.END, "(No se pudo mostrar preview de matriz)\n")

        self.txt_conclusions.configure(state="disabled")

import tkinter as tk
from .matrix_input import MatrixInput
from ...step_viewer import StepViewer
from ....methods.matrix_mth.multiplication import matrix_multiply, pretty_frac, handle_vector_warning, is_column_vector

import tkinter as tk
from tkinter import messagebox
from .matrix_input import MatrixInput
from ...step_viewer import StepViewer
from ....methods.matrix_mth.multiplication import matrix_multiply, pretty_frac, handle_vector_warning, is_column_vector

class MatrixMultiplyView(tk.Frame):
    """Vista para multiplicar dos matrices A y B"""

    def __init__(self, master, controller, *args, **kwargs):
        super().__init__(master, bg="#0D1B2A", *args, **kwargs)
        self.controller = controller
        self.matrix_input_A = None
        self.matrix_input_B = None
        self._build_ui()

    def _build_ui(self):
        from ...theme import COLORS, FONTS

        # Panel superior: controles de dimensiones + botones
        controls = tk.Frame(self, bg=COLORS["panel"])
        controls.pack(fill="x", padx=12, pady=12)

        # Dimensiones Matriz A
        dims_A = tk.Frame(controls, bg=COLORS["panel"])
        dims_A.pack(side="left", padx=(0,20))
        tk.Label(dims_A, text="Matriz A:", fg=COLORS["text"], bg=COLORS["panel"], font=FONTS["normal"]).pack(side="left")
        self.ent_rows_A = tk.Entry(dims_A, width=4, justify="center", font=FONTS["normal"])
        self.ent_rows_A.pack(side="left", padx=2)
        tk.Label(dims_A, text="x", fg=COLORS["text"], bg=COLORS["panel"], font=FONTS["normal"]).pack(side="left")
        self.ent_cols_A = tk.Entry(dims_A, width=4, justify="center", font=FONTS["normal"])
        self.ent_cols_A.pack(side="left", padx=2)

        # Dimensiones Matriz B
        dims_B = tk.Frame(controls, bg=COLORS["panel"])
        dims_B.pack(side="left", padx=(20,0))
        tk.Label(dims_B, text="Matriz B:", fg=COLORS["text"], bg=COLORS["panel"], font=FONTS["normal"]).pack(side="left")
        self.ent_rows_B = tk.Entry(dims_B, width=4, justify="center", font=FONTS["normal"])
        self.ent_rows_B.pack(side="left", padx=2)
        tk.Label(dims_B, text="x", fg=COLORS["text"], bg=COLORS["panel"], font=FONTS["normal"]).pack(side="left")
        self.ent_cols_B = tk.Entry(dims_B, width=4, justify="center", font=FONTS["normal"])
        self.ent_cols_B.pack(side="left", padx=2)

        # Botones generar/multiplicar
        actions = tk.Frame(controls, bg=COLORS["panel"])
        actions.pack(side="right")
        self.btn_gen = tk.Button(actions, text="Generar matrices", font=FONTS["normal"],
                                 bg=COLORS["accent"], fg="#062235", bd=0, padx=12, pady=6,
                                 command=self.generar_matrices)
        self.btn_gen.pack(side="left", padx=6)
        self.btn_mult = tk.Button(actions, text="Multiplicar", font=FONTS["normal"],
                                  bg=COLORS["accent"], fg="#062235", bd=0, padx=12, pady=6,
                                  command=self.calculate)
        self.btn_mult.pack(side="left", padx=6)

        # Panel principal: izquierda -> matrices + conclusiones, derecha -> pasos
        main = tk.Frame(self, bg=COLORS["bg"])
        main.pack(fill="both", expand=True, padx=12, pady=8)

        # Columna izquierda
        self.left_col = tk.Frame(main, bg=COLORS["bg"])
        self.left_col.pack(side="left", fill="both", expand=False, padx=(0,8))

        # Panel para matrices
        self.mat_panel = tk.Frame(self.left_col, bg=COLORS["bg"])
        self.mat_panel.pack(fill="both", expand=False)

        # Panel de conclusiones (gris)
        self.conclusions_panel = tk.Frame(self.left_col, bg=COLORS["card"])
        self.conclusions_panel.pack(fill="both", expand=True, pady=(8,0))

        self.txt_conclusions = tk.Text(
            self.conclusions_panel,
            height=16,
            width=50,
            bg=COLORS["card"],
            fg=COLORS["text"],
            bd=0,
            wrap="word",
            font=("Consolas", 13)
        )
        self.txt_conclusions.pack(side="left", fill="both", expand=True, padx=(8,0), pady=8)

        scroll_c = tk.Scrollbar(self.conclusions_panel, command=self.txt_conclusions.yview)
        self.txt_conclusions.configure(yscrollcommand=scroll_c.set)
        scroll_c.pack(side="right", fill="y", padx=(0,8), pady=8)
        self.txt_conclusions.configure(state="disabled")

        # Columna derecha: StepViewer (azul)
        self.right_col = tk.Frame(main, bg=COLORS["bg"])
        self.right_col.pack(side="right", fill="both", expand=True)
        self.step_viewer = StepViewer(self.right_col)
        self.step_viewer.pack(fill="both", expand=True)

    def generar_matrices(self):
        try:
            nA = int(self.ent_rows_A.get())
            mA = int(self.ent_cols_A.get())
            nB = int(self.ent_rows_B.get())
            mB = int(self.ent_cols_B.get())
            if nA <= 0 or mA <= 0 or nB <= 0 or mB <= 0:
                raise ValueError
            if mA != nB:
                raise ValueError("Columnas de A deben coincidir con filas de B")
        except Exception as e:
            messagebox.showerror("Error", f"Dimensiones inválidas: {e}")
            return

        # Limpiar panel de matrices
        for widget in self.mat_panel.winfo_children():
            widget.destroy()

        tk.Label(self.mat_panel, text="Matriz A", fg="white", bg="#0D1B2A").pack()
        self.matrix_input_A = MatrixInput(self.mat_panel, rows=nA, cols=mA, include_rhs=False)
        self.matrix_input_A.pack(pady=4)

        tk.Label(self.mat_panel, text="Matriz B", fg="white", bg="#0D1B2A").pack()
        self.matrix_input_B = MatrixInput(self.mat_panel, rows=nB, cols=mB, include_rhs=False)
        self.matrix_input_B.pack(pady=4)

        self.step_viewer.clear()
        self.txt_conclusions.configure(state="normal")
        self.txt_conclusions.delete("1.0", tk.END)
        self.txt_conclusions.configure(state="disabled")

    def calculate(self):
        if not self.matrix_input_A or not self.matrix_input_B:
            from tkinter import messagebox
            messagebox.showwarning("Atención", "Primero genera las matrices")
            return

        # Obtener matrices
        A = self.matrix_input_A.get_matrix()
        B = self.matrix_input_B.get_matrix()

        # Mensaje de vector (si aplica)
        vector_warning = handle_vector_warning(A, B)

        # Limpiar cuadros
        self.txt_conclusions.configure(state="normal")
        self.txt_conclusions.delete("1.0", tk.END)
        self.step_viewer.clear()

        # Multiplicación
        try:
            result, steps = matrix_multiply(A, B)
        except ValueError as e:
            self.txt_conclusions.insert(tk.END, vector_warning + f"Error: {e}")
            self.txt_conclusions.configure(state="disabled")
            return

        # StepViewer azul: mostrar todos los pasos
        for step in steps:
            self.step_viewer.add_step(step["descripcion"], step["matriz"])
        self.step_viewer.add_step("Resultado final", result)

        # Cuadro gris: mostrar paso a paso y luego resultado final como C = [A, B]
        self.txt_conclusions.insert(tk.END, vector_warning)
        self.txt_conclusions.insert(tk.END, "Pasos de la multiplicación:\n\n")
        for step in steps:
            self.txt_conclusions.insert(tk.END, step["descripcion"] + "\n")
            for row in step["matriz"]:
                self.txt_conclusions.insert(tk.END, "  " + "  ".join(pretty_frac(x) for x in row) + "\n")
            self.txt_conclusions.insert(tk.END, "\n")

        # Resultado final
        self.txt_conclusions.insert(tk.END, "Resultado final:\nC = [\n")
        for row in result:
            self.txt_conclusions.insert(tk.END, "  " + "  ".join(pretty_frac(x) for x in row) + "\n")
        self.txt_conclusions.insert(tk.END, "]\n")
        self.txt_conclusions.configure(state="disabled")