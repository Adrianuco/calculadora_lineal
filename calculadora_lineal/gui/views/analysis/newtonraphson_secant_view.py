# calculadora_lineal/gui/views/analysis/newtonraphson_secant_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from ...theme import COLORS, FONTS
from ....methods.analysis_mth.newtonraphson_secant import (
    newton_clasico,
    newton_subintervalos,
    secante,
    exportar_a_excel_newton
)
import re

def fmt(x):
    """Formato uniforme a 6 decimales."""
    if x is None:
        return ""
    try:
        return f"{float(x):.6f}"
    except:
        return str(x)

class NewtonRaphsonSecantView(tk.Frame):
    def __init__(self, master, controller=None, *args, **kwargs):
        super().__init__(master, bg=COLORS["bg"], *args, **kwargs)
        self.controller = controller

        self.current_inputs = []
        self.input_fields = {}
        self.selected_method = tk.StringVar(value="Newton Clásico")

        self.tabla_resultado = None
        self.proceso_iter = ""

        self._build_ui()

    def _build_ui(self):
        top = tk.Frame(self, bg=COLORS["panel"])
        top.pack(fill="x", padx=12, pady=12)

        tk.Label(
            top, text="Método:",
            bg=COLORS["panel"], fg=COLORS["text"],
            font=FONTS["normal"]
        ).pack(side="left")

        self.combo = ttk.Combobox(
            top,
            textvariable=self.selected_method,
            values=["Newton Clásico", "Newton por Subintervalos", "Método de la Secante"],
            state="readonly",
            width=30
        )
        self.combo.pack(side="left", padx=10)
        self.combo.bind("<<ComboboxSelected>>", self._on_method_change)

        tk.Button(
            top, text="Generar",
            bg=COLORS["accent"], fg="#062235",
            bd=0, padx=10, pady=5,
            command=self._generar_inputs
        ).pack(side="left", padx=10)

        tk.Button(
            top, text="Calcular",
            bg=COLORS["accent"], fg="#062235",
            bd=0, padx=10, pady=5,
            command=self._calcular
        ).pack(side="left")

        tk.Button(
            top, text="Exportar Excel",
            bg=COLORS["accent"], fg="#062235",
            bd=0, padx=10, pady=5,
            command=self._exportar_excel
        ).pack(side="left", padx=10)

        self.result_panel = tk.Frame(self, bg=COLORS["card"])
        self.result_panel.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        self.txt_result = tk.Text(
            self.result_panel,
            bg=COLORS["card"],
            fg=COLORS["text"],
            font=("Consolas", 14),
            wrap="word",
            bd=0,
            state="disabled",
            cursor="arrow"
        )
        self.txt_result.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        self.txt_result.bind("<Key>", lambda e: "break")
        self.txt_result.bind("<Button-1>", lambda e: "break")

        scroll = tk.Scrollbar(self.result_panel, command=self.txt_result.yview)
        self.txt_result.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")

        self.inputs_frame = tk.Frame(self, bg=COLORS["bg"])
        self.inputs_frame.pack(fill="x", padx=12, pady=12)

    def _on_method_change(self, event=None):
        self._clear_inputs()
        self._mostrar("")
        self.tabla_resultado = None

    def _clear_inputs(self):
        for w in self.current_inputs:
            w.destroy()
        self.current_inputs.clear()
        self.input_fields.clear()

    def _add_input(self, label, default=""):
        frame = tk.Frame(self.inputs_frame, bg=COLORS["bg"])
        frame.pack(anchor="w", pady=2)

        tk.Label(
            frame, text=label,
            bg=COLORS["bg"], fg=COLORS["text"],
            font=FONTS["normal"]
        ).pack(side="left", padx=6)

        ent = tk.Entry(frame, width=25)
        ent.pack(side="left")
        ent.insert(0, default)

        self.current_inputs.append(frame)
        self.input_fields[label] = ent
        return ent

    def _generar_inputs(self):
        self._clear_inputs()
        metodo = self.selected_method.get()

        self._add_input("Función f(x):")
        self._add_input("x₀ (punto inicial):")
        self._add_input("Error deseado:")

        if metodo == "Newton por Subintervalos":
            self._add_input("Límite inferior a:")
            self._add_input("Límite superior b:")
            self._add_input("Subintervalos n:")

        if metodo == "Método de la Secante":
            self._add_input("x₋₁ (valor previo):")

    def _calcular(self):
        metodo = self.selected_method.get()
        self._mostrar("")
        self.tabla_resultado = None

        try:
            funcion = self.input_fields["Función f(x):"].get()

            x0 = float(self.input_fields["x₀ (punto inicial):"].get())

            err_str = (
                self.input_fields["Error deseado:"]
                .get().replace(" ", "")
            )

            err_str = re.sub(r"10\^(-?\d+)", lambda m: str(10 ** int(m.group(1))), err_str)
            err_str = err_str.replace("^", "**")

            try:
                error = float(eval(err_str))
            except:
                raise ValueError("Error inválido. Ejemplo: 0.0001 o 10^-4")

            if metodo == "Newton Clásico":
                tabla, iters, proceso = newton_clasico(funcion, x0, error)

            elif metodo == "Método de la Secante":
                xm1 = float(self.input_fields["x₋₁ (valor previo):"].get())

                tabla, iters, proceso = secante(funcion, xm1, x0, error)

            else:
                a = float(self.input_fields["Límite inferior a:"].get())
                b = float(self.input_fields["Límite superior b:"].get())
                n = int(self.input_fields["Subintervalos n:"].get())

                if n <= 0:
                    raise ValueError("n debe ser mayor que 0")

                tabla, iters, proceso = newton_subintervalos(
                    funcion, a, b, n, x0, error
                )

            self.tabla_resultado = tabla

            texto_tabla = self._formato_tabla(tabla)
            self._mostrar(texto_tabla + "\n\n" + proceso)

        except ValueError as e:
            messagebox.showerror("Error en los datos", str(e))
        except Exception as e:
            messagebox.showerror("Error inesperado", str(e))

    def _formato_tabla(self, tabla):
        es_secante = ("xi-1" in tabla[0]) and ("f(xi-1)" in tabla[0])

        if es_secante:
            header = (
                f"{'Iteración':>10} | {'xi-1':>12} | {'xi':>12} | "
                f"{'f(xi-1)':>12} | {'f(xi)':>12} | {'xi+1':>12} | {'Ea':>12}\n"
            )
            sep = "-" * len(header)
            txt = header + sep + "\n"

            for fila in tabla:
                txt += (
                    f"{fila['Iteración']:>10} | "
                    f"{fmt(fila['xi-1']):>12} | "
                    f"{fmt(fila['xi']):>12} | "
                    f"{fmt(fila['f(xi-1)']):>12} | "
                    f"{fmt(fila['f(xi)']):>12} | "
                    f"{fmt(fila['xi+1']):>12} | "
                    f"{fmt(fila['Ea']):>12}\n"
                )

            return txt

        header = (
            f"{'Iteración':>10} | {'xi':>12} | {'xi+1':>12} | "
            f"{'Ea':>12} | {'f(xi)':>12} | {'f\'(xi)':>12}\n"
        )
        sep = "-" * len(header)
        txt = header + sep + "\n"

        for fila in tabla:
            txt += (
                f"{fila['Iteración']:>10} | "
                f"{fmt(fila['xi']):>12} | "
                f"{fmt(fila['xi+1']):>12} | "
                f"{fmt(fila['Ea']):>12} | "
                f"{fmt(fila['f(xi)']):>12} | "
                f"{fmt(fila['f\'(xi)']):>12}\n"
            )

        return txt

    def _mostrar(self, texto):
        self.txt_result.configure(state="normal")
        self.txt_result.delete("1.0", "end")
        self.txt_result.insert("1.0", texto)
        self.txt_result.configure(state="disabled")

    def _exportar_excel(self):
        try:
            if not self.tabla_resultado:
                messagebox.showwarning(
                    "Sin datos",
                    "Debe calcular antes de exportar."
                )
                return

            filename = "resultadosnewtonraphson_secant.xlsx"
            exportar_a_excel_newton(self.tabla_resultado, filename)

            messagebox.showinfo(
                "Éxito",
                f"Archivo generado: {filename}"
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))