# calculadora_lineal/methods/vectors_mth/linear_comb_prep.py
from fractions import Fraction
from typing import Dict, List, Tuple

def ensure_fractions(vec: List) -> List[Fraction]:
    return [Fraction(x) for x in vec]

def build_linear_combination_system(vectors: Dict[str, List], v: List) -> Tuple[List[dict], List[List[Fraction]]]:
    """
    vectors: dict con claves 'u1','u2',... -> listas numéricas
    v: lista numérica (vector objetivo)

    Retorna:
      - steps: lista de pasos; cada paso es dict {"type":"text"|"matrix", "desc": str, "matrix": optional}
      - A: matriz aumentada lista de filas con Fraction (para usar en gauss_jordan)
    """
    if not vectors:
        raise ValueError("No hay vectores provistos.")
    names = list(vectors.keys())
    k = len(names)
    dim = len(vectors[names[0]])
    for name in names:
        if len(vectors[name]) != dim:
            raise ValueError(f"Vector {name} tiene dimensión distinta.")

    if len(v) != dim:
        raise ValueError("Vector objetivo v tiene dimensión distinta.")

    # Convertir a Fracciones
    vectors_f = {n: ensure_fractions(vectors[n]) for n in names}
    v_f = ensure_fractions(v)

    steps = []
    vars_list = [f"x{j+1}" for j in range(k)]
    v_str = f"[{', '.join(str(val) for val in v)}]"

    # Paso 1: combinación lineal
    lhs = " + ".join(f"{vars_list[j]}[{', '.join(str(val) for val in vectors[names[j]])}]" for j in range(k))
    steps.append({"type": "text", "desc": f"{lhs} = {v_str}"})

    # Paso 2: productos distribuidos
    expanded = []
    for j, name in enumerate(names):
        terms = [f"{coef}{vars_list[j]}" if coef != 1 else f"{vars_list[j]}" for coef in vectors_f[name]]
        expanded.append(f"[{', '.join(terms)}]")
    steps.append({"type": "text", "desc": " + ".join(expanded) + f" = {v_str}"})

    # Paso 3: suma agrupada
    grouped = []
    for i in range(dim):
        expr_parts = []
        for j in range(k):
            coef = vectors_f[names[j]][i]
            if coef == 0:
                continue
            elif coef == 1:
                expr_parts.append(f"{vars_list[j]}")
            elif coef == -1:
                expr_parts.append(f"-{vars_list[j]}")
            else:
                expr_parts.append(f"{coef}{vars_list[j]}")
        grouped.append(" + ".join(expr_parts))
    steps.append({"type": "text", "desc": f"[{', '.join(grouped)}] = {v_str}"})

    # Paso 4: sistema de ecuaciones
    system = "\n".join(f"{grouped[i]} = {v_f[i]}" for i in range(dim))
    steps.append({"type": "text", "desc": system})

    # Paso 5: matriz aumentada
    A = []
    for i in range(dim):
        row_coeffs = [vectors_f[names[j]][i] for j in range(k)]
        rhs = v_f[i]
        row = [Fraction(c) for c in row_coeffs] + [rhs]
        A.append(row)
    steps.append({"type": "matrix", "desc": "Matriz aumentada (coeficientes | términos independientes):", "matrix": A})

    return steps, A