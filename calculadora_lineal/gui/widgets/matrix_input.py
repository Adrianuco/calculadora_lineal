# calculadora_lineal/gui/widgets/matrix_input.py
import tkinter as tk
from tkinter import ttk
from fractions import Fraction
from ...metodos.gauss_jordan import to_fraction

class MatrixInput(tk.Frame):
    def __init__(self, master, rows, cols, include_rhs=True, col_headers=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.rows = rows
        self.cols = cols
        self.include_rhs = include_rhs
        self.total_cols = cols + (1 if include_rhs else 0)
        self.entries = []  # lista de filas -> lista de Entry
        self.col_headers = col_headers
        self._build()

    def _build(self):
        # Encabezados de columna si vienen
        if self.col_headers:
            for j, h in enumerate(self.col_headers[:self.total_cols]):
                lbl = tk.Label(self, text=str(h), font=("Segoe UI", 9, "bold"))
                lbl.grid(row=0, column=j, padx=4, pady=2)
            start_row = 1
        else:
            start_row = 0

        for i in range(self.rows):
            fila_entries = []
            for j in range(self.total_cols):
                e = tk.Entry(self, width=10)
                e.grid(row=start_row + i, column=j, padx=3, pady=3)
                fila_entries.append(e)
            self.entries.append(fila_entries)

    def get_matrix(self, parse=True):
        """
        Devuelve A como lista de filas.
        Si parse=True, convierte las entradas a Fraction (usando to_fraction).
        """
        A = []
        for i in range(self.rows):
            fila = []
            for j in range(self.total_cols):
                val = self.entries[i][j].get().strip()
                if val == "":
                    val = "0"
                if parse:
                    fila.append(to_fraction(val))
                else:
                    fila.append(val)
            A.append(fila)
        return A
    
    def clear(self):
        for row in self.entries:
            for e in row:
                e.delete(0, tk.END)