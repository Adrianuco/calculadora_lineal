# calculadora_lineal/methods/solutions_mth/solution_set.py
from fractions import Fraction
from typing import List, Dict, Any, Tuple
from copy import deepcopy

# importamos tus utilidades de gauss_jordan existentes
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
    Asume que la última columna es b (términos independientes).
    Retorna un dict con claves:
      - is_homogeneous (bool)
      - consistent (bool)
      - num_vars (int)
      - rank (int)
      - pivot_cols (list[int])  # índices 0-based
      - free_vars (list[int])   # índices 0-based
      - particular (list[Fraction] | None)
      - basis (list[list[Fraction]])  # base del núcleo (nullspace)
      - general_solution (list[str])  # líneas de texto con la forma paramétrica
      - steps (list)  # pasos de gauss_jordan (si include_steps=True): cada paso {'descripcion','matriz'}
      - A_rref (matrix of Fraction)
      - augmented_pretty / rref_pretty (matrices con strings)
    """
    # Validaciones básicas
    if not A_aug_in:
        raise ValueError("Matriz vacía.")
    # convertimos a Fracciones (matrix_to_fraction hace deep copy)
    try:
        A_aug = matrix_to_fraction(A_aug_in)
    except Exception as e:
        raise ValueError(f"Error convirtiendo a fracciones: {e}")

    n = len(A_aug)
    m_plus1 = len(A_aug[0])
    if m_plus1 < 1:
        raise ValueError("Matriz con 0 columnas.")
    num_vars = m_plus1 - 1  # tratamos la última columna como RHS

    # detectar homogéneo (última columna todo 0)
    is_homogeneous = all(row[-1] == 0 for row in A_aug)

    # Gauss-Jordan (obtenemos pasos si include_steps)
    A_rref, pasos = gauss_jordan(A_aug, record_steps=include_steps)

    # analizar rref
    analisis = analyze_rref(A_rref)

    # consistencia
    inconsistent = (analisis.get("tipo") == "inconsistente")
    consistent = not inconsistent

    # detectar pivotes: map col -> row
    pivots = {}
    for i, row in enumerate(A_rref):
        first_nonzero = next((j for j, val in enumerate(row[:num_vars]) if val != 0), None)
        if first_nonzero is not None and row[first_nonzero] == 1:
            pivots[first_nonzero] = i

    pivot_cols = sorted(pivots.keys())
    free_vars = [j for j in range(num_vars) if j not in pivot_cols]
    rank = len(pivot_cols)

    # Si inconsistente y non-homogeneous => no solución
    if inconsistent:
        return {
            "is_homogeneous": is_homogeneous,
            "consistent": False,
            "reason": "Sistema inconsistente (fila 0...0 | b != 0)",
            "steps": pasos,
            "A_rref": A_rref,
            "augmented_pretty": _matrix_pretty(A_aug),
            "rref_pretty": _matrix_pretty(A_rref),
        }

    # PARTICULAR (tomando variables libres = 0)
    particular = [Fraction(0) for _ in range(num_vars)]
    for col in range(num_vars):
        if col in pivots:
            row_idx = pivots[col]
            particular[col] = A_rref[row_idx][-1]
        else:
            particular[col] = Fraction(0)

    # NULLSPACE / BASIS: por cada variable libre k construir vector v_k
    basis = []
    for k in free_vars:
        v = [Fraction(0) for _ in range(num_vars)]
        v[k] = Fraction(1)
        for pcol, prow in pivots.items():
            # x_pcol = rhs - sum_{free} coeff * t_free  => coef for t_k is -A_rref[prow][k]
            v[pcol] = -A_rref[prow][k]
        basis.append(v)

    # Construir representación textual ordenada de la solución
    general_lines = []
    # encabece
    general_lines.append("Rango r = " + str(rank))
    if is_homogeneous:
        general_lines.append("Sistema homogéneo (b = 0).")
    else:
        general_lines.append("Sistema no homogéneo (Ax = b).")

    # Variables básicas y libres (1-based para usuario)
    if pivot_cols:
        general_lines.append("Variables básicas: " + ", ".join(f"x{c+1}" for c in pivot_cols))
    else:
        general_lines.append("Variables básicas: —")
    if free_vars:
        general_lines.append("Variables libres: " + ", ".join(f"x{c+1}" for c in free_vars))
    else:
        general_lines.append("Variables libres: — (solución única)")

    # Caso solución única
    if len(free_vars) == 0:
        general_lines.append("")  # línea vacía
        general_lines.append("Solución única:")
        sol_strs = [pretty_frac(x) for x in particular]
        for i, s in enumerate(sol_strs):
            general_lines.append(f"  x{i+1} = {s}")
        # conjunto solución es {particular}
        general_lines.append("")
        general_lines.append("Conjunto solución: { " + "(" + ", ".join(sol_strs) + ") }")
    else:
        # general paramétrica
        general_lines.append("")
        # mostrar solución particular (si no homogénea) o 0 si homogénea
        if any(particular):
            part_str = "(" + ", ".join(pretty_frac(x) for x in particular) + ")"
            general_lines.append("Solución particular (todas las variables libres = 0):")
            general_lines.append("  x_particular = " + part_str)
            general_lines.append("")
        else:
            general_lines.append("Solución particular: x_particular = (0, ..., 0)")

        # mostrar relaciones de las básicas en función de parámetros t1,t2,...
        general_lines.append("")
        general_lines.append("Expresiones (variables básicas en función de parámetros):")
        # para cada variable básica x_p
        for pcol in pivot_cols:
            prow = pivots[pcol]
            rhs = A_rref[prow][-1]
            parts = []
            # coeficientes para cada libre
            for idx_t, free_col in enumerate(free_vars):
                coeff = -A_rref[prow][free_col]  # x_p = rhs + sum coeff * t_idx
                if coeff == 0:
                    continue
                # notation t1..tk
                parts.append(f"{pretty_frac(coeff)}*t{idx_t+1}")
            lhs = f"x{pcol+1}"
            rhs_str = []
            if rhs != 0:
                rhs_str.append(pretty_frac(rhs))
            if parts:
                rhs_str.extend(parts)
            if not rhs_str:
                rhs_expr = "0"
            else:
                rhs_expr = " + ".join(rhs_str)
            general_lines.append(f"  {lhs} = {rhs_expr}")

        # free vars explicit
        general_lines.append("")
        general_lines.append("Variables libres (parámetros):")
        for idx_t, free_col in enumerate(free_vars):
            general_lines.append(f"  x{free_col+1} = t{idx_t+1}")

        # vectorial: x = x_particular + sum t_i * v_i
        general_lines.append("")
        if any(particular):
            general_lines.append("Forma vectorial (particular + combinación de la base del núcleo):")
            general_lines.append("  x = " + _vec_pretty(particular) + " + " + " + ".join(f"t{idx+1}*{_vec_pretty(v)}" for idx, v in enumerate(basis)))
        else:
            general_lines.append("Forma vectorial (núcleo):")
            general_lines.append("  x = " + " + ".join(f"t{idx+1}*{_vec_pretty(v)}" for idx, v in enumerate(basis)))

    # Resultado final estructurado
    result = {
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
    return result

# Ejemplo de uso (no en el módulo, solo referencia):
# from calculadora_lineal.methods.solutions_mth.solution_set import describe_solution_set
# out = describe_solution_set([[3,5,-4,0], [-3,-2,4,0], [6,1,-8,0]])
# for line in out["general_solution_lines"]:
#     print(line)