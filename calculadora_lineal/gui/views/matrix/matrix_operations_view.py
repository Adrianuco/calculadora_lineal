# calculadora_lineal/gui/matrix_operations_view.py
import tkinter as tk
from tkinter import messagebox
from .matrix_input import MatrixInput
from ...step_viewer import StepViewer
from ....methods.matrix_mth.gauss_jordan import pretty_frac
from ....methods.matrix_mth.operations import evaluate_matrix_expression, pretty_frac

class MatrixOperationsView(tk.Frame):
    """Vista para operaciones generales con matrices (A,B,C..., escalares en la ecuación, transpuesta T)."""

    def __init__(self, master, controller=None, *args, **kwargs):
        super().__init__(master, bg="#0D1B2A", *args, **kwargs)
        self.controller = controller
        self.matrix_inputs = {}  # 'A'->MatrixInput
        self._build_ui()

    def _build_ui(self):
        from ...theme import COLORS, FONTS

        # Controles superiores
        controls = tk.Frame(self, bg=COLORS["panel"])
        controls.pack(fill="x", padx=12, pady=12)

        left = tk.Frame(controls, bg=COLORS["panel"])
        left.pack(side="left")

        tk.Label(left, text="Cantidad de matrices (A, B, C...):", fg=COLORS["text"], bg=COLORS["panel"], font=FONTS["normal"]).pack(side="left")
        self.ent_count = tk.Entry(left, width=4, justify="center", font=FONTS["normal"])
        self.ent_count.pack(side="left", padx=6)
        self.btn_gen = tk.Button(left, text="Generar matrices", font=FONTS["normal"], bg=COLORS["accent"], fg="#062235", bd=0, padx=8, pady=6, command=self.generar_matrices)
        self.btn_gen.pack(side="left", padx=(8,0))

        # Botón resolver
        actions = tk.Frame(controls, bg=COLORS["panel"])
        actions.pack(side="right")
        self.btn_resolve = tk.Button(actions, text="Resolver operación", font=FONTS["normal"], bg=COLORS["accent"], fg="#062235", bd=0, padx=12, pady=6, command=self.resolver_operacion)
        self.btn_resolve.pack(side="left", padx=6)

        # Panel principal
        main = tk.Frame(self, bg=COLORS["bg"])
        main.pack(fill="both", expand=True, padx=12, pady=8)

        self.left_col = tk.Frame(main, bg=COLORS["bg"])
        self.left_col.pack(side="left", fill="both", expand=False, padx=(0,8))

        self.mat_panel = tk.Frame(self.left_col, bg=COLORS["bg"])
        self.mat_panel.pack(fill="both", expand=False)

        # Panel ecuación (sin escalares)
        defs = tk.Frame(self.left_col, bg=COLORS["card"])
        defs.pack(fill="both", expand=False, pady=(8,0))

        lbl_expr = tk.Label(defs, text="Ecuación (ej: (2A^T + 0.5*(B*C^T))):", bg=COLORS["card"], fg=COLORS["text"])
        lbl_expr.pack(anchor="w", padx=8)
        self.ent_expr = tk.Entry(defs)
        self.ent_expr.pack(fill="x", padx=8, pady=(0,8))

        # Conclusiones
        self.conclusions_panel = tk.Frame(self.left_col, bg=COLORS["card"])
        self.conclusions_panel.pack(fill="both", expand=True, pady=(8,0))

        self.txt_conclusions = tk.Text(self.conclusions_panel, height=16, width=50, bg=COLORS["card"], fg=COLORS["text"], bd=0, wrap="word", font=("Consolas", 13))
        self.txt_conclusions.pack(side="left", fill="both", expand=True, padx=(8,0), pady=8)
        scroll_c = tk.Scrollbar(self.conclusions_panel, command=self.txt_conclusions.yview)
        self.txt_conclusions.configure(yscrollcommand=scroll_c.set)
        scroll_c.pack(side="right", fill="y", padx=(0,8), pady=8)
        self.txt_conclusions.configure(state="disabled")

        # StepViewer a la derecha
        self.right_col = tk.Frame(main, bg=COLORS["bg"])
        self.right_col.pack(side="right", fill="both", expand=True)
        self.step_viewer = StepViewer(self.right_col)
        self.step_viewer.pack(fill="both", expand=True)

    def generar_matrices(self):
        try:
            n = int(self.ent_count.get())
            if n <= 0:
                raise ValueError
            if n > 26:
                raise ValueError("Máximo 26 matrices (A..Z).")
        except Exception as e:
            messagebox.showerror("Error", f"Ingrese una cantidad válida: {e}")
            return

        for widget in self.mat_panel.winfo_children():
            widget.destroy()
        self.matrix_inputs = {}

        letters = [chr(ord("A") + i) for i in range(n)]
        for L in letters:
            frame = tk.Frame(self.mat_panel, bg="#0D1B2A")
            frame.pack(fill="x", pady=4, padx=6)

            tk.Label(frame, text=f"Matriz {L}", fg="white", bg="#0D1B2A", font=("Segoe UI", 11, "bold")).pack(side="left", padx=(0,6))

            # entradas para filas y columnas
            tk.Label(frame, text="Filas:", bg="#0D1B2A", fg="white").pack(side="left")
            ent_filas = tk.Entry(frame, width=3, justify="center")
            ent_filas.insert(0, "2")
            ent_filas.pack(side="left", padx=(2,6))

            tk.Label(frame, text="Columnas:", bg="#0D1B2A", fg="white").pack(side="left")
            ent_cols = tk.Entry(frame, width=3, justify="center")
            ent_cols.insert(0, "2")
            ent_cols.pack(side="left", padx=(2,6))

            # botón aplicar tamaño
            def aplicar_tam(eL=L, ef=ent_filas, ec=ent_cols):
                try:
                    r = int(ef.get())
                    c = int(ec.get())
                    if r <= 0 or c <= 0:
                        raise ValueError
                except Exception:
                    messagebox.showerror("Error", "Tamaño inválido.")
                    return

                mi = self.matrix_inputs[eL]

                # --- simulamos set_size sin tocar MatrixInput ---
                old_vals = [[mi.entries[i][j].get() for j in range(mi.total_cols)] for i in range(mi.rows)]

                # borrar todos los entries
                for fila in mi.entries:
                    for e in fila:
                        e.destroy()

                mi.rows = r
                mi.cols = c
                mi.total_cols = c + (1 if mi.include_rhs else 0)
                mi.entries = []

                start_row = 1 if mi.col_headers else 0
                if mi.col_headers:
                    for j, h in enumerate(mi.col_headers[:mi.total_cols]):
                        lbl = tk.Label(mi, text=str(h), font=("Segoe UI", 9, "bold"))
                        lbl.grid(row=0, column=j, padx=4, pady=2)

                for i in range(r):
                    fila_entries = []
                    for j in range(mi.total_cols):
                        e = tk.Entry(mi, width=10)
                        e.grid(row=start_row + i, column=j, padx=3, pady=3)
                        if i < len(old_vals) and j < len(old_vals[0]):
                            e.insert(0, old_vals[i][j])
                        fila_entries.append(e)
                    mi.entries.append(fila_entries)

            btn_aplicar = tk.Button(frame, text="Aceptar", bg="#1B263B", fg="white", font=("Segoe UI", 9), command=aplicar_tam)
            btn_aplicar.pack(side="left", padx=(4,0))

            # MatrixInput debajo
            mi = MatrixInput(self.mat_panel, rows=2, cols=2, include_rhs=False)
            mi.pack(pady=2, padx=12)
            self.matrix_inputs[L] = mi

        self.step_viewer.clear()
        self.txt_conclusions.configure(state="normal")
        self.txt_conclusions.delete("1.0", tk.END)
        self.txt_conclusions.configure(state="disabled")

    def resolver_operacion(self):
        if not self.matrix_inputs:
            messagebox.showwarning("Atención", "Primero genera las matrices.")
            return

        matrices = {}
        try:
            for name, mi in self.matrix_inputs.items():
                matrices[name] = mi.get_matrix(parse=True)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer matrices: {e}")
            return

        expr = self.ent_expr.get().strip()

        self.step_viewer.clear()
        self.txt_conclusions.configure(state="normal")
        self.txt_conclusions.delete("1.0", tk.END)

        try:
            result, steps = evaluate_matrix_expression(expr, matrices)
        except Exception as e:
            self.txt_conclusions.insert(tk.END, f"⚠️ {e}\n")
            self.txt_conclusions.configure(state="disabled")
            return

        # --- Mostrar pasos en el panel derecho ---
        for st in steps:
            desc = st.get("descripcion", "")
            mat = st.get("matriz", [])
            self.step_viewer.add_step(desc, mat)

        # --- Mostrar solo el resultado final en el panel inferior ---
        self.txt_conclusions.insert(tk.END, "Resultado final:\n\n")
        for row in result:
            self.txt_conclusions.insert(
                tk.END, "  " + "  ".join(pretty_frac(x) for x in row) + "\n"
            )

        self.txt_conclusions.configure(state="disabled")