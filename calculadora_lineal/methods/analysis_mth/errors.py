import numpy as np
import sympy as sp
import pandas as pd

# ===============================
# Notación Posicional
# ===============================
def truncar(valor, decimales=2):
    factor = 10 ** decimales
    return int(valor * factor) / factor

def notacion_posicional(numero: str, base: int = 10):
    pasos = []
    numero_str = str(numero)

    if base == 2 and any(c not in "01" for c in numero_str):
        raise ValueError("El número contiene dígitos no permitidos para binario.")

    suma_total = 0
    potencia = len(numero_str) - 1
    partes = []


    for digito in numero_str:
        valor = int(digito) * (base ** potencia)
        pasos.append(f"{digito} × {base}^{potencia} = {valor}")
        partes.append(f"({digito}×{base}^{potencia})")
        suma_total += valor
        potencia -= 1

    sumatoria = " + ".join(partes) + f" = {suma_total}"
    return pasos, suma_total, sumatoria

# ===============================
# Conceptos de error
# ===============================
def conceptos_de_error():
    ejemplos = {}
    valor_real = np.pi
    valor_aprox = 3.14
    x = 1
    valor_real_e = np.e
    aprox_trunc = 1 + x + x**2 / 2

    ejemplos["Error Inherente"] = (
        "• Definición: Es el error presente en los datos de entrada.\n"
        f"• Ejemplo: π real = {valor_real}, aproximación = {valor_aprox}, "
        f"error = {abs(valor_real - valor_aprox):.6f}\n"
        "• Explicación: Los datos no son exactos desde el inicio."
    )

    ejemplos["Error de Redondeo"] = (
        "• Definición: Se produce al limitar decimales en cálculos.\n"
        f"• Ejemplo: 1/3 ≈ {round(1/3,4)}, error = {abs(1/3 - round(1/3,4)):.6f}\n"
        "• Explicación: No todos los decimales infinitos se pueden representar."
    )

    ejemplos["Error de Truncamiento"] = (
        "• Definición: Surge al cortar un cálculo o serie antes de completarlo.\n"
        f"• Ejemplo: Aproximación de e con 1+x+x²/2 = {aprox_trunc:.6f}, valor real = {valor_real_e:.6f}, "
        f"error = {abs(valor_real_e - aprox_trunc):.6f}\n"
        "• Explicación: La truncación reduce trabajo, pero acumula error."
    )

    ejemplos["Overflow / Underflow"] = (
        "• Definición: Errores por límites de representación numérica.\n"
        "  - Overflow: número demasiado grande.\n"
        "  - Underflow: número demasiado pequeño.\n"
        "• Ejemplo Overflow: np.exp(1000) provoca Overflow.\n"
        "• Ejemplo Underflow: np.float32(1e-50) ≈ 0."
    )

    ejemplos["Error del Modelo Matemático"] = (
        "• Definición: Surge al simplificar fenómenos reales.\n"
        "• Ejemplo: Péndulo simple θ'' + θ = 0, válido solo para ángulos pequeños.\n"
        "• Explicación: La simplificación matemática introduce error inherente."
    )

    return ejemplos

# ===============================
# Ejemplos punto flotante
# ===============================
def ejemplos_punto_flotante():
    ejemplos = {}
    suma = 0.1 + 0.2
    ejemplos["Comparación"] = "0.1 + 0.2 == 0.3"
    ejemplos["Resultado"] = f"0.1 + 0.2 = {suma:.17f}"
    ejemplos["Explicación"] = (
        "• 0.1 y 0.2 no tienen representación exacta en binario.\n"
        "• La suma no coincide exactamente con 0.3.\n"
        "• Esto demuestra el error de punto flotante en computadoras."
    )
    return ejemplos

# ===============================
# Acumulación error truncamiento
# ===============================
def acumulacion_error_truncamiento(monto_inicial: float, iteraciones: int):
    if iteraciones < 1 or iteraciones > 50:
        raise ValueError("Número de iteraciones permitido: 1-50")

    tasa = 0.0625
    tabla = []
    detalles = []
    error_acum = 0.0
    monto_ant = monto_inicial

    # Cabecera de tabla formateada
    header = (
        f"{'Iteración':>10} | "
        f"{'Monto anterior':>15} | "
        f"{'Interés truncado':>17} | "
        f"{'Interés real':>15} | "
        f"{'Monto truncado':>15} | "
        f"{'Monto real':>12} | "
        f"{'Diferencia':>12} | "
        f"{'Error acumulado':>17}"
    )
    sep = "-" * len(header)
    tabla_texto = header + "\n" + sep + "\n"

    for i in range(1, iteraciones + 1):
        interes_real = monto_ant * tasa
        monto_real_nuevo = monto_ant + interes_real
        interes_trunc = truncar(interes_real, 2)
        monto_trunc_nuevo = truncar(monto_ant + interes_trunc, 2)
        diferencia = round(monto_real_nuevo - monto_trunc_nuevo, 6)
        error_acum += diferencia
        error_acum = round(error_acum, 6)

        # Guardamos la fila en tabla
        tabla.append({
            "Iteración": i,
            "Monto anterior": round(monto_ant, 2),
            "Interés truncado": round(interes_trunc, 2),
            "Interés real": round(interes_real, 6),
            "Monto truncado": round(monto_trunc_nuevo, 2),
            "Monto real": round(monto_real_nuevo, 6),
            "Diferencia": diferencia,
            "Error acumulado": error_acum
        })

        # Formateamos la fila para la tabla de texto
        tabla_texto += (
            f"{i:>10} | "
            f"{monto_ant:>15,.2f} | "
            f"{interes_trunc:>17,.2f} | "
            f"{interes_real:>15,.6f} | "
            f"{monto_trunc_nuevo:>15,.2f} | "
            f"{monto_real_nuevo:>12,.6f} | "
            f"{diferencia:>12,.6f} | "
            f"{error_acum:>17,.6f}\n"
        )

        # Detalle paso a paso
        texto_detalle = (
            f"Iteración {i}\n"
            f"Monto anterior: {monto_ant:,.2f}\n"
            f"Interés real: {monto_ant:,.2f} × {tasa} = {interes_real:,.6f}\n"
            f"Interés truncado (2 dec.): {interes_trunc:,.2f}\n"
            f"Monto real nuevo: {monto_ant:,.2f} + {interes_real:,.6f} = {monto_real_nuevo:,.6f}\n"
            f"Monto truncado nuevo: {monto_ant:,.2f} + {interes_trunc:,.2f} = {monto_trunc_nuevo:,.2f}\n"
            f"Diferencia: {diferencia:,.6f}\n"
            f"Error acumulado: {error_acum:,.6f}\n"
        )
        detalles.append(texto_detalle)
        monto_ant = monto_trunc_nuevo

    return tabla, detalles, tabla_texto

# ===============================
# Error absoluto y relativo
# ===============================
def error_absoluto_relativo(m: float, m_barra: float):
    ea = abs(m - m_barra)
    er = float("inf") if m == 0 else ea / abs(m)
    er_pct = er * 100

    resultados = {
        "Datos": f"m = {m}, m̄ = {m_barra}",
        "Error Absoluto": f"{ea}",
        "Error Relativo": f"{er} ({er_pct}%)",
    }

    interpretacion = (
        f"El error absoluto ({ea}) indica cuánto difiere el valor aproximado.\n"
        f"El error relativo ({er_pct}%) expresa la magnitud del error respecto al valor real."
    )

    return resultados, interpretacion

# ===============================
# Propagación de errores
# ===============================
def propagacion_errores(funcion: str, x_val: float, delta_x: float):
    x = sp.Symbol("x")
    funcion_procesada = funcion.replace("^", "**")

    try:
        f = sp.sympify(funcion_procesada)
    except Exception as e:
        raise ValueError(f"Error al interpretar la función: {e}")

    f_der = sp.diff(f, x)

    f_x = float(f.evalf(subs={x: x_val}))
    f_x_dx = float(f.evalf(subs={x: x_val + delta_x}))
    f_der_x = float(f_der.evalf(subs={x: x_val}))

    delta_y_aprox = f_der_x * delta_x
    delta_y_real = f_x_dx - f_x
    error_abs = abs(delta_y_real - delta_y_aprox)

    # Formateo para evitar notación científica
    f_x_str = f"{f_x:.9f}"
    f_x_dx_str = f"{f_x_dx:.9f}"
    f_der_x_str = f"{f_der_x:.9f}"
    delta_y_aprox_str = f"{delta_y_aprox:.6f}"
    delta_y_real_str = f"{delta_y_real:.6f}"
    error_abs_str = f"{error_abs:.6f}"

    derivada_str = str(f_der).replace("**", "^")

    resultados = {
        "Función": f"f(x) = {funcion}",
        "Datos": f"x = {x_val}, Δx = {delta_x}",
        "Derivada": f"f'(x) = {derivada_str}",
        "Derivada en x": f"f'({x_val}) = {f_der_x_str}",
        "Aproximación lineal": f"Δy ≈ f'({x_val}) * {delta_x} = {delta_y_aprox_str}",
        "Cálculo exacto": f"f({x_val + delta_x}) − f({x_val}) = {f_x_dx_str} − {f_x_str} = {delta_y_real_str}",
        "Error absoluto": f"|{delta_y_real_str} − {delta_y_aprox_str}| = {error_abs_str}"
    }

    interpretacion = f"El error absoluto = {error_abs_str} muestra la diferencia entre aproximación lineal y cambio real."

    return resultados, interpretacion

# ===============================
# Exportar Excel
# ===============================
def exportar_a_excel(tabla: list[dict], nombre_archivo: str = "resultado.xlsx"):
    df = pd.DataFrame(tabla)
    df.to_excel(nombre_archivo, index=False)
    return f"Archivo guardado como {nombre_archivo}"