# calculadora_lineal/metodos/gauss_jordan.py
from fractions import Fraction
import copy

def to_fraction(x):
    """Convierte int/float/str/Fraction a Fraction. Lanza ValueError si no se puede."""
    if isinstance(x, Fraction):
        return x
    if isinstance(x, (int,)):
        return Fraction(x)
    if isinstance(x, float):
        return Fraction(x).limit_denominator()
    if isinstance(x, str):
        s = x.strip()
        # Intentar directamente (acepta "3", "2/3", "0.5")
        try:
            return Fraction(s)
        except Exception:
            try:
                return Fraction(float(s)).limit_denominator()
            except Exception:
                raise ValueError(f"Entrada inválida: {x!r}")
    raise ValueError(f"Tipo no soportado: {type(x)}")


def matrix_to_fraction(A):
    """Deep copy de A (lista de filas) convirtiendo todo a Fraction."""
    return [[to_fraction(x) for x in row] for row in copy.deepcopy(A)]


def pretty_frac(f: Fraction):
    """Formato legible para mostrar: si denom==1 -> 'n' else 'p/q'"""
    if f.denominator == 1:
        return str(f.numerator)
    return f"{f.numerator}/{f.denominator}"


def gauss_jordan(A_in, record_steps=True):
    """
    Aplica Gauss-Jordan (RREF) sobre la matriz aumentada A_in.
    A_in: lista de filas, cada fila es lista de números/strings/Fraction.
    Devuelve: A_rref (matriz de Fractions), pasos (lista) si record_steps True.
    Cada paso: {'descripcion': str, 'matriz': deep_copy_de_A}
    Este algoritmo trabaja columna por columna y maneja matrices no cuadradas.
    """
    A = matrix_to_fraction(A_in)
    pasos = []
    m = len(A)
    if m == 0:
        return (A, pasos) if record_steps else A
    n_plus1 = len(A[0])
    num_vars = n_plus1 - 1

    def snapshot(desc):
        if record_steps:
            pasos.append({"descripcion": desc, "matriz": copy.deepcopy(A)})

    row = 0
    for col in range(num_vars):
        # Buscar pivote en o debajo de 'row'
        pivot_row = None
        for r in range(row, m):
            if A[r][col] != 0:
                pivot_row = r
                break
        if pivot_row is None:
            # No hay pivote en esta columna, pasar a la siguiente
            continue

        # Intercambiar filas si es necesario
        if pivot_row != row:
            A[row], A[pivot_row] = A[pivot_row], A[row]
            snapshot(f"Intercambio fila {row+1} con fila {pivot_row+1}")

        # Normalizar pivote (hacerlo 1)
        piv = A[row][col]
        if piv != 1:
            A[row] = [x / piv for x in A[row]]
            snapshot(f"Normalizamos fila {row+1} (dividimos por {pretty_frac(piv)})")

        # Hacer ceros en toda la columna (arriba y abajo)
        for r in range(m):
            if r != row and A[r][col] != 0:
                factor = A[r][col]
                A[r] = [a - factor * b for a, b in zip(A[r], A[row])]
                snapshot(f"Fila {r+1} = Fila {r+1} - ({pretty_frac(factor)})*Fila {row+1}")

        row += 1
        if row == m:
            break

    return (A, pasos) if record_steps else A


def analyze_rref(A):
    """
    Analiza la matriz RREF (ya reducida) y determina si es:
     - inconsistente (no solución)
     - única
     - infinitas soluciones
    Devuelve dict con keys: 'tipo' in {'inconsistente','única','infinitas'},
    y datos adicionales:
      - si 'única': 'solucion' -> lista de Fractions (long = num_vars)
      - si 'infinitas': 'free_vars' (lista indices), 'expresiones' (dict var_index -> str)
    """
    m = len(A)
    if m == 0:
        return {"tipo": "única", "solucion": []}
    n_plus1 = len(A[0])
    num_vars = n_plus1 - 1

    # 1) comprobar inconsistencias: fila [0...0 | b] con b != 0
    for fila in A:
        if all(x == 0 for x in fila[:num_vars]) and fila[-1] != 0:
            return {"tipo": "inconsistente"}

    # 2) encontrar pivotes: para cada fila, el primer índice j con A[i][j] != 0
    pivots = {}
    for i in range(m):
        first_nonzero = next((j for j, val in enumerate(A[i][:num_vars]) if val != 0), None)
        if first_nonzero is not None and A[i][first_nonzero] == 1:
            pivots[first_nonzero] = i  # columna -> fila (posible pivote)

    rank = len(pivots)
    if rank == num_vars:
        # única solución: por cada variable j, la fila pivote nos da la solución
        solucion = [Fraction(0) for _ in range(num_vars)]
        for j in range(num_vars):
            i = pivots.get(j, None)
            if i is not None:
                solucion[j] = A[i][-1]
            else:
                # no debería ocurrir si rank == num_vars
                solucion[j] = Fraction(0)
        return {"tipo": "única", "solucion": solucion}

    # Infinitas soluciones: variables libres
    free = [j for j in range(num_vars) if j not in pivots]
    # construir expresiones: x_pivot = rhs - sum(coeff_free * t_k)
    expresiones = {}
    for j, i in pivots.items():
        rhs = A[i][-1]
        terms = []
        for fv in free:
            coeff = A[i][fv]
            if coeff != 0:
                terms.append((coeff, fv))  # (coef, index of free)
        # Formatear la expresión en string
        expr = pretty_frac(rhs)
        if terms:
            expr += "  "
            expr += " + ".join([f"-({pretty_frac(coeff)})*t{fv+1}" for coeff, fv in terms])
        expresiones[j] = expr

    return {"tipo": "infinitas", "free_vars": free, "expresiones": expresiones}