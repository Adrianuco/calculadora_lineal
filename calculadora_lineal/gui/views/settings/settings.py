# calculadora_lineal/gui/views/settings/settings.py
import tkinter as tk
from ...theme import COLORS, FONTS

class SettingsView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg"])
        self.controller = controller  # Esto ES la ventana principal (Tk)

        title = tk.Label(
            self,
            text="Configuración",
            font=FONTS["title"],
            fg=COLORS["text"],
            bg=COLORS["bg"]
        )
        title.pack(pady=20)

        # Botón: Pantalla completa
        btn_fullscreen = tk.Button(
            self,
            text="Pantalla Completa",
            font=FONTS["normal"],
            bg=COLORS["accent"],
            fg="white",
            relief="flat",
            command=self.toggle_fullscreen
        )
        btn_fullscreen.pack(pady=10, ipadx=10, ipady=5)

        # Botón: Cerrar programa
        btn_exit = tk.Button(
            self,
            text="Cerrar Programa",
            font=FONTS["normal"],
            bg=COLORS["accent"],
            fg="white",
            relief="flat",
            command=self.close_app
        )
        btn_exit.pack(pady=10, ipadx=10, ipady=5)

    def toggle_fullscreen(self):
        """Activa o desactiva pantalla completa."""
        current = self.controller.attributes("-fullscreen")
        self.controller.attributes("-fullscreen", not current)

    def close_app(self):
        """Cierra la aplicación."""
        self.controller.quit()