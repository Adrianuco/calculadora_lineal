# calculadora_lineal/methods/vectors_mth/dependency.py
from fractions import Fraction
from ..matrix_mth.gauss_jordan import gauss_jordan, matrix_to_fraction, to_fraction

def fmt(val):
    """Formatea números o fracciones para mostrar en textos."""
    if isinstance(val, Fraction):
        if val.denominator == 1:
            return str(val.numerator)
        return f"{val.numerator}/{val.denominator}"
    return str(val)

def check_vector_dependency(vectors):
    pasos = []
    n = len(vectors)
    if n == 0:
        return [], "independientes"

    m = len(vectors[0])
    matriz = [list(col) for col in zip(*vectors)]
    vars_str = [chr(97 + i) for i in range(n)]  # a, b, c, d...

    # Combinación general
    comb = " + ".join(f"{vars_str[i]}v{i+1}" for i in range(n))
    pasos.append({"titulo": "Solución:", "desc": f"{comb} = 0"})

    # Combinación con valores
    combo_desc = " + ".join(
        f"{vars_str[i]}({', '.join(fmt(v) for v in vectors[i])})"
        for i in range(n)
    )
    zero_tuple = "(" + ", ".join(["0"]*m) + ")"
    pasos.append({"desc": f"Formamos la combinación lineal:\n{combo_desc} = {zero_tuple}"})

    # Sistema de ecuaciones
    eqs = []
    for i in range(m):
        ecu = " + ".join(f"{vars_str[j]}({fmt(vectors[j][i])})" for j in range(n))
        eqs.append(f"Ec. {i+1}: {ecu} = 0")
    pasos.append({"desc": "De aquí:\n" + "\n".join(eqs)})

    # Gauss-Jordan
    pasos.append({"titulo": "Resolución en Gauss-Jordan:"})
    A = matrix_to_fraction(matriz)
    A_ext = [row + [Fraction(0)] for row in A]
    A_rref, gauss_steps = gauss_jordan(A_ext)

    for step in gauss_steps:
        step_matrix = step.get("matriz", [])
        step_matrix_frac = [
            [to_fraction(el) for el in row] for row in step_matrix
        ]
        pasos.append({
            "desc": step.get("descripcion", ""),
            "matrix": step_matrix_frac
        })

    # Conjunto Solución
    conjunto_solucion = ", ".join(f"{var} = 0" for var in vars_str)
    pasos.append({"titulo": "Conjunto Solución:", "desc": conjunto_solucion})

    # Conclusión
    rank = sum(any(el != 0 for el in row[:-1]) for row in A_rref)
    conclusion = "independientes" if rank == n else "dependientes"

    pasos.append({
        "desc": (
            "Indica que los vectores son linealmente independientes (solución trivial)."
            if conclusion == "independientes"
            else "Indica que los vectores son linealmente dependientes (infinitas soluciones)."
        )
    })

    return pasos, conclusion

def check_matrix_dependency(matrices):
    pasos = []
    n = len(matrices)
    if n == 0:
        return [], "independientes"

    # Aplanar matrices y generar columnas
    flat_mats = [sum(mat, []) for mat in matrices]
    m = len(flat_mats[0])
    matriz = [list(col) for col in zip(*flat_mats)]
    vars_str = [chr(97 + i) for i in range(n)]

    pasos.append({"titulo": "Solución:", "desc": " + ".join(f"{vars_str[i]}M{i+1}" for i in range(n)) + " = 0"})

    combo_desc = " + ".join(
        f"{vars_str[i]}({'; '.join(', '.join(fmt(v) for v in row) for row in matrices[i])})"
        for i in range(n)
    )
    pasos.append({"desc": f"Formamos la combinación lineal:\n{combo_desc} = 0"})

    pasos.append({"titulo": "Resolución en Gauss-Jordan:"})
    A = matrix_to_fraction(matriz)
    A_ext = [row + [Fraction(0)] for row in A]
    A_rref, gauss_steps = gauss_jordan(A_ext)

    for step in gauss_steps:
        step_matrix = step.get("matriz", [])
        step_matrix_frac = [
            [to_fraction(el) for el in row] for row in step_matrix
        ]
        pasos.append({
            "desc": step.get("descripcion", ""),
            "matrix": step_matrix_frac
        })

    rank = sum(any(el != 0 for el in row[:-1]) for row in A_rref)
    conclusion = "independientes" if rank == n else "dependientes"

    pasos.append({
        "desc": (
            "Indica que las matrices son linealmente independientes (solución trivial)."
            if conclusion == "independientes"
            else "Indica que las matrices son linealmente dependientes (infinitas soluciones)."
        )
    })

    return pasos, conclusion

def fmt(val):
    if isinstance(val, Fraction):
        if val.denominator == 1:
            return str(val.numerator)
        return f"{val.numerator}/{val.denominator}"
    return str(val)

def parse_polynomial(expr):
    expr = expr.replace(" ", "").replace("-", "+-")
    terms = [t for t in expr.split("+") if t]
    coef_dict = {}
    for term in terms:
        if "x" not in term:
            coef = Fraction(term)
            exp = 0
        else:
            if "^" in term:
                base, exp_str = term.split("^")
                exp = int(exp_str)
            else:
                base = term
                exp = 1
            base = base.replace("x", "")
            if base in ("", "+"):
                coef = Fraction(1)
            elif base == "-":
                coef = Fraction(-1)
            else:
                coef = Fraction(base)
        coef_dict[exp] = coef_dict.get(exp, Fraction(0)) + coef
    max_exp = max(coef_dict.keys()) if coef_dict else 0
    coeffs = [coef_dict.get(i, Fraction(0)) for i in range(max_exp, -1, -1)]
    return coeffs

def check_polynomial_dependency(polynomials):
    pasos = []
    n = len(polynomials)
    if n == 0:
        return [], "independientes"

    # Convertir polinomios a coeficientes
    processed = []
    for p in polynomials:
        expr = p.replace(" ", "").replace("-", "+-")
        terms = [t for t in expr.split("+") if t]
        max_exp = 0
        coef_dict = {}
        for term in terms:
            if "x" not in term:
                coef = Fraction(term)
                exp = 0
            else:
                if "^" in term:
                    base, exp_str = term.split("^")
                    exp = int(exp_str)
                else:
                    base = term
                    exp = 1
                base = base.replace("x", "")
                if base in ("", "+"):
                    coef = Fraction(1)
                elif base == "-":
                    coef = Fraction(-1)
                else:
                    coef = Fraction(base)
            coef_dict[exp] = coef_dict.get(exp, Fraction(0)) + coef
            if exp > max_exp:
                max_exp = exp
        coeffs = [coef_dict.get(i, Fraction(0)) for i in range(max_exp, -1, -1)]
        processed.append(coeffs)

    # Alinear longitudes
    max_len = max(len(p) for p in processed)
    for p in processed:
        p += [Fraction(0)] * (max_len - len(p))

    # Formar matriz aumentada
    A = [[processed[j][i] for j in range(n)] + [Fraction(0)] for i in range(max_len)]

    # Combinación lineal paso inicial
    vars_str = [chr(97 + i) for i in range(n)]
    comb = " + ".join(f"{vars_str[i]}(v{i+1})" for i in range(n))
    pasos.append({"titulo": "Solución:", "desc": f"{comb} = 0"})

    combo_desc = " + ".join(f"{vars_str[i]}({polynomials[i]})" for i in range(n))
    zero_tuple = "(" + ", ".join(["0"]*max_len) + ")"
    pasos.append({"desc": f"Formamos la combinación lineal:\n{combo_desc} = {zero_tuple}"})

    # Gauss-Jordan
    pasos.append({"titulo": "Resolución en Gauss-Jordan:"})
    A_rref, gauss_steps = gauss_jordan(A)
    for step in gauss_steps:
        step_matrix = step.get("matriz", [])
        pasos.append({
            "desc": step.get("descripcion", ""),
            "matrix": step_matrix
        })

    # Construir solución general a partir de RREF
    sol_general = []
    m = len(A_rref)
    for i, row in enumerate(A_rref):
        eq_terms = []
        for j in range(n):
            coeff = row[j]
            if coeff != 0:
                eq_terms.append(f"{'' if coeff==1 else coeff}{vars_str[j]}")
        eq_str = " + ".join(eq_terms) + " = 0" if eq_terms else "0 = 0"
        sol_general.append(eq_str)

    # Sustituir variables libres por 0 para solución trivial
    final_sol = {v: Fraction(0) for v in vars_str}
    pasos.append({"titulo": "Solución General:", "desc": "\n".join(sol_general)})
    pasos.append({"desc": f"Solución trivial: {', '.join(f'{k} = {v}' for k,v in final_sol.items())}"})

    # Conclusión de dependencia
    rank = sum(any(el != 0 for el in row[:-1]) for row in A_rref)
    conclusion = "independientes" if rank == n else "dependientes"
    pasos.append({"desc": f"Indica que los polinomios son linealmente {conclusion}."})

    return pasos, conclusion