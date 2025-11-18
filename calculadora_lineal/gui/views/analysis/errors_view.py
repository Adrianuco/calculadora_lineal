# calculadora_lineal/gui/views/analysis/errors_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from ...theme import COLORS, FONTS

from ....methods.analysis_mth.errors import (
    notacion_posicional,
    conceptos_de_error,
    ejemplos_punto_flotante,
    acumulacion_error_truncamiento,
    error_absoluto_relativo,
    propagacion_errores
)

class ErrorsView(tk.Frame):

    def __init__(self, master, controller=None, *args, **kwargs):
        super().__init__(master, bg=COLORS["bg"], *args, **kwargs)
        self.controller = controller

        self.current_inputs = []
        self.selected_method = tk.StringVar(value="Notación Posicional")
        self.input_fields = {}

        self._build_ui()

    def _build_ui(self):

        top = tk.Frame(self, bg=COLORS["panel"])
        top.pack(fill="x", padx=12, pady=12)

        tk.Label(top, text="Métodos:", bg=COLORS["panel"], fg=COLORS["text"],
                 font=FONTS["normal"]).pack(side="left")

        self.combo = ttk.Combobox(
            top,
            textvariable=self.selected_method,
            values=[
                "Notación Posicional",
                "Conceptos de Error",
                "Ejemplos Punto Flotante",
                "Acumulación Error Truncamiento",
                "Error Absoluto y Relativo",
                "Propagación de Errores"
            ],
            state="readonly",
            width=35
        )
        self.combo.pack(side="left", padx=10)
        self.combo.bind("<<ComboboxSelected>>", self._on_method_change)

        tk.Button(
            top, text="Generar", bg=COLORS["accent"], fg="#062235",
            bd=0, padx=10, pady=5,
            command=self._generar_inputs
        ).pack(side="left", padx=10)

        tk.Button(
            top, text="Calcular", bg=COLORS["accent"], fg="#062235",
            bd=0, padx=10, pady=5,
            command=self._calcular
        ).pack(side="left")

        self.result_panel = tk.Frame(self, bg=COLORS["card"])
        self.result_panel.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        self.txt_result = tk.Text(
            self.result_panel,
            bg=COLORS["card"], fg=COLORS["text"],
            font=("Consolas", 12),
            wrap="word", bd=0
        )
        self.txt_result.pack(side="left", fill="both", expand=True, padx=8, pady=8)

        scroll_r = tk.Scrollbar(self.result_panel, command=self.txt_result.yview)
        self.txt_result.configure(yscrollcommand=scroll_r.set)
        scroll_r.pack(side="right", fill="y")

        self.inputs_frame = tk.Frame(self, bg=COLORS["bg"])
        self.inputs_frame.pack(fill="x", padx=12, pady=12)

    def _on_method_change(self, event=None):
        self._clear_inputs()
        self._mostrar("")  # limpia pantalla

    def _clear_inputs(self):
        for w in self.current_inputs:
            w.destroy()
        self.current_inputs.clear()
        self.input_fields.clear()

    def _add_input(self, label, default=""):
        frame = tk.Frame(self.inputs_frame, bg=COLORS["bg"])
        frame.pack(anchor="w", pady=2)

        tk.Label(
            frame, text=label, bg=COLORS["bg"], fg=COLORS["text"],
            font=FONTS["normal"]
        ).pack(side="left", padx=6)

        ent = tk.Entry(frame, width=20)
        ent.pack(side="left")
        ent.insert(0, default)

        self.current_inputs.append(frame)
        return ent

    def _generar_inputs(self):
        self._clear_inputs()
        metodo = self.selected_method.get()

        if metodo == "Notación Posicional":
            self.input_fields["numero"] = self._add_input("Número:")

            frame_base = tk.Frame(self.inputs_frame, bg=COLORS["bg"])
            frame_base.pack(anchor="w", pady=2)

            tk.Label(frame_base, text="Base:", bg=COLORS["bg"], fg=COLORS["text"], font=FONTS["normal"]).pack(side="left", padx=6)

            base_var = tk.IntVar(value=10)
            self.input_fields["base"] = base_var

            for val in [2, 10]:
                rb = tk.Radiobutton(
                    frame_base,
                    text=str(val),
                    variable=base_var,
                    value=val,
                    bg=COLORS["bg"],
                    fg=COLORS["text"],
                    selectcolor=COLORS["accent"]
                )
                rb.pack(side="left", padx=5)

            self.current_inputs.append(frame_base)

        elif metodo == "Acumulación Error Truncamiento":
            self.input_fields["iteraciones"] = self._add_input("Iteraciones:")

        elif metodo == "Error Absoluto y Relativo":
            self.input_fields["m"] = self._add_input("Valor real m:")
            self.input_fields["m_barra"] = self._add_input("Valor aproximado m̄:")

        elif metodo == "Propagación de Errores":
            self.input_fields["funcion"] = self._add_input("Función:")
            self.input_fields["x_val"] = self._add_input("x:")
            self.input_fields["delta_x"] = self._add_input("Δx:")

        else:
            lbl = tk.Label(self.inputs_frame, text="(Este método no requiere datos)",
                        bg=COLORS["bg"], fg=COLORS["text"], font=FONTS["normal"])
            lbl.pack()
            self.current_inputs.append(lbl)

    def _calcular(self):
        metodo = self.selected_method.get()
        self._mostrar("")

        try:
            if metodo == "Notación Posicional":
                numero = self.input_fields["numero"].get()
                base = int(self.input_fields["base"].get())

                pasos, total, sumatoria = notacion_posicional(numero, base)

                text = "Notación Posicional\n\n"
                text += "\n".join(pasos)
                text += f"\n\nSumatoria:\n{sumatoria}\n"
                text += f"\nResultado final: {total}"

            elif metodo == "Conceptos de Error":
                data = conceptos_de_error()
                text = "Conceptos de Error:\n\n"
                for k, v in data.items():
                    text += f"— {k} —\n{v}\n\n"

            elif metodo == "Ejemplos Punto Flotante":
                data = ejemplos_punto_flotante()
                text = "Ejemplos en Punto Flotante:\n\n"
                for k, v in data.items():
                    text += f"{k}: {v}\n"

            elif metodo == "Acumulación Error Truncamiento":
                if "monto_1" not in self.input_fields:
                    it = int(self.input_fields["iteraciones"].get())

                    self._clear_inputs()

                    self.input_fields["iteraciones"] = self._add_input("Iteraciones:", str(it))

                    for j in range(it):
                        self.input_fields[f"monto_{j+1}"] = self._add_input(f"Monto anterior #{j+1}:")

                    return

                it = int(self.input_fields["iteraciones"].get())
                montos = [float(self.input_fields[f"monto_{j+1}"].get()) for j in range(it)]

                tabla, detalles = acumulacion_error_truncamiento(montos, it)

                header = (
                    f"{'Iteración':>10} | "
                    f"{'Monto anterior':>15} | "
                    f"{'Interés truncado':>17} | "
                    f"{'Interés real':>15} | "
                    f"{'Monto truncado':>15} | "
                    f"{'Monto real':>12} | "
                    f"{'Diferencia':>12} | "
                    f"{'Error acumulado':>17}"
                )
                sep = "-" * len(header)

                text = "Acumulación Error por Truncamiento\n\n"
                text += header + "\n" + sep + "\n"

                for row in tabla:
                    text += (
                        f"{row['Iteración']:>10} | "
                        f"{row['Monto anterior']:>15} | "
                        f"{row['Interés truncado']:>17} | "
                        f"{row['Interés real']:>15} | "
                        f"{row['Monto truncado']:>15} | "
                        f"{row['Monto real']:>12} | "
                        f"{row['Diferencia']:>12} | "
                        f"{row['Error acumulado']:>17}\n"
                    )

                text += "\nDetalles:\n"
                text += "\n".join(detalles)

                self._mostrar(text)

            elif metodo == "Error Absoluto y Relativo":
                m = float(self.input_fields["m"].get())
                m_barra = float(self.input_fields["m_barra"].get())

                res, interp = error_absoluto_relativo(m, m_barra)

                text = "Error absoluto y relativo\n\n"
                for k, v in res.items():
                    text += f"{k}: {v}\n"
                text += "\n" + interp

            elif metodo == "Propagación de Errores":
                func = self.input_fields["funcion"].get()
                x = float(self.input_fields["x_val"].get())
                dx = float(self.input_fields["delta_x"].get())

                res, interp = propagacion_errores(func, x, dx)

                text = "Propagación de errores\n\n"
                for k, v in res.items():
                    text += f"{k}: {v}\n"
                text += "\n" + interp

            else:
                text = "No implementado."

            self._mostrar(text)

        except ValueError as e:
            messagebox.showerror("Error de validación", str(e))
        except Exception as e:
            messagebox.showerror("Error inesperado", str(e))

    def _mostrar(self, text):
        self.txt_result.configure(state="normal")
        self.txt_result.delete("1.0", tk.END)
        self.txt_result.insert("1.0", text)
        self.txt_result.configure(state="disabled")