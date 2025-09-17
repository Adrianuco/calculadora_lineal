# calculadora_lineal/main.py

import tkinter as tk
from calculadora_lineal.gui.app import AlgebraApp

def main():

    app = AlgebraApp()
    # Ejecutar el loop de Tkinter
    app.mainloop()

if __name__ == "__main__":
    main()