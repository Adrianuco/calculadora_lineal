from fractions import Fraction
import sys
import os

# Agrega la carpeta algebra_lineal al path de Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import validaciones as val

def print_matrix(A):
    for fila in A:
        print([str(x) for x in fila])
    print()

def mostrar_solucion(A, num_vars):
    n = len(A)

    # 1) Inconsistencia: [0 ... 0 | b!=0]
    for fila in A:
        if all(x == 0 for x in fila[:num_vars]) and fila[-1] != 0:
            print("\nEl sistema no tiene solución (inconsistente)\n")
            return

    # 2) Identificar columnas pivote (un 1 y ceros en el resto de la columna)
    pivot_cols = []
    pivot_row_of = {}
    for j in range(num_vars):
        ones = [i for i in range(n) if A[i][j] == 1]
        if len(ones) == 1 and all(A[i][j] == 0 for i in range(n) if i != ones[0]):
            pivot_cols.append(j)
            pivot_row_of[j] = ones[0]

    # 3) Única solución: pivotes == num_vars
    if len(pivot_cols) == num_vars:
        sol = [0]*num_vars
        for j in pivot_cols:
            i = pivot_row_of[j]
            sol[j] = A[i][-1]
        print("\nEl sistema tiene solución única:\n")
        for k, val in enumerate(sol, start=1):
            print(f"x{k} = {val}")
        print()
        return

    # 4) Infinitas soluciones: variables libres = columnas sin pivote
    free_cols = [j for j in range(num_vars) if j not in pivot_cols]
    print("\nEl sistema tiene infinitas soluciones (hay variables libres).")
    if not free_cols:
        print()
        return

    # Expresar las básicas en función de parámetros t1, t2, ...
    params = {col: f"t{idx+1}" for idx, col in enumerate(free_cols)}

    for j in range(num_vars):
        if j in free_cols:
            print(f"x{j+1} = {params[j]}")
        else:
            i = pivot_row_of[j]
            expr = f"{A[i][-1]}"
            # En RREF, los únicos posibles no-cero fuera del pivote están en columnas libres
            for col in free_cols:
                coef = -A[i][col]
                if coef != 0:
                    sign = " + " if coef > 0 else " - "
                    coef_abs = coef if coef > 0 else -coef
                    if coef_abs == 1:
                        expr += f"{sign}{params[col]}"
                    else:
                        expr += f"{sign}{coef_abs}*{params[col]}"
            print(f"x{j+1} = {expr}")
    print()

def gauss_jordan(A):
    n = len(A)                 # filas (ecuaciones)
    num_vars = len(A[0]) - 1   # variables (sin la columna b)

    print("\n\n-- Proceso de Gauss-Jordan --")
    print("\n\nMatriz inicial:\n")
    print_matrix(A)

    fila = 0  # siguiente fila donde queremos poner el pivote
    for col in range(num_vars):
        if fila >= n:
            break

        # 1) Buscar una fila con A[r][col] != 0 a partir de 'fila'
        piv = None
        for r in range(fila, n):
            if A[r][col] != 0:
                piv = r
                break
        if piv is None:
            # no hay pivote en esta columna; pasamos a la siguiente columna
            continue

        # 2) Subir esa fila a la posición 'fila'
        if piv != fila:
            A[fila], A[piv] = A[piv], A[fila]
            print(f"\n\nIntercambio fila {fila+1} con fila {piv+1}\n")
            print_matrix(A)

        # 3) Normalizar el pivote a 1
        pivote = A[fila][col]
        if pivote != 1:
            A[fila] = [x / pivote for x in A[fila]]
            print(f"\n\nNormalizamos fila {fila+1} (dividimos por {pivote})\n")
            print_matrix(A)

        # 4) Hacer ceros arriba y abajo en esta columna
        for r in range(n):
            if r != fila and A[r][col] != 0:
                factor = A[r][col]
                A[r] = [xr - factor * xf for xr, xf in zip(A[r], A[fila])]
                print(f"\n\nFila {r+1} = Fila {r+1} - ({factor})*Fila {fila+1}\n")
                print_matrix(A)

        # 5) Avanzar a la siguiente fila para el próximo pivote
        fila += 1

    return A

def ingresar_matriz():
    print("\n-- Definir Matriz --")
    n = val.validar_entero_positivo("\nNúmero de filas (ecuaciones): ")
    m = val.validar_entero_positivo("Número de columnas (variables): ")

    A = []
    print("\n\n-- Ingreso de Datos --")
    for i in range(n):
        fila = []
        print(f"\n\nIngrese los {m} coeficientes y el término independiente para la fila {i+1}:\n")
        for j in range(m + 1):
            valor = val.validar_numero(f"  Elemento [{i+1},{j+1}]: ")
            fila.append(valor)
        A.append(fila)

    return A

print("\n\n--- METODO DE GAUSS-JORDAN ---\n")


A = ingresar_matriz()

resultado = gauss_jordan(A)
print("Matriz final (identidad | soluciones)")
print_matrix(resultado)

print("\n\n-- Resultados --\n")
mostrar_solucion(resultado, len(A[0]) - 1)