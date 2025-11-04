import tkinter as tk
from tkinter import ttk, messagebox
from fractions import Fraction
from copy import deepcopy
from .matrix_input import MatrixInput
from ...step_viewer import StepViewer
from ....methods.matrix_mth.operations import pretty_frac, to_fraction
from ....methods.matrix_mth.determinant import metodo_cramer, regla_sarrus, determinante_cofactores, verificar_propiedades


class ReadOnlyMatrix(tk.Frame):
    """Muestra una matriz con estilo similar a MatrixInput pero sin edición."""

    def __init__(self, master, matrix, col_headers=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.matrix = matrix
        self.col_headers = col_headers
        self._build()

    def _build(self):
        for widget in self.winfo_children():
            widget.destroy()

        total_cols = len(self.matrix[0]) if self.matrix else 0
        if self.col_headers:
            for j, h in enumerate(self.col_headers[:total_cols]):
                lbl = tk.Label(self, text=str(h), font=("Segoe UI", 9, "bold"),
                               bg="#1B263B", fg="white", borderwidth=1, relief="solid",
                               width=10, anchor="center")
                lbl.grid(row=0, column=j, padx=1, pady=1)
            start_row = 1
        else:
            start_row = 0

        for i, fila in enumerate(self.matrix):
            for j, val in enumerate(fila):
                lbl = tk.Label(self, text=pretty_frac(val),
                               bg="#0D1B2A", fg="white", borderwidth=1, relief="solid",
                               width=10, anchor="center", font=("Segoe UI", 10))
                lbl.grid(row=start_row + i, column=j, padx=1, pady=1)


class DeterminantView(tk.Frame):
    """Vista para calcular determinantes con diferentes métodos."""

    def __init__(self, master, controller=None, *args, **kwargs):
        super().__init__(master, bg="#0D1B2A", *args, **kwargs)
        self.controller = controller
        self.matrix_widget = None
        self.vector_b_widget = None
        self.method = tk.StringVar(value="Expansión por Cofactores")
        self._build_ui()

    def _build_ui(self):
        from ...theme import COLORS, FONTS

        controls = tk.Frame(self, bg=COLORS["panel"])
        controls.pack(fill="x", padx=12, pady=12)

        tk.Label(controls, text="Método:", bg=COLORS["panel"], fg=COLORS["text"], font=FONTS["normal"]).pack(side="left")
        self.combo_method = ttk.Combobox(
            controls,
            textvariable=self.method,
            values=["Método de Cramer", "Regla de Sarrus", "Expansión por Cofactores"],
            state="readonly",
            width=28
        )
        self.combo_method.pack(side="left", padx=(8, 12))
        self.combo_method.bind("<<ComboboxSelected>>", self._on_method_change)

        tk.Label(controls, text="n (n×n):", bg=COLORS["panel"], fg=COLORS["text"], font=FONTS["normal"]).pack(side="left")
        self.ent_n = tk.Entry(controls, width=4, justify="center")
        self.ent_n.pack(side="left", padx=(4, 12))
        self.ent_n.insert(0, "3")

        tk.Button(controls, text="Generar matriz", bg=COLORS["accent"], fg="#062235",
                  bd=0, padx=10, pady=5, font=FONTS["normal"],
                  command=self.generar_matriz).pack(side="left", padx=6)
        tk.Button(controls, text="Calcular", bg=COLORS["accent"], fg="#062235",
                  bd=0, padx=10, pady=5, font=FONTS["normal"],
                  command=self.calcular).pack(side="left", padx=6)

        main = tk.Frame(self, bg=COLORS["bg"])
        main.pack(fill="both", expand=True, padx=12, pady=8)

        left = tk.Frame(main, bg=COLORS["bg"])
        left.pack(side="left", fill="both", expand=False, padx=(0, 8))

        self.matrix_container = tk.Frame(left, bg=COLORS["bg"])
        self.matrix_container.pack(pady=8)

        self.vector_b_container = tk.Frame(left, bg=COLORS["bg"])
        self.vector_b_container.pack(pady=8)

        self.result_panel = tk.Frame(left, bg=COLORS["card"])
        self.result_panel.pack(fill="both", expand=True)
        self.txt_result = tk.Text(self.result_panel, height=18, width=52, bg=COLORS["card"],
                                  fg=COLORS["text"], bd=0, wrap="word", font=("Consolas", 12))
        self.txt_result.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        scroll_r = tk.Scrollbar(self.result_panel, command=self.txt_result.yview)
        self.txt_result.configure(yscrollcommand=scroll_r.set)
        scroll_r.pack(side="right", fill="y")

        right = tk.Frame(main, bg=COLORS["bg"])
        right.pack(side="right", fill="both", expand=True)
        self.step_viewer = StepViewer(right)
        self.step_viewer.pack(fill="both", expand=True)

    def _on_method_change(self, event=None):
        metodo = self.method.get()
        if metodo == "Regla de Sarrus":
            self.ent_n.delete(0, tk.END)
            self.ent_n.insert(0, "3")
            self.ent_n.config(state="disabled")
        else:
            self.ent_n.config(state="normal")

    def generar_matriz(self):
        try:
            n = int(self.ent_n.get())
            if n <= 0:
                raise ValueError
            if self.method.get() == "Regla de Sarrus" and n != 3:
                raise ValueError("La Regla de Sarrus solo aplica para matrices 3x3.")
        except Exception as e:
            messagebox.showerror("Error", f"Ingrese un tamaño válido: {e}")
            return

        for widget in self.matrix_container.winfo_children():
            widget.destroy()
        for widget in self.vector_b_container.winfo_children():
            widget.destroy()
        self.matrix_widget = None
        self.vector_b_widget = None

        col_headers = [f"a{j+1}" for j in range(n)]

        if self.method.get() == "Método de Cramer":
            frame = tk.Frame(self.matrix_container, bg="#0D1B2A")
            frame.pack()
            self.matrix_widget = MatrixInput(frame, rows=n, cols=n, include_rhs=False, col_headers=col_headers)
            self.matrix_widget.pack(side="left", padx=(0, 6), pady=6)

            self.vector_b_widget = MatrixInput(frame, rows=n, cols=1, include_rhs=False, col_headers=["b"])
            self.vector_b_widget.pack(side="left", padx=(6,0), pady=6)
        else:
            self.matrix_widget = MatrixInput(self.matrix_container, rows=n, cols=n, include_rhs=False, col_headers=col_headers)
            self.matrix_widget.pack(pady=6)

        self.step_viewer.clear()
        self._mostrar_result("")

    def calcular(self):
        if not self.matrix_widget:
            messagebox.showwarning("Atención", "Primero genere la matriz.")
            return

        try:
            A = self.matrix_widget.get_matrix(parse=True)
            n = len(A)
            metodo = self.method.get()

            if metodo == "Método de Cramer":
                if not self.vector_b_widget:
                    messagebox.showerror("Error", "Vector b no generado.")
                    return
                b = self.vector_b_widget.get_matrix(parse=True)
                b = [row[0] for row in b]
                if len(b) != n:
                    messagebox.showerror("Error", "Vector b tiene tamaño incompatible.")
                    return
            else:
                b = None

            A = [[to_fraction(x) for x in row] for row in A]
            if b:
                b = [to_fraction(x) for x in b]

        except Exception as e:
            messagebox.showerror("Error al leer matriz/vector", str(e))
            return

        self.step_viewer.clear()
        self.txt_result.configure(state="normal")
        self.txt_result.delete("1.0", tk.END)

        try:
            if metodo == "Regla de Sarrus":
                resultado = regla_sarrus(A, step_viewer=self.step_viewer)
                det = resultado["resultado"]

            elif metodo == "Expansión por Cofactores":
                resultado = determinante_cofactores(A, step_viewer=self.step_viewer)
                det = resultado["resultado"]

            else:  # Método de Cramer
                resultado = metodo_cramer(A, b, step_viewer=self.step_viewer)
                det = resultado["detA"]

            texto_result = []
            texto_result.append("Resultado Final:\n")
            texto_result.append(f"|A| = {pretty_frac(det)}")
            if det == 0:
                texto_result.append("La matriz es singular (no invertible).")
            else:
                texto_result.append("La matriz es no singular (invertible).")
            if det == 0:
                pass
            else:
                texto_result.append("\n" + verificar_propiedades(A, det))
            self._mostrar_result("\n".join(texto_result))

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _mostrar_result(self, texto):
        self.txt_result.configure(state="normal")
        self.txt_result.delete("1.0", tk.END)
        self.txt_result.insert(tk.END, texto)
        self.txt_result.configure(state="disabled")