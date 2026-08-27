# calculadora_lineal/methods/matrix_mth/gauss.py
from fractions import Fraction
import copy

def to_fraction(x):
    """Convierte cualquier número o string a Fraction."""
    if isinstance(x, Fraction):
        return x
    try:
        return Fraction(x)
    except Exception:
        return Fraction(str(x))

def determinant_gauss(A):
    """
    Calcula el determinante de una matriz cuadrada A usando eliminación de Gauss
    (método por triangulación superior).
    Retorna Fraction.
    """
    A = [[to_fraction(x) for x in row] for row in copy.deepcopy(A)]
    n = len(A)
    if any(len(row) != n for row in A):
        raise ValueError("Determinante (Gauss): la matriz debe ser cuadrada.")
    if n == 0:
        return Fraction(1)

    det = Fraction(1)
    swap_count = 0

    for i in range(n):
        # Buscar pivote distinto de 0
        pivot_row = None
        for r in range(i, n):
            if A[r][i] != 0:
                pivot_row = r
                break

        # Si no hay pivote, determinante = 0
        if pivot_row is None:
            return Fraction(0)

        # Si hay intercambio de filas, cambia el signo del determinante
        if pivot_row != i:
            A[i], A[pivot_row] = A[pivot_row], A[i]
            swap_count += 1

        pivot = A[i][i]
        det *= pivot

        # Eliminar elementos debajo del pivote
        for r in range(i + 1, n):
            if A[r][i] == 0:
                continue
            factor = A[r][i] / pivot
            for c in range(i, n):
                A[r][c] -= factor * A[i][c]

    # Ajuste de signo si hubo intercambios
    if swap_count % 2 == 1:
        det *= -1

    return det