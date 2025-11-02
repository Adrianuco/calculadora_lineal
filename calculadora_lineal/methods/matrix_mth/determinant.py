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
    """Devuelve una cadena representando la matriz completa en bloque."""
    return "\n".join(["  " + "  ".join(pretty_frac(x) for x in fila) for fila in M])

def metodo_cramer(A, b):
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

    return {"resultado": soluciones, "pasos": pasos, "detA": detA}

def regla_sarrus(A):
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

    return {"resultado": det, "pasos": pasos}

def determinante_cofactores(A):
    pasos = []
    n = len(A)
    if any(len(row) != n for row in A):
        raise ValueError("La matriz debe ser cuadrada.")

    pasos.append("Método por Cofactores\n")
    pasos.append("Matriz A:\n" + matrix_to_text(A))

    def cofactor_exp(matriz, nivel=0, prefix=""):
        tamaño = len(matriz)
        if tamaño == 1:
            return matriz[0][0], [f"{prefix}Único elemento: {pretty_frac(matriz[0][0])}"]

        if tamaño == 2:
            det2 = matriz[0][0]*matriz[1][1] - matriz[0][1]*matriz[1][0]
            pasos_loc = [f"{prefix}Submatriz 2×2:\n{matrix_to_text(matriz)}"]
            pasos_loc.append(f"{prefix}Det 2×2 = ({pretty_frac(matriz[0][0])}×{pretty_frac(matriz[1][1])}) - ({pretty_frac(matriz[0][1])}×{pretty_frac(matriz[1][0])}) = {pretty_frac(det2)}")
            return det2, pasos_loc

        det_total = 0
        pasos_loc = []
        for j in range(tamaño):
            val = matriz[0][j]
            signo = (-1) ** j
            submatriz = [fila[:j] + fila[j+1:] for fila in matriz[1:]]
            pasos_loc.append(f"{prefix}a₁{j+1} = {pretty_frac(val)}, signo = {'+' if signo>0 else '-'} → contribuye:")
            sub_det, sub_pasos = cofactor_exp(submatriz, nivel+1, prefix + '    ')
            contrib = signo * val * sub_det
            pasos_loc += sub_pasos
            pasos_loc.append(f"{prefix}  Contribución = {pretty_frac(signo)} × {pretty_frac(val)} × {pretty_frac(sub_det)} = {pretty_frac(contrib)}")
            det_total += contrib

        pasos_loc.append(f"{prefix}Suma nivel {nivel} = {pretty_frac(det_total)}")
        return det_total, pasos_loc

    det, detalles = cofactor_exp(A, nivel=0, prefix="")
    pasos += detalles
    pasos.append(f"\n|A| = {pretty_frac(det)}")
    return {"resultado": det, "pasos": pasos}

def verificar_propiedades(A, det):
    texto = ["\nPropiedades y Teoremas del Determinante:"]
    n = len(A)

    # Propiedad 1
    for i, fila in enumerate(A):
        if all(x == 0 for x in fila):
            texto.append(f"✅ Propiedad 1: La fila {i+1} es nula → det(A) = 0")
            break
    else:
        texto.append("⚠️ Propiedad 1: Ninguna fila es nula.")

    for j in range(n):
        if all(A[i][j] == 0 for i in range(n)):
            texto.append(f"✅ Propiedad 1: La columna {j+1} es nula → det(A) = 0")
            break

    # Propiedad 2
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
                texto.append(f"✅ Propiedad 2: Filas {i+1} y {j+1} son proporcionales → det(A)=0")
                break
        if proporcional:
            break
    if not proporcional:
        texto.append("⚠️ Propiedad 2: No hay filas o columnas proporcionales.")

    # Propiedad 3
    if n >= 2:
        B = deepcopy(A)
        B[0], B[1] = B[1], B[0]
        detB = determinante_cofactores(B)["resultado"]
        if detB == -det:
            texto.append("✅ Propiedad 3: Al intercambiar dos filas, det cambia de signo.")
        else:
            texto.append("⚠️ Propiedad 3: No se verifica el cambio de signo (o det=0).")

    # Propiedad 4
    if n >= 2:
        k = 2
        C = deepcopy(A)
        for j in range(n):
            C[0][j] *= k
        detC = determinante_cofactores(C)["resultado"]
        if detC == k * det:
            texto.append(f"✅ Propiedad 4: Multiplicar una fila por {k} multiplica el determinante por {k}.")
        else:
            texto.append(f"⚠️ Propiedad 4: No se verifica (o det=0).")

    # Propiedad 5
    if n >= 2:
        I = [[Fraction(1 if i == j else 0) for j in range(n)] for i in range(n)]
        prod = [[sum(A[i][k] * I[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
        det_prod = determinante_cofactores(prod)["resultado"]
        detI = determinante_cofactores(I)["resultado"]
        if det_prod == det * detI:
            texto.append("✅ Propiedad 5: det(AB) = det(A) × det(B) (verificado con I).")
        else:
            texto.append("⚠️ Propiedad 5: No se verifica (o det=0).")

    return "\n".join(texto)