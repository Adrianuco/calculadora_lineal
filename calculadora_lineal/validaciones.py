def validar_entero_positivo(mensaje):
    while True:
        try:
            valor = int(input(mensaje))
            if valor <= 0:
                print("Debe ser un número entero positivo.")
                continue
            return valor
        except ValueError:
            print("Error! Debe ingresar un número entero.")

from fractions import Fraction

def validar_numero(mensaje):
    while True:
        entrada = input(mensaje)
        try:
            valor = Fraction(entrada)
            return valor
        except ValueError:
            print("Error! Debe ingresar un número real o fracción (ej: 3, -2, 1/2, 4/5).")