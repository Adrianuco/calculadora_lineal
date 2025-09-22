import tkinter as tk
from ..methods.matrix_mth.gauss_jordan import pretty_frac

class StepViewer(tk.Frame):
    """
    Panel scrollable que contiene 'tarjetas' (descripcion + matriz) para cada paso.
    Cada tarjeta está centrada dentro del scrollable.
    """
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        # Canvas + scrollbar
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.scroll = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scroll.set)

        self.scroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Frame interno donde estarán las tarjetas
        self.inner = tk.Frame(self.canvas)
        self.inner_id = self.canvas.create_window((0,0), window=self.inner, anchor="n")
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Configuración para centrar los widgets con grid
        self.inner.grid_columnconfigure(0, weight=1)

    def clear(self):
        for w in self.inner.winfo_children():
            w.destroy()

    def add_step(self, descripcion, matriz):
        card = tk.Frame(self.inner, bd=1, relief="groove", padx=6, pady=6)
        card.grid(row=len(self.inner.winfo_children()), column=0, pady=6, sticky="n")  # columna única, centrada

        lbl = tk.Label(card, text=descripcion, font=("Segoe UI", 12, "bold"))
        lbl.pack(anchor="center")

        mat_frame = tk.Frame(card)
        mat_frame.pack(anchor="center", pady=(4,2))
        for i, fila in enumerate(matriz):
            for j, val in enumerate(fila):
                lblv = tk.Label(mat_frame, text=pretty_frac(val), font=("Segoe UI", 12), borderwidth=0, padx=6, pady=2)
                lblv.grid(row=i, column=j, sticky="nsew")

    def add_text(self, text):
        card = tk.Frame(self.inner, bd=1, relief="groove", padx=6, pady=6)
        card.grid(row=len(self.inner.winfo_children()), column=0, pady=6, sticky="n")  # columna única, centrada

        lbl = tk.Label(card, text=text, font=("Segoe UI", 12, "bold"))
        lbl.pack(anchor="center")