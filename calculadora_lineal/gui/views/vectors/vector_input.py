# calculadora_lineal/gui/views/vectors/vector_input.py
import tkinter as tk

class VectorInput(tk.Frame):
    def __init__(self, master, dim=2, cell_width=5, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.dim = dim
        self.cell_width = cell_width
        self.entries = []

        for j in range(dim):
            entry = tk.Entry(self, width=self.cell_width, justify="center")
            entry.grid(row=0, column=j, padx=2, pady=2)
            self.entries.append(entry)

    def get_vector(self):
        vec = []
        for e in self.entries:
            val = e.get().strip()
            try:
                vec.append(float(val))
            except ValueError:
                vec.append(0.0)
        return vec