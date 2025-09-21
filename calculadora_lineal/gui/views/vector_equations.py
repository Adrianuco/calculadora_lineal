import tkinter as tk
from ..theme import COLORS, FONTS

class VectorEquations(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["panel"])
        self.controller = controller

        title = tk.Label(self, text="Ecuaciones Vectoriales", 
                         font=FONTS["title"], fg=COLORS["text"], bg=COLORS["panel"])
        title.pack(pady=20)

        tk.Label(self, text="[Pantalla para ecuaciones vectoriales tipo u - 2v]",
                 font=FONTS["normal"], fg=COLORS["muted"], bg=COLORS["panel"]).pack(pady=20)