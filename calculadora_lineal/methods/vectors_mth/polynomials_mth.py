# calculadora_lineal/methods/vectors_mth/polynomials_mth.py
from fractions import Fraction
from ..matrix_mth.gauss_jordan import gauss_jordan, analyze_rref

def parse_polynomial_manual(expr):
    """Convierte un string tipo 'x^3 - 2x + 1' a lista de coeficientes."""
    expr = expr.replace(" ", "").replace("-", "+-")
    terms = [t for t in expr.split("+") if t]
    coef_dict = {}
    for term in terms:
        if "x" not in term:
            coef = float(term)
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
                coef = 1.0
            elif base == "-":
                coef = -1.0
            else:
                coef = float(base)
        coef_dict[exp] = coef_dict.get(exp, 0) + coef

    max_exp = max(coef_dict.keys())
    coeffs = [0.0] * (max_exp + 1)
    for exp, coef in coef_dict.items():
        coeffs[exp] = float(coef)
    return coeffs


def check_polynomial_dependency(polynomials):
    """
    Convierte todo a listas de floats y evita errores de 'len()'.
    """
    processed = []
    for p in polynomials:
        if isinstance(p, str):
            coeffs = parse_polynomial_manual(p)
        elif isinstance(p, (int, float, Fraction)):
            coeffs = [float(p)]
        else:
            coeffs = [float(x) for x in p]
        processed.append(coeffs)

    # Alinear longitudes
    max_len = max(len(p) for p in processed) if processed else 0
    for p in processed:
        p += [0.0] * (max_len - len(p))

    # Construir matriz aumentada
    A = [[processed[j][i] for j in range(len(processed))] + [0.0] for i in range(max_len)]

    if not A:
        return "independientes"

    # Gauss-Jordan
    A_rref, _ = gauss_jordan(A, record_steps=False)
    analisis = analyze_rref(A_rref)
    return "independientes" if analisis["tipo"] == "única" else "dependientes"