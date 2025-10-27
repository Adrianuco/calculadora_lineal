# calculadora_lineal/gui/matrix_inverse_view.py
import tkinter as tk
from tkinter import messagebox
from .matrix_input import MatrixInput
from ...step_viewer import StepViewer
from ....methods.matrix_mth.gauss_jordan import gauss_jordan, pretty_frac, to_fraction
from ....methods.matrix_mth.operations import pretty_frac, to_fraction

class MatrixInverseView(tk.Frame):
    """
    Vista para calcular la matriz inversa o resolver Ax=b (modo sistema).
    - Modo "Matriz": solo A -> invertir A.
    - Modo "Sistema": A y vector b (lado aparte) -> x = A^{-1} * b.
    Reglas:
      - 2x2: usar fórmula directa (determinante y 1/det * adj).
      - >=3: usar Gauss-Jordan sobre [A | I] y mostrar pasos.
    """
    def __init__(self, master, controller=None, *args, **kwargs):
        super().__init__(master, bg="#0D1B2A", *args, **kwargs)
        self.controller = controller
        self.matrix_widget = None
        self.vector_entries = []  # lista de tk.Entry para b (si modo sistema)
        self.mode = tk.StringVar(value="Matriz")  # "Matriz" o "Sistema"
        self._build_ui()

    def _build_ui(self):
        from ...theme import COLORS, FONTS

        # Controles superiores
        controls = tk.Frame(self, bg=COLORS["panel"])
        controls.pack(fill="x", padx=12, pady=12)

        # Modo (Matriz / Sistema)
        mode_frame = tk.Frame(controls, bg=COLORS["panel"])
        mode_frame.pack(side="left")
        tk.Label(mode_frame, text="Modo:", fg=COLORS["text"], bg=COLORS["panel"], font=FONTS["normal"]).pack(side="left", padx=(0,6))
        rb_mat = tk.Radiobutton(mode_frame, text="Matriz", variable=self.mode, value="Matriz", bg=COLORS["panel"], fg=COLORS["text"], selectcolor=COLORS["panel"], command=self._on_mode_change)
        rb_sis = tk.Radiobutton(mode_frame, text="Sistema (Ax=b)", variable=self.mode, value="Sistema", bg=COLORS["panel"], fg=COLORS["text"], selectcolor=COLORS["panel"], command=self._on_mode_change)
        rb_mat.pack(side="left", padx=4)
        rb_sis.pack(side="left", padx=4)

        # Tamaño
        tk.Label(controls, text="n (n x n):", fg=COLORS["text"], bg=COLORS["panel"], font=FONTS["normal"]).pack(side="left", padx=(12,4))
        self.ent_n = tk.Entry(controls, width=4, justify="center", font=FONTS["normal"])
        self.ent_n.pack(side="left")
        self.ent_n.insert(0, "3")

        # Botones
        btn_gen = tk.Button(controls, text="Generar", font=FONTS["normal"], bg=COLORS["accent"], fg="#062235", bd=0, padx=12, pady=6, command=self.generar_matriz)
        btn_gen.pack(side="left", padx=8)
        btn_solve = tk.Button(controls, text="Resolver", font=FONTS["normal"], bg=COLORS["accent"], fg="#062235", bd=0, padx=12, pady=6, command=self.resolver)
        btn_solve.pack(side="right", padx=8)

        # Main panels
        main = tk.Frame(self, bg=COLORS["bg"])
        main.pack(fill="both", expand=True, padx=12, pady=8)

        # Left: matriz A + resultados (cuadro azul)
        left = tk.Frame(main, bg=COLORS["bg"])
        left.pack(side="left", fill="both", expand=False, padx=(0,8))

        self.matrix_container = tk.Frame(left, bg=COLORS["bg"])
        self.matrix_container.pack(fill="both", expand=False)

        # Resultado (cuadro azul)
        self.result_panel = tk.Frame(left, bg=COLORS["card"])
        self.result_panel.pack(fill="both", expand=True, pady=(8,0))
        self.txt_result = tk.Text(self.result_panel, height=18, width=48, bg=COLORS["card"], fg=COLORS["text"], bd=0, wrap="word", font=("Consolas", 13))
        self.txt_result.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        scroll_r = tk.Scrollbar(self.result_panel, command=self.txt_result.yview)
        self.txt_result.configure(yscrollcommand=scroll_r.set)
        scroll_r.pack(side="right", fill="y")
        self.txt_result.configure(state="disabled")

        # Middle: espacio para vector b (si modo sistema)
        self.vector_container = tk.Frame(main, bg=COLORS["bg"])
        self.vector_container.pack(side="left", fill="y", padx=(0,8), pady=8)

        # Right: StepViewer (cuadro gris)
        right = tk.Frame(main, bg=COLORS["bg"])
        right.pack(side="right", fill="both", expand=True)
        self.step_viewer = StepViewer(right)
        self.step_viewer.pack(fill="both", expand=True)

        # inicializar sin widgets
        self._on_mode_change()

    def _on_mode_change(self):
        """Actualiza interfaz cuando cambia modo (Matriz/Sistema)."""
        # Si vector existía y ahora se cambió a Matriz, borrar vector entries
        for w in self.vector_container.winfo_children():
            w.destroy()
        self.vector_entries = []
        # Si ya hay matriz creada y el modo es Sistema, recrear vector espacio
        if self.matrix_widget:
            rows = self.matrix_widget.rows
            if self.mode.get() == "Sistema":
                self._create_vector_inputs(rows)
        # limpiar pasos y resultados
        self.step_viewer.clear()
        self._clear_result_text()

    def generar_matriz(self):
        """Genera MatrixInput para A y, si aplica, el vector b al lado."""
        try:
            n = int(self.ent_n.get())
            if n <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Error", "Ingrese un tamaño válido (entero > 0).")
            return

        # destruir anterior A
        if self.matrix_widget:
            self.matrix_widget.destroy()
            self.matrix_widget = None

        headers = [f"a{j+1}" for j in range(n)]
        # include_rhs=False porque b estará aparte
        self.matrix_widget = MatrixInput(self.matrix_container, rows=n, cols=n, include_rhs=False, col_headers=headers)
        self.matrix_widget.pack(padx=6, pady=6)

        # crear vector b si estamos en modo Sistema
        if self.mode.get() == "Sistema":
            self._create_vector_inputs(n)
        else:
            # limpiar la columna de vector si existe
            for w in self.vector_container.winfo_children():
                w.destroy()
            self.vector_entries = []

        # limpiar pasos y resultado
        self.step_viewer.clear()
        self._clear_result_text()

    def _create_vector_inputs(self, n):
        """Crea un pequeño panel con n entries (vector columna b)."""
        for w in self.vector_container.winfo_children():
            w.destroy()
        self.vector_entries = []

        lbl = tk.Label(self.vector_container, text="Vector b", bg="#0D1B2A", fg="white", font=("Segoe UI", 10, "bold"))
        lbl.pack(pady=(4,4))
        for i in range(n):
            e = tk.Entry(self.vector_container, width=8, justify="center")
            e.pack(pady=3)
            e.insert(0, "0")
            self.vector_entries.append(e)

    def _clear_result_text(self):
        self.txt_result.configure(state="normal")
        self.txt_result.delete("1.0", tk.END)
        self.txt_result.configure(state="disabled")

    # ---------------------
    # Helpers matemáticos
    # ---------------------
    def _to_fraction_matrix(self, M):
        """Convierte lista de filas a Fraction usando to_fraction del módulo."""
        return [[to_fraction(x) for x in row] for row in M]

    def _determinant_2x2(self, A):
        a = to_fraction(A[0][0]); b = to_fraction(A[0][1])
        c = to_fraction(A[1][0]); d = to_fraction(A[1][1])
        return a * d - b * c

    def _adjugate_2x2(self, A):
        a = to_fraction(A[0][0]); b = to_fraction(A[0][1])
        c = to_fraction(A[1][0]); d = to_fraction(A[1][1])
        # adj(A) = [[d, -b], [-c, a]]
        return [[d, -b], [-c, a]]

    def _rref_of_A(self, A):
        """Devuelve A_rref (solo A, sin RHS) y pasos de gauss_jordan si se decide usar."""
        # construir A_aug = [row + [0]]
        A_copy = self._to_fraction_matrix(A)
        A_aug = [row + [to_fraction(0)] for row in A_copy]
        A_rref_aug, pasos = gauss_jordan(A_aug, record_steps=True)
        A_rref = [row[:-1] for row in A_rref_aug]
        return A_rref, pasos

    def _pivot_info(self, A_rref):
        """Dado A_rref (RREF), devuelve (pivot_cols_sorted, rank)."""
        n_rows = len(A_rref)
        n_cols = len(A_rref[0]) if n_rows else 0
        pivots = {}
        for i in range(n_rows):
            first_nonzero = next((j for j, val in enumerate(A_rref[i]) if val != 0), None)
            if first_nonzero is not None and A_rref[i][first_nonzero] == 1:
                pivots[first_nonzero] = i
        pivot_cols_sorted = sorted(pivots.keys())
        return pivot_cols_sorted, len(pivot_cols_sorted)

    def _format_matrix_pretty(self, M):
        lines = []
        str_mat = [[pretty_frac(x) for x in row] for row in M]
        if not str_mat:
            return ""
        col_widths = [max(len(str_mat[i][j]) for i in range(len(str_mat))) for j in range(len(str_mat[0]))]
        for row in str_mat:
            lines.append("  " + "  ".join(val.rjust(col_widths[j]) for j, val in enumerate(row)))
        return "\n".join(lines)

    # ---------------------
    # Resolver lógica
    # ---------------------
    def resolver(self):
        """Entry point cuando el usuario presiona Resolver."""
        if not self.matrix_widget:
            messagebox.showwarning("Atención", "Primero genere la matriz.")
            return

        try:
            A = self.matrix_widget.get_matrix(parse=True)
        except Exception as e:
            messagebox.showerror("Error al leer matriz", str(e))
            return

        # convertir a Fraction internamente
        try:
            A_frac = self._to_fraction_matrix(A)
        except Exception as e:
            messagebox.showerror("Error al convertir matriz", str(e))
            return

        n = len(A_frac)
        if any(len(row) != n for row in A_frac):
            messagebox.showerror("Error", "La matriz debe ser cuadrada.")
            return

        # Si modo sistema, leer b
        b_vec = None
        if self.mode.get() == "Sistema":
            if not self.vector_entries or len(self.vector_entries) != n:
                messagebox.showerror("Error", "Vector b ausente o de tamaño incorrecto. Genere la matriz con el modo 'Sistema' activo.")
                return
            try:
                b_vec = [to_fraction(e.get()) for e in self.vector_entries]
            except Exception as e:
                messagebox.showerror("Error al leer vector b", str(e))
                return

        # CASE 1: n == 2 -> usar fórmula directa (no gauss)
        if n == 2:
            det = self._determinant_2x2(A_frac)
            # mostrar pasos mínimos en StepViewer (si quieres mantener simple, mostramos sólo el cálculo del determinante)
            self.step_viewer.clear()
            self.step_viewer.add_step(f"Cálculo del determinante (2x2): det = a*d - b*c = {pretty_frac(det)}", A_frac)

            if det == 0:
                # no se continúa
                resultado_txt = "⚠️ Determinante = 0 → La matriz NO es invertible.\n"
                resultado_txt += "Es una matriz singular.\n"
                # also show pivot info from RREF for messages
                A_rref, _ = self._rref_of_A(A_frac)
                piv, rank = self._pivot_info(A_rref)
                resultado_txt += f"\nA tiene {rank} posiciones pivote\n"
                if rank < n:
                    resultado_txt += "La ecuación Ax = 0 tiene soluciones no triviales.\n"
                    resultado_txt += "Las columnas de A NO son linealmente independientes.\n"
                self._mostrar_result_text(resultado_txt)
                return

            # inversa por fórmula
            adj = self._adjugate_2x2(A_frac)
            inv = [[adj[i][j] / det for j in range(2)] for i in range(2)]

            # si es sistema, multiplicar inv * b
            if b_vec is not None:
                x = []
                for i in range(2):
                    s = to_fraction(0)
                    for j in range(2):
                        s += inv[i][j] * b_vec[j]
                    x.append(s)

                # construir texto resultado con mensajes de pivote etc
                A_rref, _ = self._rref_of_A(A_frac)
                piv, rank = self._pivot_info(A_rref)
                lines = []
                lines.append("Resultado: Solución del sistema x = A^{-1} * b\n")
                for idx, val in enumerate(x):
                    lines.append(f"  x{idx+1} = {pretty_frac(val)}")
                lines.append("")
                lines.append(f"A tiene {rank} posiciones pivote")
                if rank == n:
                    lines.append("La ecuación Ax = 0 tiene solamente solución trivial.")
                    lines.append("Las columnas de A forman un conjunto linealmente independiente.")
                else:
                    lines.append("La ecuación Ax = 0 tiene soluciones no triviales.")
                    lines.append("Las columnas de A NO son linealmente independientes.")
                # mostrar inv y x
                lines.append("\nMatriz inversa A⁻¹:\n")
                lines.append(self._format_matrix_pretty(inv))
                self._mostrar_result_text("\n".join(lines))
                return
            else:
                # solo inversa
                A_rref, _ = self._rref_of_A(A_frac)
                piv, rank = self._pivot_info(A_rref)
                lines = []
                lines.append("✅ Determinante ≠ 0 -> La matriz es invertible (2x2).")
                lines.append("Es una matriz no singular.")
                lines.append("\nMatriz inversa A⁻¹:\n")
                lines.append(self._format_matrix_pretty(inv))
                lines.append("")
                lines.append(f"A tiene {rank} posiciones pivote")
                if rank == n:
                    lines.append("La ecuación Ax = 0 tiene solamente solución trivial.")
                    lines.append("Las columnas de A forman un conjunto linealmente independiente.")
                else:
                    lines.append("La ecuación Ax = 0 tiene soluciones no triviales.")
                    lines.append("Las columnas de A NO son linealmente independientes.")
                self._mostrar_result_text("\n".join(lines))
                return

        # CASE 2: n >= 3 -> usar Gauss-Jordan sobre [A | I]
        # construir aumentada [A | I]
        from fractions import Fraction
        identidad = [[Fraction(1 if i == j else 0) for j in range(n)] for i in range(n)]
        A_ext = [A_frac[i] + identidad[i] for i in range(n)]

        # Ejecutar Gauss-Jordan (devuelve A_rref_aug y pasos)
        try:
            A_rref_aug, pasos = gauss_jordan(A_ext, record_steps=True)
        except Exception as e:
            messagebox.showerror("Error durante Gauss-Jordan", str(e))
            return

        # Mostrar pasos en StepViewer
        self.step_viewer.clear()
        for p in pasos:
            self.step_viewer.add_step(p["descripcion"], p["matriz"])

        # Extraer lado izquierdo y derecho
        left_rref = [row[:n] for row in A_rref_aug]
        right_candidate = [row[n:] for row in A_rref_aug]

        # Verificar si izquierda es identidad (pivotes completos)
        piv_cols, rank = self._pivot_info(left_rref)
        if rank < n:
            # No invertible
            lines = []
            lines.append("⚠️ Determinante = 0 -> La matriz NO es invertible (no se redujo a identidad).")
            lines.append("Es una matriz singular.\n")
            lines.append(f"A tiene {rank} posiciones pivote")
            lines.append("La ecuación Ax = 0 tiene soluciones no triviales.")
            lines.append("Las columnas de A NO son linealmente independientes.")
            self._mostrar_result_text("\n".join(lines))
            return

        # Si invertible: right_candidate es la inversa
        inv = right_candidate

        # Si modo sistema -> multiplicar A^{-1} * b
        if b_vec is not None:
            try:
                x = []
                for i in range(n):
                    s = Fraction(0)
                    for j in range(n):
                        s += inv[i][j] * b_vec[j]
                    x.append(s)
            except Exception as e:
                messagebox.showerror("Error al multiplicar A^{-1} * b", str(e))
                return

            lines = []
            lines.append("✅ Solución del sistema x = A^{-1} * b\n")
            for idx, val in enumerate(x):
                lines.append(f"  x{idx+1} = {pretty_frac(val)}")
            lines.append("")
            lines.append("Matriz inversa A⁻¹:\n")
            lines.append(self._format_matrix_pretty(inv))
            lines.append("")
            lines.append(f"A tiene {rank} posiciones pivote")
            lines.append("La ecuación Ax = 0 tiene solamente solución trivial.")
            lines.append("Las columnas de A forman un conjunto linealmente independiente.")
            self._mostrar_result_text("\n".join(lines))
            return
        else:
            # solo mostrar inversa y mensajes
            lines = []
            lines.append("✅ Determinante ≠ 0 -> La matriz es invertible.")
            lines.append("Es una matriz no singular.")
            lines.append("\nMatriz inversa A⁻¹:\n")
            lines.append(self._format_matrix_pretty(inv))
            lines.append("")
            lines.append(f"A tiene {rank} posiciones pivote")
            lines.append("La ecuación Ax = 0 tiene solamente solución trivial.")
            lines.append("Las columnas de A forman un conjunto linealmente independiente.")
            self._mostrar_result_text("\n".join(lines))
            return

    def _mostrar_result_text(self, texto):
        """Inserta texto formateado en el cuadro azul (solo-lectura)."""
        self.txt_result.configure(state="normal")
        self.txt_result.delete("1.0", tk.END)
        self.txt_result.insert(tk.END, texto)
        self.txt_result.configure(state="disabled")