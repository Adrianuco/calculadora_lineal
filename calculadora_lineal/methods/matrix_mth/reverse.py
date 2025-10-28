# calculadora_lineal/metodos/reverse.py
from fractions import Fraction
import copy
from .gauss_jordan import to_fraction, gauss_jordan, pretty_frac
from ..matrix_mth.gauss import determinant_gauss

def _to_fraction_matrix(A):
    """Convierte A (lista de filas) a Fraction, deep copy."""
    return [[to_fraction(x) for x in row] for row in copy.deepcopy(A)]

def _identity(n):
    return [[Fraction(1) if i==j else Fraction(0) for j in range(n)] for i in range(n)]

def _extract_right_from_augmented(aug, n):
    """Dada una matriz aumentada [n | 2n], extrae la parte derecha (n..2n-1)."""
    return [row[n:] for row in aug]

def _rref_of_A(A):
    """
    Obtiene RREF de A (sin RHS) usando gauss_jordan:
    Como gauss_jordan espera una matriz aumentada (n_cols = num_vars+1),
    añadimos una columna RHS dummy con ceros.
    Devuelve A_rref (lista de filas con Fracciones) y pasos (si los hay).
    """
    # crear A_aug = [row + [0]]
    A_copy = _to_fraction_matrix(A)
    A_aug = [row + [Fraction(0)] for row in A_copy]
    A_rref_aug, pasos = gauss_jordan(A_aug, record_steps=True)
    # quitar la última columna (RHS dummy)
    A_rref = [row[:-1] for row in A_rref_aug]
    return A_rref, pasos

def _pivot_info_from_rref(A_rref):
    """
    Dado A_rref (RREF de A, no aumentada), detecta pivotes.
    Devuelve (pivot_cols_sorted, rank)
    """
    n_rows = len(A_rref)
    n_cols = len(A_rref[0]) if n_rows else 0
    pivots = {}
    for i in range(n_rows):
        # primer índice j con A[i][j] != 0
        first_nonzero = next((j for j, val in enumerate(A_rref[i]) if val != 0), None)
        if first_nonzero is not None and A_rref[i][first_nonzero] == 1:
            pivots[first_nonzero] = i
    pivot_cols_sorted = sorted(pivots.keys())
    rank = len(pivot_cols_sorted)
    return pivot_cols_sorted, rank

def inverse_matrix(A, record_steps=True):
    """
    Calcula la inversa de A (lista de filas) y devuelve:
      inv_matrix (lista de filas con Fractions) o None si no invertible,
      steps (lista de {'descripcion','matriz'}) listo para StepViewer,
      conclusions (lista de strings) con los 3 mensajes pedidos.
    Para 2x2 usa fórmula cerrada (y registra pasos simples).
    Para n>=3 usa [A|I] + gauss_jordan sobre la aumentada.
    """
    A = _to_fraction_matrix(A)
    n = len(A)
    if any(len(row) != n for row in A):
        raise ValueError("La matriz debe ser cuadrada para calcular la inversa.")

    steps = []
    conclusions = []

    if n == 0:
        return [], [], ["Matriz vacía."]

    if n == 1:
        a = A[0][0]
        if a == 0:
            conclusions.append("Determinante = 0 → no tiene inversa.")
            return None, steps, conclusions
        inv = [[Fraction(1)/a]]
        steps.append({"descripcion": f"Determinante = {pretty_frac(a)}. Inversa trivial.", "matriz": [[a]]})
        conclusions.append("A tiene 1 posiciones pivote")
        conclusions.append("La ecuación Ax = 0 tiene solamente solución trivial.")
        conclusions.append("Las columnas de A forman un conjunto linealmente independiente.")
        return inv, steps, conclusions

    if n == 2:
        det = determinant_gauss(A)
        steps.append({"descripcion": f"Cálculo del determinante (Gauss): det = {pretty_frac(det)}", "matriz": copy.deepcopy(A)})
        if det == 0:
            conclusions.append("Determinante = 0 → la matriz NO es invertible.")
            A_rref, _ = _rref_of_A(A)
            pivot_cols, rank = _pivot_info_from_rref(A_rref)
            conclusions.append(f"A tiene {rank} posiciones pivote")
            if rank < n:
                conclusions.append("La ecuación Ax = 0 tiene soluciones no triviales.")
                conclusions.append("Las columnas de A NO son linealmente independientes.")
            return None, steps, conclusions

        a, b = A[0][0], A[0][1]
        c, d = A[1][0], A[1][1]
        inv = [
            [ d / det, -b / det ],
            [ -c / det, a / det ]
        ]
        steps.append({"descripcion": f"Aplicamos fórmula inversa 2x2 multiplicando por 1/det = 1/{pretty_frac(det)}", "matriz": copy.deepcopy(inv)})

        product = [[sum(A[i][k] * inv[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
        steps.append({"descripcion": "Verificamos A * A⁻¹ (debe dar la identidad):", "matriz": product})

        A_rref, _ = _rref_of_A(A)
        pivot_cols, rank = _pivot_info_from_rref(A_rref)
        conclusions.append(f"A tiene {rank} posiciones pivote")
        if rank == n:
            conclusions.append("La ecuación Ax = 0 tiene solamente solución trivial.")
            conclusions.append("Las columnas de A forman un conjunto linealmente independiente.")
        else:
            conclusions.append("La ecuación Ax = 0 tiene soluciones no triviales.")
            conclusions.append("Las columnas de A NO son linealmente independientes.")
        return inv, steps, conclusions

    I = _identity(n)
    A_aug = [row + I_row for row, I_row in zip(A, I)]
    A_rref_aug, gj_steps = gauss_jordan(A_aug, record_steps=record_steps)

    if record_steps:
        steps.extend(gj_steps)

    left_rref = [row[:n] for row in A_rref_aug]
    right_candidate = [row[n:] for row in A_rref_aug]

    pivot_cols, rank = _pivot_info_from_rref(left_rref)
    if rank < n:
        conclusions.append(f"A tiene {rank} posiciones pivote")
        conclusions.append("La ecuación Ax = 0 tiene soluciones no triviales.")
        conclusions.append("Las columnas de A NO son linealmente independientes.")
        steps.append({"descripcion": "La parte izquierda no pudo reducirse a la identidad → A no es invertible.", "matriz": left_rref})
        return None, steps, conclusions

    conclusions.append(f"A tiene {rank} posiciones pivote")
    conclusions.append("La ecuación Ax = 0 tiene solamente solución trivial.")
    conclusions.append("Las columnas de A forman un conjunto linealmente independiente.")

    product = [[sum(A[i][k] * right_candidate[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
    steps.append({
        "descripcion": "Verificamos A * A⁻¹ (debe dar la identidad):",
        "matriz": product
    })

    return right_candidate, steps, conclusions

def solve_system_with_inverse_2x2(A, b):
    """
    Para sistemas (A x = b) en 2x2: valida A 2x2, calcula A^{-1} y x = A^{-1} * b.
    Devuelve x (lista de Fractions), pasos (lista) y conclusions (lista).
    """
    A = _to_fraction_matrix(A)
    if len(A) != 2 or any(len(row) != 2 for row in A):
        raise ValueError("solve_system_with_inverse_2x2: A debe ser 2x2.")
    if not (isinstance(b, (list, tuple)) and len(b) == 2):
        raise ValueError("b debe ser un vector de longitud 2 (lista/tuple).")

    inv, steps, conclusions = inverse_matrix(A, record_steps=True)
    if inv is None:
        return None, steps, conclusions

    b_f = [to_fraction(x) for x in b]
    x = []
    for i in range(2):
        s = Fraction(0)
        for j in range(2):
            s += inv[i][j] * b_f[j]
        x.append(s)

    mult_mat = [
        [inv[0][0], inv[0][1], b_f[0]],
        [inv[1][0], inv[1][1], b_f[1]]
    ]
    steps.append({"descripcion": "Multiplicamos A^{-1} por b para obtener x.", "matriz": mult_mat})
    return x, steps, conclusions