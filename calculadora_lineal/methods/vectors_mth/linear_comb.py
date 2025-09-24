from ..matrix_mth.gauss_jordan import gauss_jordan, analyze_rref, pretty_frac
from .linear_comb_prep import build_linear_combination_system

def check_linear_combination(A):
    """
    Verifica si el último vector (columna RHS) es combinación lineal de los demás vectores.
    A: lista de listas (matriz d x (k+1)), última columna es v.
    """
    steps = []

    # Separar vectores
    d = len(A)
    k = len(A[0]) - 1
    vectors = {f"u{j+1}": [A[i][j] for i in range(d)] for j in range(k)}
    v = [A[i][k] for i in range(d)]

    # --- Parte nueva: pasos previos ---
    prep_steps, A_aug = build_linear_combination_system(vectors, v)
    steps.extend(prep_steps)

    # --- Gauss-Jordan con la matriz resultante ---
    A_rref, rref_steps = gauss_jordan(A_aug, record_steps=True)
    for s in rref_steps:
        steps.append({"type": "matrix", "desc": s["descripcion"], "matrix": s["matriz"]})

    # --- Conclusión ---
    info = analyze_rref(A_rref)

    if info["tipo"] == "inconsistente":
        conclusion = "El vector v NO es combinación lineal de u1..uk (sistema inconsistente)."
    elif info["tipo"] == "única":
        coeffs = info["solucion"]
        coeffs_str = ", ".join([f"c{j+1} = {pretty_frac(c)}" for j, c in enumerate(coeffs)])
        conclusion = "Sí es combinación lineal. Coeficientes (únicos): " + coeffs_str
    else:
        free = info["free_vars"]
        exprs = info["expresiones"]
        free_str = ", ".join(f"x{f+1}" for f in free)
        expr_lines = ", ".join([f"c{var+1} = {val}" for var, val in exprs.items()])
        conclusion = f"Sí es combinación lineal (infinitas soluciones). Variables libres: {free_str}. Expresiones: {expr_lines}"

    return {"steps": steps, "conclusion": conclusion}