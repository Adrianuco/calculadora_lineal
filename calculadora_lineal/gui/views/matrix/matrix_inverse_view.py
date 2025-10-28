import tkinter as tk
from tkinter import ttk, messagebox
from .matrix_input import MatrixInput
from ...step_viewer import StepViewer
from ....methods.matrix_mth.gauss_jordan import gauss_jordan, pretty_frac, to_fraction
from ....methods.matrix_mth.operations import pretty_frac, to_fraction
from ....methods.matrix_mth.gauss import determinant_gauss
from fractions import Fraction


class MatrixInverseView(tk.Frame):
    """
    Vista para calcular la matriz inversa o resolver Ax=b (modo sistema).
    - "Matriz cuadrada": solo A -> invertir A.
    - "Sistema (Ax=b)": A y vector b -> resolver x = A^{-1} * b.
    """

    def __init__(self, master, controller=None, *args, **kwargs):
        super().__init__(master, bg="#0D1B2A", *args, **kwargs)
        self.controller = controller
        self.matrix_widget = None
        self.vector_entries = []
        self.mode = tk.StringVar(value="Matriz cuadrada")
        self._build_ui()

    def _build_ui(self):
        from ...theme import COLORS, FONTS

        controls = tk.Frame(self, bg=COLORS["panel"])
        controls.pack(fill="x", padx=12, pady=12)

        # --- ComboBox modo ---
        tk.Label(controls, text="Modo:", fg=COLORS["text"], bg=COLORS["panel"], font=FONTS["normal"]).pack(side="left", padx=(0, 6))
        self.combo_mode = ttk.Combobox(
            controls,
            textvariable=self.mode,
            values=["Matriz cuadrada", "Sistema (Ax = b)"],
            state="readonly",
            width=20
        )
        self.combo_mode.pack(side="left", padx=(0, 12))
        self.combo_mode.bind("<<ComboboxSelected>>", lambda e: self._on_mode_change())

        # Tamaño n
        tk.Label(controls, text="n (n x n):", fg=COLORS["text"], bg=COLORS["panel"], font=FONTS["normal"]).pack(side="left", padx=(12, 4))
        self.ent_n = tk.Entry(controls, width=4, justify="center", font=FONTS["normal"])
        self.ent_n.pack(side="left")
        self.ent_n.insert(0, "3")

        # Botones
        tk.Button(controls, text="Generar", font=FONTS["normal"], bg=COLORS["accent"],
                  fg="#062235", bd=0, padx=12, pady=6, command=self.generar_matriz).pack(side="left", padx=8)
        tk.Button(controls, text="Resolver", font=FONTS["normal"], bg=COLORS["accent"],
                  fg="#062235", bd=0, padx=12, pady=6, command=self.resolver).pack(side="right", padx=8)

        # --- Panel principal ---
        main = tk.Frame(self, bg=COLORS["bg"])
        main.pack(fill="both", expand=True, padx=12, pady=8)

        # Izquierda: matriz A + resultados
        left = tk.Frame(main, bg=COLORS["bg"])
        left.pack(side="left", fill="both", expand=False, padx=(0, 8))

        # contenedor conjunto A | b
        self.matrix_vector_container = tk.Frame(left, bg=COLORS["bg"])
        self.matrix_vector_container.pack(fill="both", expand=False, pady=4)

        self.matrix_container = tk.Frame(self.matrix_vector_container, bg=COLORS["bg"])
        self.matrix_container.grid(row=0, column=0, sticky="n")

        self.vector_container = tk.Frame(self.matrix_vector_container, bg=COLORS["bg"])
        self.vector_container.grid(row=0, column=1, sticky="n", padx=(10, 0))

        # Panel de resultado
        self.result_panel = tk.Frame(left, bg=COLORS["card"])
        self.result_panel.pack(fill="both", expand=True, pady=(8, 0))
        self.txt_result = tk.Text(self.result_panel, height=18, width=48, bg=COLORS["card"],
                                  fg=COLORS["text"], bd=0, wrap="word", font=("Consolas", 13))
        self.txt_result.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        scroll_r = tk.Scrollbar(self.result_panel, command=self.txt_result.yview)
        self.txt_result.configure(yscrollcommand=scroll_r.set)
        scroll_r.pack(side="right", fill="y")
        self.txt_result.configure(state="disabled")

        # Derecha: StepViewer
        right = tk.Frame(main, bg=COLORS["bg"])
        right.pack(side="right", fill="both", expand=True)
        self.step_viewer = StepViewer(right)
        self.step_viewer.pack(fill="both", expand=True)

        self._on_mode_change()

    def _on_mode_change(self):
        for w in self.vector_container.winfo_children():
            w.destroy()
        self.vector_entries = []
        if self.matrix_widget:
            rows = self.matrix_widget.rows
            if self.mode.get() == "Sistema (Ax = b)":
                self._create_vector_inputs(rows)
        self.step_viewer.clear()
        self._clear_result_text()

    def generar_matriz(self):
        try:
            n = int(self.ent_n.get())
            if n <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Error", "Ingrese un tamaño válido (entero > 0).")
            return

        if self.matrix_widget:
            self.matrix_widget.destroy()
            self.matrix_widget = None

        headers = [f"a{j+1}" for j in range(n)]
        self.matrix_widget = MatrixInput(self.matrix_container, rows=n, cols=n, include_rhs=False, col_headers=headers)
        self.matrix_widget.pack(padx=6, pady=6)

        if self.mode.get() == "Sistema (Ax = b)":
            self._create_vector_inputs(n)
        else:
            for w in self.vector_container.winfo_children():
                w.destroy()
            self.vector_entries = []

        self.step_viewer.clear()
        self._clear_result_text()

    def _create_vector_inputs(self, n):
        for w in self.vector_container.winfo_children():
            w.destroy()
        self.vector_entries = []
        lbl = tk.Label(self.vector_container, text="b", bg="#0D1B2A", fg="white", font=("Segoe UI", 10, "bold"))
        lbl.pack(pady=(4, 4))
        for i in range(n):
            e = tk.Entry(self.vector_container, width=8, justify="center")
            e.pack(pady=3)
            e.insert(0, "0")
            self.vector_entries.append(e)

    def _clear_result_text(self):
        self.txt_result.configure(state="normal")
        self.txt_result.delete("1.0", tk.END)
        self.txt_result.configure(state="disabled")

    def _mostrar_result_text(self, texto):
        self.txt_result.configure(state="normal")
        self.txt_result.delete("1.0", tk.END)
        self.txt_result.insert(tk.END, texto)
        self.txt_result.configure(state="disabled")

    def _format_matrix_pretty(self, M):
        if not M:
            return ""
        str_mat = [[pretty_frac(x) for x in row] for row in M]
        col_widths = [max(len(row[j]) for row in str_mat) for j in range(len(str_mat[0]))]
        lines = ["  " + "  ".join(row[j].rjust(col_widths[j]) for j in range(len(row))) for row in str_mat]
        return "\n".join(lines)

    def _pivot_info(self, A_rref):
        """Obtiene pivotes y rango."""
        n_rows = len(A_rref)
        n_cols = len(A_rref[0]) if n_rows else 0
        pivots = {}
        for i in range(n_rows):
            first_nonzero = next((j for j, val in enumerate(A_rref[i]) if val != 0), None)
            if first_nonzero is not None and A_rref[i][first_nonzero] == 1:
                pivots[first_nonzero] = i
        pivot_cols_sorted = sorted(pivots.keys())
        return pivot_cols_sorted, len(pivot_cols_sorted)

    def resolver(self):
        if not self.matrix_widget:
            messagebox.showwarning("Atención", "Primero genere la matriz.")
            return

        try:
            A = self.matrix_widget.get_matrix(parse=True)
        except Exception as e:
            messagebox.showerror("Error al leer matriz", str(e))
            return

        n = len(A)
        if any(len(row) != n for row in A):
            messagebox.showerror("Error", "La matriz debe ser cuadrada.")
            return

        A = [[to_fraction(x) for x in row] for row in A]

        # Vector b
        b_vec = None
        if self.mode.get() == "Sistema (Ax = b)":
            try:
                b_vec = [to_fraction(e.get()) for e in self.vector_entries]
            except Exception as e:
                messagebox.showerror("Error al leer vector b", str(e))
                return

        self.step_viewer.clear()

        # Paso 1: matriz aumentada [A | I]
        I = [[Fraction(1 if i == j else 0) for j in range(n)] for i in range(n)]
        A_aug = [A[i] + I[i] for i in range(n)]
        self.step_viewer.add_step("Matriz aumentada inicial [A | I]:", A_aug)

        # Paso 2: determinante
        det = determinant_gauss(A)
        self.step_viewer.add_step(f"Cálculo del determinante: det(A) = {pretty_frac(det)}", A)

        # Si determinante = 0 → no invertible
        if det == 0:
            A_rref_aug, _ = gauss_jordan(A_aug, record_steps=True)
            left_rref = [row[:n] for row in A_rref_aug]
            piv_cols, rank = self._pivot_info(left_rref)

            texto = "⚠️ Determinante = 0 → La matriz NO es invertible.\n"
            texto += "Es una matriz singular.\n\n"
            texto += f"A tiene {rank} posiciones pivote.\n"
            texto += "La ecuación Ax = 0 tiene soluciones no triviales.\n"
            texto += "Las columnas de A NO son linealmente independientes.\n"
            self._mostrar_result_text(texto)
            return

        # Paso 3: Gauss-Jordan
        A_rref_aug, pasos = gauss_jordan(A_aug, record_steps=True)
        for p in pasos:
            self.step_viewer.add_step(p["descripcion"], p["matriz"])

        left_rref = [row[:n] for row in A_rref_aug]
        inv = [row[n:] for row in A_rref_aug]
        piv_cols, rank = self._pivot_info(left_rref)

        # Paso 4: verificación A * A^-1
        product = [[sum(A[i][k] * inv[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
        self.step_viewer.add_step("Verificación final: A * A⁻¹ (debe ser la identidad)", product)

        # Resultado
        lines = []
        lines.append("✅ Determinante ≠ 0 → La matriz es invertible.\n")
        lines.append("Es una matriz no singular.\n")

        if b_vec is not None:
            # Resolver x = A^-1 * b
            x = []
            for i in range(n):
                s = Fraction(0)
                for j in range(n):
                    s += inv[i][j] * b_vec[j]
                x.append(s)
            lines.append("Solución del sistema x = A⁻¹ * b:\n")
            for idx, val in enumerate(x):
                lines.append(f"  x{idx+1} = {pretty_frac(val)}")
            lines.append("")

        lines.append("Matriz inversa A⁻¹:\n")
        lines.append(self._format_matrix_pretty(inv))
        lines.append("")
        lines.append(f"A tiene {rank} posiciones pivote.")
        if rank == n:
            lines.append("La ecuación Ax = 0 tiene solamente la solución trivial.")
            lines.append("Las columnas de A forman un conjunto linealmente independiente.")
        else:
            lines.append("La ecuación Ax = 0 tiene soluciones no triviales.")
            lines.append("Las columnas de A NO son linealmente independientes.")

        lines.append("\nVerificación A * A⁻¹:\n")
        lines.append(self._format_matrix_pretty(product))

        self._mostrar_result_text("\n".join(lines))