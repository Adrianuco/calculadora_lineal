# calculadora_lineal/methods/vectors.py
from ..matrix_mth.gauss_jordan import gauss_jordan, analyze_rref, pretty_frac

def check_linear_combination(A):
    """
    Verifica si el último vector (columna RHS) es combinación lineal de los demás vectores.
    A: lista de listas (matriz d x (k+1)), última columna es v.
    
    Retorna:
        {
            "steps": [{"desc": str, "matrix": list}, ...],
            "conclusion": str
        }
    """
    steps = []
    # Obtenemos RREF y pasos
    A_rref, rref_steps = gauss_jordan(A, record_steps=True)
    for s in rref_steps:
        steps.append({"desc": s["descripcion"], "matrix": s["matriz"]})

    # Analizamos RREF
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