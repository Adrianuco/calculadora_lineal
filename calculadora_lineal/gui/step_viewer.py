# calculadora_lineal/gui/step_viewer.py
import tkinter as tk
from tkinter import ttk
from ..methods.matrix_mth.gauss_jordan import pretty_frac

class StepViewer(tk.Frame):
    """
    Panel scrollable que contiene 'tarjetas' (descripcion + matriz) para cada paso.
    """
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        # Scrollable canvas setup
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.scroll = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas)
        self.inner_id = self.canvas.create_window((0,0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scroll.pack(side="right", fill="y")
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

    def clear(self):
        for w in self.inner.winfo_children():
            w.destroy()

    def add_step(self, descripcion, matriz):
        card = tk.Frame(self.inner, bd=1, relief="groove", padx=6, pady=6)
        lbl = tk.Label(card, text=descripcion, font=("Segoe UI", 9, "bold"))
        lbl.pack(anchor="w")
        # Mostrar matriz
        mat_frame = tk.Frame(card)
        mat_frame.pack(anchor="w", pady=(4,2))
        for i, fila in enumerate(matriz):
            for j, val in enumerate(fila):
                lblv = tk.Label(mat_frame, text=pretty_frac(val), font=("Segoe UI", 9), borderwidth=0, padx=6, pady=2)
                lblv.grid(row=i, column=j, sticky="w")
        card.pack(fill="x", pady=6, padx=6)