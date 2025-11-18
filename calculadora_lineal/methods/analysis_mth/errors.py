# calculadora_lineal/methods/analysis_mth/errors.py
import numpy as np
import sympy as sp

def notacion_posicional(numero: str, base: int = 10):
    pasos = []
    numero_str = str(numero)

    if base == 2 and len(numero_str) != 7:
        raise ValueError("Para base 2 debes ingresar un número binario de 7 dígitos.")
    if base == 10 and len(numero_str) != 5:
        raise ValueError("Para base 10 debes ingresar un número de 5 dígitos.")
    if base == 2 and any(c not in "01" for c in numero_str):
        raise ValueError("El número contiene dígitos no permitidos para binario.")

    suma_total = 0
    potencia = len(numero_str) - 1
    sumatoria_partes = []

    for digito in numero_str:
        valor = int(digito) * (base ** potencia)
        pasos.append(f"{digito} × {base}^{potencia} = {valor}")
        sumatoria_partes.append(f"({digito}×{base}^{potencia})")
        suma_total += valor
        potencia -= 1

    sumatoria = " + ".join(sumatoria_partes) + f" = {suma_total}"

    return pasos, suma_total, sumatoria


def conceptos_de_error():
    ejemplos = {}

    valor_real = np.pi
    valor_aprox = 3.14
    ejemplos["Error inherente"] = (
        "El error inherente proviene de datos de entrada imprecisos o aproximados.\n"
        f"Ejemplo: π real = {valor_real}, aproximación = {valor_aprox}, "
        f"error = {abs(valor_real - valor_aprox)}.\n"
        "Explicación: cualquier medición o dato que no sea exacto ya introduce error."
    )

    ejemplos["Error de redondeo"] = (
        "Ocurre al representar valores infinitos con precisión finita.\n"
        f"Ejemplo: 1/3 = {1/3}, redondeado a 4 decimales = {round(1/3, 4)}, "
        f"error = {abs((1/3) - round(1/3, 4))}.\n"
        "Explicación: las computadoras no pueden almacenar infinitos decimales."
    )

    x = 1
    real = np.e
    aprox_trunc = 1 + x + x**2 / 2
    ejemplos["Error de truncamiento"] = (
        "Aparece al cortar una serie o proceso antes de completarse.\n"
        f"Aproximar e usando 1 + x + x²/2 = {aprox_trunc}, valor real = {real}, "
        f"error = {abs(real - aprox_trunc)}.\n"
        "Explicación: truncar reduce trabajo, pero acumula error."
    )

    explic_concepto = (
        "Overflow y Underflow:\n"
        "Son errores producidos por límites de representación numérica.\n"
        "Overflow → número demasiado grande.\n"
        "Underflow → número demasiado pequeño."
    )

    try:
        overflow = np.exp(1000)
    except OverflowError:
        overflow = "Overflow (demasiado grande)"

    ejemplos["Overflow"] = (
        f"{explic_concepto}\n\nEjemplo Overflow:\n{overflow}\n"
        "Explicación: exp(1000) excede la capacidad del sistema."
    )

    underflow = np.float32(1e-50)
    ejemplos["Underflow"] = (
        "Ejemplo Underflow:\n"
        f"{underflow} (se aproxima a 0 por límites internos)\n"
        "Explicación: el número es tan pequeño que se redondea a cero."
    )

    ejemplos["Error del modelo matemático"] = (
        "Surge al simplificar fenómenos reales.\n"
        "Ejemplo: un péndulo se modela como θ'' + θ = 0, válido solo para ángulos pequeños.\n"
        "Explicación: si el ángulo es grande, las hipótesis no se cumplen."
    )

    return ejemplos


def ejemplos_punto_flotante():
    ejemplos = {}

    ejemplos["0.1 + 0.2 == 0.3"] = (0.1 + 0.2 == 0.3)
    ejemplos["0.1 + 0.2"] = 0.1 + 0.2
    ejemplos["Explicación"] = (
        "0.1 y 0.2 no tienen representación exacta en binario.\n"
        "El error surge porque el sistema usa aproximaciones y al sumarlas "
        "no coincide exactamente con 0.3."
    )

    return ejemplos

def acumulacion_error_truncamiento(montos: list[float], iteraciones: int):
    if iteraciones > 50:
        raise ValueError("El número máximo de iteraciones permitidas es 50.")
    if len(montos) < iteraciones:
        raise ValueError("La lista de montos no contiene suficientes valores.")
    
    tasa = 0.0625
    
    tabla = []
    detalles = []
    error_acum = 0.0

    for i in range(1, iteraciones + 1):
        monto_ant = montos[i - 1]
        interes_real = monto_ant * tasa
        interes_trunc = float(f"{interes_real:.2f}")
        monto_real_nuevo = monto_ant + interes_real
        monto_trunc_nuevo = float(f"{(monto_ant + interes_trunc):.2f}")
        diferencia = monto_real_nuevo - monto_trunc_nuevo
        diferencia = float(f"{diferencia:.4f}")
        error_acum += diferencia
        error_acum = float(f"{error_acum:.4f}")

        tabla.append({
            "Iteración": i,
            "Monto anterior": float(f"{monto_ant:.2f}"),
            "Interés truncado": float(f"{interes_trunc:.2f}"),
            "Interés real": float(f"{interes_real:.4f}"),
            "Monto truncado": float(f"{monto_trunc_nuevo:.2f}"),
            "Monto real": float(f"{monto_real_nuevo:.4f}"),
            "Diferencia": float(f"{diferencia:.4f}"),
            "Error acumulado": float(f"{error_acum:.4f}")
        })

        texto = f"""
Iteración {i}
Monto anterior:  {monto_ant:,.2f}
Interés real:  {monto_ant:,.2f} × {tasa} = {interes_real:,.4f}
Interés truncado (2 dec.):  {interes_trunc:,.2f}
Monto real nuevo: {monto_ant:,.2f} + {interes_real:,.4f} = {monto_real_nuevo:,.4f}
Monto truncado nuevo: {monto_ant:,.2f} + {interes_trunc:,.2f} = {monto_trunc_nuevo:,.2f}
Diferencia:  {monto_real_nuevo:,.6f} - {monto_trunc_nuevo:,.2f} = {diferencia:,.6f}
Error acumulado: {error_acum:,.4f}
"""
        detalles.append(texto)

    return tabla, detalles

def error_absoluto_relativo(m: float, m_barra: float):
    ea = abs(m - m_barra)
    er = float("inf") if m == 0 else ea / m
    er_porcentaje = er * 100

    resultados = {
        "Datos": f"m = {m}, m̄ = {m_barra}",
        "Error Absoluto": f"ea = |{m} - {m_barra}| = {ea}",
        "Error Relativo": f"er = {ea} / |{m}| = {er} ({er_porcentaje}%)"
    }

    interpretacion = (
        f"El valor aproximado difiere {ea} unidades del real, "
        f"equivalente a {er_porcentaje}% respecto a {m}."
    )

    return resultados, interpretacion

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

    delta_y_aprox = round(f_der_x * delta_x, 4)
    delta_y_real = round(f_x_dx - f_x, 4)
    error_abs = round(abs(delta_y_real - delta_y_aprox), 4)

    derivada_str = str(f_der).replace("**", "^")

    resultados = {
        "Función": f"f(x) = {funcion}",
        "Datos": f"x = {x_val}, Δx = {delta_x}",
        "Derivada": f"f'(x) = {derivada_str}",
        "Derivada en x": f"f'({x_val}) = {round(f_der_x, 4)}",
        "Aproximación lineal": f"Δy ≈ f'({x_val}) * {delta_x} = {delta_y_aprox}",
        "Cálculo exacto": (
            f"f({x_val + delta_x}) − f({x_val}) = "
            f"{round(f_x_dx, 4)} − {round(f_x, 4)} = {delta_y_real}"
        ),
        "Error absoluto": f"|{delta_y_real} − {delta_y_aprox}| = {error_abs}"
    }

    interpretacion = (
        f"El error absoluto = {error_abs:.4f} muestra la diferencia entre "
        f"la aproximación lineal y el cambio real de la función."
    )

    return resultados, interpretacion