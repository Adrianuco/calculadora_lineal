# calculadora_lineal/gui/views/analysis/bisection_false_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from ...theme import COLORS, FONTS
from ....methods.analysis_mth.bisection_false import (
    biseccion,
    falsa_posicion,
    exportar_a_excel
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

class BisectionFalseView(tk.Frame):

    def __init__(self, master, controller=None, *args, **kwargs):
        super().__init__(master, bg=COLORS["bg"], *args, **kwargs)
        self.controller = controller

        self.current_inputs = []
        self.input_fields = {}
        self.selected_method = tk.StringVar(value="Bisección")

        self.tabla_resultado = None
        self.proceso_iter = ""

        self._build_ui()

    def _build_ui(self):
        top = tk.Frame(self, bg=COLORS["panel"])
        top.pack(fill="x", padx=12, pady=12)

        tk.Label(top, text="Métodos:",
                 bg=COLORS["panel"], fg=COLORS["text"],
                 font=FONTS["normal"]).pack(side="left")

        self.combo = ttk.Combobox(
            top,
            textvariable=self.selected_method,
            values=["Bisección", "Falsa Posición"],
            state="readonly",
            width=25
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

        # Panel resultados
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
        self.txt_result.bind("<Button-1>", lambda e: None)


        scroll_r = tk.Scrollbar(self.result_panel, command=self.txt_result.yview)
        self.txt_result.configure(yscrollcommand=scroll_r.set)
        scroll_r.pack(side="right", fill="y")

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

        self.input_fields["funcion"] = self._add_input(
            "Función f(x):", ""
        )
        self.input_fields["xl"] = self._add_input(
            "Límite inferior xl (xi):", ""
        )
        self.input_fields["xu"] = self._add_input(
            "Límite superior xu:", ""
        )
        self.input_fields["error"] = self._add_input(
            "Error deseado:", ""
        )

    def _calcular(self):
        metodo = self.selected_method.get()
        self._mostrar("")
        self.tabla_resultado = None
        self.proceso_iter = ""

        try:
            funcion = self.input_fields["funcion"].get()
            xl = float(self.input_fields["xl"].get())
            xu = float(self.input_fields["xu"].get())
            
            import re

            err_str = self.input_fields["error"].get().replace(" ", "")

            err_str = re.sub(r"10\^(-?\d+)", lambda m: str(10 ** int(m.group(1))), err_str)
            err_str = err_str.replace("^", "**")

            try:
                error = float(eval(err_str))
            except:
                raise ValueError("Error inválido. Intente algo como 0.0001 o 10^-4.")

            if xl >= xu:
                raise ValueError("xl debe ser menor que xu")

            if metodo == "Bisección":
                tabla, iter_needed, proceso = biseccion(funcion, xl, xu, error)
            else:
                tabla, iter_needed, proceso = falsa_posicion(funcion, xl, xu, error)

            if tabla is None:
                self.tabla_resultado = None
                self._mostrar(proceso)
                return

            self.tabla_resultado = tabla

            # TABLA
            texto_tabla = self._formato_tabla(tabla, metodo)

            # FINAL
            self._mostrar(texto_tabla + "\n\n" + proceso)

        except ValueError as e:
            messagebox.showerror("Error de validación", str(e))
        except Exception as e:
            messagebox.showerror("Error inesperado", str(e))

    def _formato_tabla(self, tabla, metodo):
        # ENCABEZADO
        if metodo == "Bisección":
            header = (
                f"{'Iteración':>10} | {'xl':>10} | {'xu':>10} | {'xr':>10} | "
                f"{'Ea':>10} | {'vl':>12} | {'vu':>12} | {'vr':>12} | {'xu - xl < E':>12}\n"
            )
        else:
            header = (
                f"{'Iteración':>10} | {'xl':>10} | {'xu':>10} | {'xr':>10} | "
                f"{'Ea':>10} | {'vl':>12} | {'vu':>12} | {'vr':>12} | {'E < Ea':>8}\n"
            )

        sep = "-" * len(header)
        texto = header + sep + "\n"

        for fila in tabla:
            if metodo == "Bisección":
                texto += (
                    f"{fila['Iteración']:>10} | "
                    f"{fmt(fila['xl']):>10} | "
                    f"{fmt(fila['xu']):>10} | "
                    f"{fmt(fila['xr']):>10} | "
                    f"{fmt(fila['Ea']):>10} | "
                    f"{fmt(fila['vl']):>12} | "
                    f"{fmt(fila['vu']):>12} | "
                    f"{fmt(fila['vr']):>12} | "
                    f"{fmt(fila['xu-xl<E']):>12}\n"
                )
            else:
                texto += (
                    f"{fila['Iteración']:>10} | "
                    f"{fmt(fila['xl']):>10} | "
                    f"{fmt(fila['xu']):>10} | "
                    f"{fmt(fila['xr']):>10} | "
                    f"{fmt(fila['Ea']):>10} | "
                    f"{fmt(fila['vl']):>12} | "
                    f"{fmt(fila['vu']):>12} | "
                    f"{fmt(fila['vr']):>12} | "
                    f"{str(fila['E<Ea']):>8}\n"
                )

        return texto

    def _mostrar(self, text):
        self.txt_result.configure(state="normal")
        self.txt_result.delete("1.0", "end")
        self.txt_result.insert("1.0", text)
        self.txt_result.configure(state="disabled")

    def _exportar_excel(self):
        try:
            if not self.tabla_resultado:
                messagebox.showwarning(
                    "Primero calcule",
                    "Debe calcular antes de exportar a Excel."
                )
                return

            filename = "bisection_false_resultados.xlsx"
            exportar_a_excel(self.tabla_resultado, filename)

            messagebox.showinfo(
                "Exportación exitosa",
                f"Archivo generado: {filename}"
            )

        except Exception as e:
            messagebox.showerror("Error", str(e))