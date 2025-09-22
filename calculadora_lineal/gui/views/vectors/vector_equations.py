# calculadora_lineal/gui/views/vectors/vector_equations.py
import tkinter as tk
from tkinter import messagebox
from fractions import Fraction
from ....methods.vectors_mth.vector_expression_parser import evaluate_expression
from .vector_input import VectorInput
from ....gui.step_viewer import StepViewer
from ...theme import COLORS, FONTS


class VectorEquations(tk.Frame):
    def __init__(self, parent, controller=None):
        super().__init__(parent, bg=COLORS["bg"])
        self.controller = controller

        # Título
        lbl = tk.Label(
            self,
            text="Ecuaciones Vectoriales",
            font=FONTS["title"],
            bg=COLORS["bg"],
            fg=COLORS["text"]
        )
        lbl.pack(pady=10)

        # Entrada de cantidad y dimensión de vectores
        input_frame = tk.Frame(self, bg=COLORS["bg"])
        input_frame.pack(pady=5)

        tk.Label(input_frame, text="Cantidad de vectores:", bg=COLORS["bg"], fg=COLORS["text"]).grid(row=0, column=0, padx=5)
        self.entry_count = tk.Entry(input_frame, width=5)
        self.entry_count.insert(0, "2")
        self.entry_count.grid(row=0, column=1)

        tk.Label(input_frame, text="Dimensión:", bg=COLORS["bg"], fg=COLORS["text"]).grid(row=0, column=2, padx=5)
        self.entry_dim = tk.Entry(input_frame, width=5)
        self.entry_dim.insert(0, "3")
        self.entry_dim.grid(row=0, column=3)

        tk.Button(input_frame, text="Generar", command=self.generar_vectores).grid(row=0, column=4, padx=10)

        # Aquí se colocarán los inputs de los vectores
        self.vectors_frame = tk.Frame(self, bg=COLORS["bg"])
        self.vectors_frame.pack(pady=10)

        # Entrada de expresión
        expr_frame = tk.Frame(self, bg=COLORS["bg"])
        expr_frame.pack(pady=10)

        tk.Label(expr_frame, text="Expresión:", bg=COLORS["bg"], fg=COLORS["text"]).pack(side="left")
        self.entry_expr = tk.Entry(expr_frame, width=40)
        self.entry_expr.insert(0, "2*u1 + u2 - u3")  # ejemplo
        self.entry_expr.pack(side="left", padx=5)

        tk.Button(expr_frame, text="Resolver", command=self.resolver).pack(side="left")

        # Step viewer para mostrar el proceso
        self.step_viewer = StepViewer(self, height=120)
        self.step_viewer.pack(pady=10, fill="both", expand=False)

        # Resultado final
        self.result_label = tk.Label(
            self,
            text="Resultado final: ",
            font=("Segoe UI", 20, "bold"),
            fg=COLORS["accent"],
            bg=COLORS["bg"]
        )
        self.result_label.pack(pady=10)

        self.vector_inputs = {}

    def generar_vectores(self):
        for widget in self.vectors_frame.winfo_children():
            widget.destroy()

        try:
            count = int(self.entry_count.get())
            dim = int(self.entry_dim.get())
        except ValueError:
            messagebox.showerror("Error", "Ingrese valores numéricos válidos.")
            return

        self.vector_inputs = {}
        for i in range(1, count + 1):
            lbl = tk.Label(self.vectors_frame, text=f"u{i}:", bg=COLORS["bg"], fg=COLORS["text"])
            lbl.grid(row=i, column=0, padx=5, pady=5)

            vec_input = VectorInput(self.vectors_frame, dim=dim, cell_width=5)
            vec_input.grid(row=i, column=1, padx=5, pady=5)
            self.vector_inputs[f"u{i}"] = vec_input

   
    def resolver(self):
        expr = self.entry_expr.get()
        if not expr:
            messagebox.showwarning("Atención", "Ingrese una expresión vectorial.")
            return

        # Recolectamos vectores
        vectors = {}
        for name, widget in self.vector_inputs.items():
            try:
                values = widget.get_vector()
                vectors[name] = [Fraction(v) for v in values]
            except Exception:
                messagebox.showerror("Error", f"Valores inválidos en {name}")
                return

        self.step_viewer.clear()

        def pretty_frac(f):
            if isinstance(f, Fraction):
                if f.denominator == 1:
                    return str(f.numerator)
                else:
                    return f"{f.numerator}/{f.denominator}"
            elif isinstance(f, list):
                return [pretty_frac(x) for x in f]
            else:
                return str(f)

        def vec_str(vec):
            return "[" + "  ".join(pretty_frac(v) for v in vec) + "]"

        pasos = []

        # Callback compatible con evaluate_expression
        def log_step(desc, val, lhs=None):
            """
            val: resultado de la operación actual (vector ya evaluado)
            lhs: expresión original antes de calcular val, opcional
            """
            if lhs is not None:
                self.step_viewer.add_step(f"{lhs} = {vec_str(val)}", [[]])
                pasos.append((lhs, vec_str(val)))
            else:
                # solo mostrar resultado
                self.step_viewer.add_step(f"{desc} = {vec_str(val)}", [[]])

        try:
            result = evaluate_expression(expr, vectors, step_callback=log_step)

            # Mostrar operación final estilo libro
            if pasos:
                final_operacion = " + ".join(lhs for lhs, rhs in pasos)
                final_resultado = " + ".join(rhs for lhs, rhs in pasos)
                self.step_viewer.add_step(f"{final_operacion} = {final_resultado}", [[]])

            self.result_label.config(text=f"Resultado final: {vec_str(result)}")

        except Exception as e:
            messagebox.showerror("Error", str(e))