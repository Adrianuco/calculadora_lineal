# calculadora_lineal/gui/views/matrix/determinant_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from fractions import Fraction
from .matrix_input import MatrixInput
from ...step_viewer import StepViewer
from ....methods.matrix_mth.operations import pretty_frac, to_fraction
from ....methods.matrix_mth.determinant import metodo_cramer, regla_sarrus, determinante_cofactores, verificar_propiedades


class DeterminantView(tk.Frame):
    """Vista para calcular determinantes con diferentes métodos."""

    def __init__(self, master, controller=None, *args, **kwargs):
        super().__init__(master, bg="#0D1B2A", *args, **kwargs)
        self.controller = controller
        self.matrix_widget = None
        self.method = tk.StringVar(value="Expansión por cofactores")
        self._build_ui()

    def _build_ui(self):
        from ...theme import COLORS, FONTS

        controls = tk.Frame(self, bg=COLORS["panel"])
        controls.pack(fill="x", padx=12, pady=12)

        tk.Label(controls, text="Método:", bg=COLORS["panel"], fg=COLORS["text"], font=FONTS["normal"]).pack(side="left")
        self.combo_method = ttk.Combobox(
            controls,
            textvariable=self.method,
            values=["Método de Cramer", "Regla de Sarrus", "Expansión por cofactores"],
            state="readonly",
            width=28
        )
        self.combo_method.pack(side="left", padx=(8, 12))

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

        headers = [f"a{j+1}" for j in range(n)]
        self.matrix_widget = MatrixInput(self.matrix_container, rows=n, cols=n, include_rhs=False, col_headers=headers)
        self.matrix_widget.pack(padx=6, pady=6)

        self.step_viewer.clear()
        self._mostrar_result("")

    def calcular(self):
        if not self.matrix_widget:
            messagebox.showwarning("Atención", "Primero genere la matriz.")
            return

        try:
            A = self.matrix_widget.get_matrix(parse=True)
        except Exception as e:
            messagebox.showerror("Error al leer matriz", str(e))
            return

        A = [[to_fraction(x) for x in row] for row in A]
        metodo = self.method.get()
        self.step_viewer.clear()

        try:
            det = None
            pasos = []
            texto_final = ""

            if metodo == "Regla de Sarrus":
                result = regla_sarrus(A)
                det = result["resultado"]
                pasos = result["pasos"]
                texto_final = f"Determinante (Sarrus): {pretty_frac(det)}"

            elif metodo == "Expansión por cofactores":
                result = determinante_cofactores(A)
                det = result["resultado"]
                pasos = result["pasos"]
                texto_final = f"Determinante (Cofactores): {pretty_frac(det)}"

            else:  # Método de Cramer
                n = len(A)
                b = [Fraction(1) for _ in range(n)]
                result = metodo_cramer(A, b)
                pasos = result["pasos"]
                det = result["detA"]
                if result["resultado"]:
                    texto_final = "Soluciones (Cramer):\n" + "\n".join(
                        [f"x{i+1} = {pretty_frac(x)}" for i, x in enumerate(result["resultado"])]
                    )
                else:
                    texto_final = "No se puede aplicar Cramer (det(A)=0)."

            for p in pasos:
                self.step_viewer.add_text(p)

            if det is not None:
                if det == 0:
                    texto_final += "\n\nEl determinante es 0, por lo tanto A no es invertible (matriz singular)."
                else:
                    texto_final += "\n\nEl determinante es distinto de cero, por lo tanto A es invertible."

                texto_final += "\n" + verificar_propiedades(A, det)

            self._mostrar_result(texto_final)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _mostrar_result(self, texto):
        self.txt_result.configure(state="normal")
        self.txt_result.delete("1.0", tk.END)
        self.txt_result.insert(tk.END, texto)
        self.txt_result.configure(state="disabled")