# calculadora_lineal/methods/multiplication.py
from fractions import Fraction
import copy


def to_fraction(x):
    """Convierte int/float/str/Fraction a Fraction."""
    if isinstance(x, Fraction):
        return x
    if isinstance(x, int):
        return Fraction(x)
    if isinstance(x, float):
        return Fraction(x).limit_denominator()
    if isinstance(x, str):
        s = x.strip()
        try:
            return Fraction(s)
        except Exception:
            return Fraction(float(s)).limit_denominator()
    raise ValueError(f"Tipo no soportado: {type(x)}")


def matrix_to_fraction(A):
    """Copia profunda convirtiendo todo a Fraction."""
    return [[to_fraction(x) for x in row] for row in copy.deepcopy(A)]


def pretty_frac(f: Fraction):
    """Formato legible para fracciones."""
    return str(f.numerator) if f.denominator == 1 else f"{f.numerator}/{f.denominator}"


def is_column_vector(mat):
    """
    Devuelve True si mat tiene exactamente una columna,
    sin importar cuántas filas tenga.
    """
    if not isinstance(mat, list) or len(mat) == 0:
        return False
    return all(isinstance(row, list) and len(row) == 1 for row in mat)


def handle_vector_warning(A, B):
    """
    Verifica si A o B son vectores columna (1 columna) y devuelve un mensaje de advertencia.
    """
    if is_column_vector(A) or is_column_vector(B):
        return "⚠️ Atención: Uno de los operandos es un vector columna (una sola columna).\n\n"
    return ""


def matrix_multiply(A_in, B_in, record_steps=True):
    """
    Multiplica dos matrices A_in y B_in (listas de listas).
    Convierte todo a Fraction, valida dimensiones y guarda los pasos si se solicita.
    Devuelve:
      - C: matriz resultado (lista de listas de Fraction)
      - pasos: lista de dicts {'descripcion': str, 'matriz': copia_de_C} si record_steps=True
    """

    """Convertir a fracciones (deep copy)"""
    A = matrix_to_fraction(A_in)
    B = matrix_to_fraction(B_in)
    pasos = []

    """Advertencia si alguno es vector columna"""
    advertencia = handle_vector_warning(A, B)
    if advertencia:
        print(advertencia, end="")  # Mostrar advertencia antes de multiplicar

    """Validar dimensiones"""
    filas_A = len(A)
    cols_A = len(A[0]) if filas_A > 0 else 0
    filas_B = len(B)
    cols_B = len(B[0]) if filas_B > 0 else 0

    if cols_A != filas_B:
        raise ValueError(
            f"No se pueden multiplicar: A es {filas_A}x{cols_A} y B es {filas_B}x{cols_B}"
        )

    """Inicializar matriz resultado con ceros"""
    C = [[Fraction(0) for _ in range(cols_B)] for _ in range(filas_A)]

    def snapshot(desc):
        """Guardar paso con descripción y copia de la matriz"""
        if record_steps:
            pasos.append({"descripcion": desc, "matriz": copy.deepcopy(C)})

    """Multiplicación: C[i][j] = sum(A[i][k] * B[k][j])"""
    for i in range(filas_A):
        for j in range(cols_B):
            suma = Fraction(0)
            detalles = []
            for k in range(cols_A):
                prod = A[i][k] * B[k][j]
                suma += prod
                detalles.append(f"({pretty_frac(A[i][k])})*({pretty_frac(B[k][j])})")
            C[i][j] = suma
            snapshot(
                f"C[{i+1}][{j+1}] = " + " + ".join(detalles) + f" = {pretty_frac(suma)}"
            )

    """Devolver resultado y pasos si se pidieron"""
    return (C, pasos) if record_steps else C