# calculadora_lineal/methods/solutions_mth/solution_set.py
from fractions import Fraction
from typing import List, Dict, Any
from copy import deepcopy

from calculadora_lineal.methods.matrix_mth.gauss_jordan import (
    gauss_jordan,
    analyze_rref,
    matrix_to_fraction,
    pretty_frac,
)

def _vec_pretty(vec: List[Fraction]) -> str:
    """Representación legible de un vector de Fracciones: [a b c]"""
    return "[" + "  ".join(pretty_frac(v) for v in vec) + "]"

def _matrix_pretty(A: List[List[Fraction]]) -> List[List[str]]:
    """Devuelve matriz con cada entrada formateada (strings) para mostrar"""
    return [[pretty_frac(x) for x in row] for row in A]

def describe_solution_set(A_aug_in: List[List], include_steps: bool = True) -> Dict[str, Any]:
    """
    Describe el conjunto solución para una matriz aumentada A (nx(m+1)).
    La última columna se asume como b.
    """
    if not A_aug_in:
        raise ValueError("Matriz vacía.")
    
    # Convertir a fracciones
    A_aug = matrix_to_fraction(A_aug_in)
    
    n = len(A_aug)
    m_plus1 = len(A_aug[0])
    num_vars = m_plus1 - 1  # Última columna = RHS

    # Homogéneo si b = 0
    is_homogeneous = all(row[-1] == 0 for row in A_aug)

    # Gauss-Jordan
    A_rref, pasos = gauss_jordan(A_aug, record_steps=include_steps)

    # Análisis RREF
    analisis = analyze_rref(A_rref)
    inconsistent = (analisis.get("tipo") == "inconsistente")
    consistent = not inconsistent

    # Pivotes
    pivots = {}
    for i, row in enumerate(A_rref):
        first_nonzero = next((j for j, val in enumerate(row[:num_vars]) if val != 0), None)
        if first_nonzero is not None and row[first_nonzero] == 1:
            pivots[first_nonzero] = i

    pivot_cols = sorted(pivots.keys())
    free_vars = [j for j in range(num_vars) if j not in pivot_cols]
    rank = len(pivot_cols)

    if inconsistent:
        return {
            "is_homogeneous": is_homogeneous,
            "consistent": False,
            "reason": "Sistema inconsistente",
            "steps": pasos,
            "A_rref": A_rref,
            "augmented_pretty": _matrix_pretty(A_aug),
            "rref_pretty": _matrix_pretty(A_rref),
        }

    # Solución particular (variables libres = 0)
    particular = [Fraction(0) for _ in range(num_vars)]
    for col in pivot_cols:
        row_idx = pivots[col]
        particular[col] = A_rref[row_idx][-1]

    # Base del núcleo
    basis = []
    for k in free_vars:
        v = [Fraction(0) for _ in range(num_vars)]
        v[k] = Fraction(1)
        for pcol, prow in pivots.items():
            v[pcol] = -A_rref[prow][k]
        basis.append(v)

    # Construir líneas de texto
    general_lines = []
    general_lines.append("Rango r = " + str(rank))
    general_lines.append("Sistema homogéneo (b = 0)." if is_homogeneous else "Sistema no homogéneo (Ax = b).")
    if pivot_cols:
        general_lines.append("Variables básicas: " + ", ".join(f"x{c+1}" for c in pivot_cols))
    if free_vars:
        general_lines.append("Variables libres: " + ", ".join(f"x{c+1}" for c in free_vars))
    
    general_lines.append("")  # Separador

    # Caso solución única
    if not free_vars:
        sol_strs = [pretty_frac(x) for x in particular]
        general_lines.append("Solución única:")
        for i, s in enumerate(sol_strs):
            general_lines.append(f"  x{i+1} = {s}")
        general_lines.append("")
        general_lines.append("Conjunto solución: { " + "(" + ", ".join(sol_strs) + ") }")
    else:
        # Relaciones de las básicas en función de parámetros
        general_lines.append("Expresiones (variables básicas en función de parámetros):")
        for pcol in pivot_cols:
            prow = pivots[pcol]
            rhs = A_rref[prow][-1]
            parts = []
            for idx_t, free_col in enumerate(free_vars):
                coeff = -A_rref[prow][free_col]
                if coeff != 0:
                    parts.append(f"{pretty_frac(coeff)}*t{idx_t+1}")
            lhs = f"x{pcol+1}"
            rhs_str = [pretty_frac(rhs)] if rhs != 0 else []
            rhs_str.extend(parts)
            rhs_expr = " + ".join(rhs_str) if rhs_str else "0"
            general_lines.append(f"  {lhs} = {rhs_expr}")

        # Mostrar variables libres como parámetros
        general_lines.append("")
        general_lines.append("Variables libres (parámetros):")
        for idx_t, free_col in enumerate(free_vars):
            general_lines.append(f"  x{free_col+1} = t{idx_t+1}")

        # Conjunto solución final (vectorial)
        general_lines.append("")
        if any(particular):
            general_lines.append("Conjunto solución (particular + base del núcleo):")
            general_lines.append("  x = " + _vec_pretty(particular) + " + " +
                                 " + ".join(f"t{idx+1}*{_vec_pretty(v)}" for idx, v in enumerate(basis)))
        else:
            general_lines.append("Conjunto solución:")
            general_lines.append("  x = " + " + ".join(f"t{idx+1}*{_vec_pretty(v)}" for idx, v in enumerate(basis)))

    return {
        "is_homogeneous": is_homogeneous,
        "consistent": consistent,
        "num_vars": num_vars,
        "rank": rank,
        "pivot_cols": pivot_cols,
        "free_vars": free_vars,
        "particular": particular,
        "basis": basis,
        "general_solution_lines": general_lines,
        "steps": pasos if include_steps else [],
        "A_rref": A_rref,
        "augmented_pretty": _matrix_pretty(A_aug),
        "rref_pretty": _matrix_pretty(A_rref),
    }