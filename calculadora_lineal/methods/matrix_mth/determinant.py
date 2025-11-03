# calculadora_lineal/methods/matrix_mth/determinant.py
from fractions import Fraction
from copy import deepcopy

def to_fraction(x):
    if isinstance(x, Fraction):
        return x
    try:
        return Fraction(str(x))
    except Exception:
        raise ValueError(f"Valor no válido: {x}")

def pretty_frac(frac):
    if isinstance(frac, Fraction):
        if frac.denominator == 1:
            return str(frac.numerator)
        return f"{frac.numerator}/{frac.denominator}"
    return str(frac)

def matrix_to_text(M):
    """Devuelve una representación visual clara y espaciosa de una matriz."""
    if not M:
        return ""
    filas_str = [[pretty_frac(x) for x in fila] for fila in M]
    col_widths = [max(max(len(fila[j]) for fila in filas_str), 6) for j in range(len(filas_str[0]))]
    texto = []
    for fila in filas_str:
        fila_fmt = " ".join(f"{val:^{col_widths[j]}}" for j, val in enumerate(fila))
        texto.append("    " + fila_fmt)
    return "\n".join(texto)

# ------------------ Métodos de cálculo ------------------

def metodo_cramer(A, b, step_viewer=None):
    pasos = []
    n = len(A)
    if n != len(b) or any(len(row) != n for row in A):
        raise ValueError("La matriz debe ser cuadrada y compatible con b")

    pasos.append("Método de Cramer\n")
    pasos.append("Matriz A:\n" + matrix_to_text(A))
    pasos.append("\nVector B:\n" + matrix_to_text([[val] for val in b]))

    def determinante(matriz):
        return determinante_cofactores(matriz)["resultado"]

    detA_info = determinante_cofactores(A)
    pasos.append("\nDet(A) =")
    pasos += detA_info["pasos"]
    detA = detA_info["resultado"]

    pasos.append(f"\nDet(A) = {pretty_frac(detA)}")

    if detA == 0:
        pasos.append("⚠️ El determinante de A es 0 → no se puede aplicar Cramer.")
        if step_viewer:
            for p in pasos:
                step_viewer.add_text(p)
        return {"resultado": None, "pasos": pasos, "detA": detA}

    soluciones = []
    for j in range(n):
        Aj = deepcopy(A)
        for i in range(n):
            Aj[i][j] = b[i]

        pasos.append(f"\nMatriz A_{j+1} (reemplazando columna {j+1} por B):\n" + matrix_to_text(Aj))

        detAj_info = determinante_cofactores(Aj)
        pasos += detAj_info["pasos"]
        detAj = detAj_info["resultado"]

        xj = detAj / detA
        soluciones.append(xj)
        pasos.append(f"x{j+1} = det(A_{j+1}) / det(A) = {pretty_frac(detAj)} / {pretty_frac(detA)} = {pretty_frac(xj)}")

    if step_viewer:
        for p in pasos:
            step_viewer.add_text(p)

    return {"resultado": soluciones, "pasos": pasos, "detA": detA}

def regla_sarrus(A, step_viewer=None):
    pasos = []
    if len(A) != 3 or any(len(row) != 3 for row in A):
        raise ValueError("La Regla de Sarrus solo aplica a matrices 3×3.")

    pasos.append("Método de Sarrus\n")
    pasos.append("Matriz A:\n" + matrix_to_text(A))

    extendida = [fila + fila[:2] for fila in A]
    pasos.append("\nAmpliando (repitiendo las dos primeras columnas):\n" + matrix_to_text(extendida))

    pasos.append("\nDiagonales principales:")
    positivos = []
    for i in range(3):
        diag = [A[j][(i + j) % 3] for j in range(3)]
        prod = diag[0] * diag[1] * diag[2]
        positivos.append(prod)
        pasos.append(f"  ({' × '.join(pretty_frac(v) for v in diag)}) = {pretty_frac(prod)}")

    pasos.append("\nDiagonales secundarias:")
    negativos = []
    for i in range(3):
        diag = [A[j][(i - j) % 3] for j in range(3)]
        prod = diag[0] * diag[1] * diag[2]
        negativos.append(prod)
        pasos.append(f"  ({' × '.join(pretty_frac(v) for v in diag)}) = {pretty_frac(prod)}")

    det = sum(positivos) - sum(negativos)
    pasos.append("\n|A| = (Suma principales) - (Suma secundarias)")
    pasos.append(f"|A| = ({' + '.join(pretty_frac(p) for p in positivos)}) - ({' + '.join(pretty_frac(n) for n in negativos)})")
    pasos.append(f"|A| = {pretty_frac(det)}")

    if step_viewer:
        for p in pasos:
            step_viewer.add_text(p)

    return {"resultado": det, "pasos": pasos}

def determinante_cofactores(A, step_viewer=None):
    pasos = []
    n = len(A)
    if any(len(row) != n for row in A):
        raise ValueError("La matriz debe ser cuadrada.")

    pasos.append("Método por Cofactores\n")
    pasos.append("Matriz A:\n" + matrix_to_text(A))

    def sub(i, j):
        sub_nums = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
        return str(i).translate(sub_nums) + str(j).translate(sub_nums)

    def cofactor_exp(matriz, nivel=0):
        tamaño = len(matriz)
        prefijo = "    " * nivel
        if tamaño == 1:
            val = matriz[0][0]
            return val, [f"{prefijo}Determinante de 1x1 = {pretty_frac(val)}"]
        if tamaño == 2:
            det2 = matriz[0][0] * matriz[1][1] - matriz[0][1] * matriz[1][0]
            pasos_local = [
                f"{prefijo}Matriz 2x2:\n{prefijo}{matrix_to_text(matriz)}",
                f"{prefijo}|A| = ({pretty_frac(matriz[0][0])}×{pretty_frac(matriz[1][1])}) - ({pretty_frac(matriz[0][1])}×{pretty_frac(matriz[1][0])}) = {pretty_frac(det2)}"
            ]
            return det2, pasos_local

        pasos_local = [f"\n{prefijo}Expansión por la primera fila:"]
        det_total = Fraction(0)
        cofactores = []

        for j in range(tamaño):
            a_1j = matriz[0][j]
            signo = (-1) ** (0 + j)
            a_texto = f"{pretty_frac(a_1j)}" if a_1j >= 0 else f"({pretty_frac(a_1j)})"
            submatriz = [fila[:j] + fila[j+1:] for fila in matriz[1:]]
            pasos_local.append(f"\n{prefijo}Elemento a{sub(1, j+1)} = {a_texto}")
            pasos_local.append(f"{prefijo}Submatriz M{sub(1, j+1)} eliminando fila 1 y columna {j+1}:\n{matrix_to_text(submatriz)}")
            sub_det, sub_pasos = cofactor_exp(submatriz, nivel + 1)
            pasos_local += sub_pasos
            contrib = signo * a_1j * sub_det
            signo_str = "" if signo > 0 else "-"
            pasos_local.append(f"{prefijo}Cofactor C{sub(1, j+1)} = {signo_str}{a_texto} × {pretty_frac(sub_det)} = {pretty_frac(contrib)}")
            cofactores.append(contrib)
            det_total += contrib

        suma_str = " + ".join(f"({pretty_frac(c)})" if c < 0 else f"{pretty_frac(c)}" for c in cofactores)
        pasos_local.append(f"\n{prefijo}Suma de cofactores: {suma_str} = {pretty_frac(det_total)}")
        return det_total, pasos_local

    det, detalles = cofactor_exp(A, nivel=0)
    pasos += detalles
    pasos.append(f"\n|A| = {pretty_frac(det)}")

    if step_viewer:
        for p in pasos:
            step_viewer.add_text(p)

    return {"resultado": det, "pasos": pasos}

# ------------------ Propiedades ------------------

def verificar_propiedades(A, det):
    texto = []
    n = len(A)

    def matrix_to_text(m):
        if not m:
            return ""
        filas_str = [[str(x) for x in fila] for fila in m]
        col_widths = [max(max(len(fila[j]) for fila in filas_str), 6) for j in range(len(filas_str[0]))]
        texto = []
        for fila in filas_str:
            fila_fmt = " ".join(f"{val:^{col_widths[j]}}" for j, val in enumerate(fila))
            texto.append("    " + fila_fmt)
        return "\n".join(texto)

    texto.append("  PROPIEDADES Y TEOREMAS DEL DETERMINANTE")

    # ▫️ Propiedad 1
    texto.append("1.  Si una fila o columna es nula → det(A) = 0")
    fila_nula = any(all(x == 0 for x in fila) for fila in A)
    col_nula = any(all(A[i][j] == 0 for i in range(n)) for j in range(n))

    if fila_nula or col_nula:
        texto.append("    ✅ Se encontró una fila o columna nula → det(A)=0.\n")
    else:
        texto.append("     Ninguna fila o columna es nula.\n")

    # ▫️ Propiedad 2
    texto.append("2.  Si dos filas o columnas son proporcionales → det(A) = 0")
    proporcional = False
    for i in range(n):
        for j in range(i+1, n):
            ratio = None
            iguales = True
            for k in range(n):
                if A[j][k] == 0 and A[i][k] == 0:
                    continue
                elif A[i][k] == 0 or A[j][k] == 0:
                    iguales = False
                    break
                r = A[i][k] / A[j][k]
                if ratio is None:
                    ratio = r
                elif r != ratio:
                    iguales = False
                    break
            if iguales:
                proporcional = True
                texto.append(f"    ✅ Filas {i+1} y {j+1} son proporcionales → det(A)=0.\n")
                break
        if proporcional:
            break
    if not proporcional:
        texto.append("     No hay filas ni columnas proporcionales.\n")

    # ▫️ Propiedad 3
    if n >= 2:
        texto.append("3.  Si se intercambian dos filas → det cambia de signo\n")

        B = deepcopy(A)
        B[0], B[1] = B[1], B[0]
        detB = determinante_cofactores(B)["resultado"]

        texto.append("     Matriz original A:")
        texto.append(matrix_to_text(A))
        texto.append(f"      det(A) = {det}\n")

        texto.append("     Matriz B (filas 1 y 2 intercambiadas):")
        texto.append(matrix_to_text(B))
        texto.append(f"      det(B) = {detB}\n")

        if detB == -det:
            texto.append("    ✅ Se cumple: det(B) = -det(A)\n")
        else:
            texto.append("     No se cumple (puede que det=0)\n")

    # ▫️ Propiedad 4
    if n >= 2:
        texto.append("4.  Si una fila se multiplica por un escalar k → det se multiplica por k\n")

        k = 2
        C = deepcopy(A)
        for j in range(n):
            C[0][j] *= k
        detC = determinante_cofactores(C)["resultado"]

        texto.append(f"     Matriz original A:")
        texto.append(matrix_to_text(A))
        texto.append(f"      det(A) = {det}\n")

        texto.append(f"     Matriz C (fila 1 × {k}):")
        texto.append(matrix_to_text(C))
        texto.append(f"      det(C) = {detC}\n")

        if detC == k * det:
            texto.append(f"    ✅ Se cumple: det(C) = {k} × det(A)\n")
        else:
            texto.append("     No se cumple (o det=0)\n")

    # ▫️ Propiedad 5
    if n >= 2:
        texto.append("5.  Propiedad multiplicativa → det(AB) = det(A) × det(B)\n")

        I = [[Fraction(1 if i == j else 0) for j in range(n)] for i in range(n)]
        prod = [[sum(A[i][k] * I[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
        det_prod = determinante_cofactores(prod)["resultado"]
        detI = determinante_cofactores(I)["resultado"]

        texto.append("     Matriz A:")
        texto.append(matrix_to_text(A))
        texto.append(f"      det(A) = {det}\n")

        texto.append("     Matriz B (identidad):")
        texto.append(matrix_to_text(I))
        texto.append(f"      det(B) = {detI}\n")

        texto.append("     Producto AB:")
        texto.append(matrix_to_text(prod))
        texto.append(f"      det(AB) = {det_prod}\n")

        if det_prod == det * detI:
            texto.append("    ✅ Se cumple: det(AB) = det(A) × det(B)\n")
        else:
            texto.append("     No se cumple (o det=0)\n")


    return "\n".join(texto)