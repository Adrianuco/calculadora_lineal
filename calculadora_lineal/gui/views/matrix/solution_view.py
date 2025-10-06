# calculadora_lineal/gui/views/solution_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from ...theme import COLORS, FONTS

from .matrix_input import MatrixInput
from ...step_viewer import StepViewer
from ....methods.matrix_mth.solution_set import describe_solution_set


class SolutionView(tk.Frame):
    """
    Pantalla para calcular el conjunto solución de un sistema lineal (homogéneo o no homogéneo).
    Muestra pasos de Gauss-Jordan y la descripción final del conjunto solución.
    """

    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg"])
        self.controller = controller

        # --- Título ---
        lbl_title = tk.Label(
            self,
            text="Conjunto Solución de un Sistema Lineal",
            font=("Segoe UI", 18, "bold"),
            bg=COLORS["bg"],
            fg=COLORS["fg"]
        )
        lbl_title.pack(pady=(10, 15))

        # --- Descripción corta ---
        lbl_desc = tk.Label(
            self,
            text="Ingrese la matriz aumentada del sistema (A | b).\nEl sistema puede ser homogéneo (b = 0) o no homogéneo.",
            font=("Segoe UI", 11),
            justify="center",
            bg=COLORS["bg"],
            fg=COLORS["fg"]
        )
        lbl_desc.pack(pady=(0, 15))

        # --- Selector de tamaño de matriz ---
        frm_size = tk.Frame(self, bg=COLORS["bg"])
        frm_size.pack(pady=(5, 10))

        tk.Label(frm_size, text="Filas:", bg=COLORS["bg"], fg=COLORS["fg"]).pack(side="left", padx=4)
        self.rows_var = tk.IntVar(value=3)
        spn_rows = tk.Spinbox(frm_size, from_=2, to=10, width=3, textvariable=self.rows_var)
        spn_rows.pack(side="left")

        tk.Label(frm_size, text="Columnas (sin incluir vector b):", bg=COLORS["bg"], fg=COLORS["fg"]).pack(side="left", padx=6)
        self.cols_var = tk.IntVar(value=3)
        spn_cols = tk.Spinbox(frm_size, from_=2, to=10, width=3, textvariable=self.cols_var)
        spn_cols.pack(side="left")

        btn_update = ttk.Button(frm_size, text="Actualizar matriz", command=self.update_matrix_size)
        btn_update.pack(side="left", padx=10)

        # --- Entrada de matriz ---
        self.frm_input = tk.Frame(self, bg=COLORS["bg"])
        self.frm_input.pack(pady=(5, 15))

        self.matrix_input = MatrixInput(self.frm_input, rows=3, cols=4)
        self.matrix_input.pack()

        # --- Botones de acción ---
        frm_buttons = tk.Frame(self, bg=COLORS["bg"])
        frm_buttons.pack(pady=(10, 20))

        btn_calc = ttk.Button(frm_buttons, text="Calcular conjunto solución", command=self.compute_solution)
        btn_calc.pack(side="left", padx=6)

        btn_clear = ttk.Button(frm_buttons, text="Limpiar", command=self.clear_all)
        btn_clear.pack(side="left", padx=6)

        # --- Viewer para pasos y resultados ---
        self.viewer = StepViewer(self)
        self.viewer.pack(fill="both", expand=True, padx=10, pady=10)

    # ----------------------------------------------------------------------
    def update_matrix_size(self):
        """Actualiza el tamaño de la matriz según los valores seleccionados"""
        rows = self.rows_var.get()
        cols = self.cols_var.get() + 1  # +1 por el vector b (columna aumentada)
        for widget in self.frm_input.winfo_children():
            widget.destroy()

        self.matrix_input = MatrixInput(self.frm_input, rows=rows, cols=cols)
        self.matrix_input.pack()

    # ----------------------------------------------------------------------
    def clear_all(self):
        """Limpia entradas y resultados"""
        self.matrix_input.clear()
        self.viewer.clear()

    # ----------------------------------------------------------------------
    def compute_solution(self):
        """Obtiene la matriz, calcula y muestra el conjunto solución"""
        try:
            A = self.matrix_input.get_matrix(parse=True)
        except Exception as e:
            messagebox.showerror("Error", f"Error al leer la matriz: {e}")
            return

        if not A or not A[0]:
            messagebox.showwarning("Aviso", "Ingrese una matriz válida.")
            return

        try:
            result = describe_solution_set(A, include_steps=True)
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un problema: {e}")
            return

        # limpiar resultados anteriores
        self.viewer.clear()

        # --- Mostrar pasos Gauss–Jordan ---
        if "steps" in result and result["steps"]:
            for paso in result["steps"]:
                desc = paso.get("descripcion", "")
                mat = paso.get("matriz", [])
                self.viewer.add_step(desc, mat)
            self.viewer.add_step("Matriz en forma reducida (RREF)", result["A_rref"])

        # --- Mostrar análisis final ---
        self.viewer.add_text("────────── Conjunto Solución ──────────")
        for line in result["general_solution_lines"]:
            self.viewer.add_text(line)

        # --- Si es inconsistente ---
        if not result.get("consistent", True):
            self.viewer.add_text("⚠️  El sistema es inconsistente (no tiene solución).")