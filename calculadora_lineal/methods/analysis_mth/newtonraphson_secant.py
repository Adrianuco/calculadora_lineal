# calculadora_lineal/methods/analysis_mth/newtonraphson_secant.py
import sympy as sp
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def _parse_function(func_str: str):
    func_str = func_str.replace("^", "**")
    import re

    func_str = re.sub(r"e\^\(([^)]+)\)", r"exp(\1)", func_str)
    func_str = re.sub(r"e\^(-?[a-zA-Z0-9.+\-*/]+)", r"exp(\1)", func_str)
    func_str = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', func_str)
    func_str = re.sub(r'(\))(\()', r'\1*\2', func_str)
    func_str = re.sub(r'([a-zA-Z])(\()', r'\1*\2', func_str)
    func_str = re.sub(r"exp\(([^)]+)$", r"exp(\1)", func_str)

    x = sp.symbols('x')
    funcs = {
        'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan,
        'exp': sp.exp, 'log': sp.log, 'sqrt': sp.sqrt,
        'abs': sp.Abs,
        'e': sp.E
    }

    try:
        f_sym = sp.sympify(func_str, locals={'x': x, **funcs})
    except Exception as e:
        raise ValueError(f"Error al interpretar la función: {e}")

    f = sp.lambdify(x, f_sym, "numpy")
    df = sp.lambdify(x, sp.diff(f_sym, x), "numpy")

    return f, df, f_sym


def super_potencias(expr: str):
    mapa = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")
    import re
    def repl(m):
        return m.group(1).translate(mapa)
    return re.sub(r"\*\*(\-?\d+)", lambda m: repl(m), expr)


def newton_clasico(funcion: str, x0: float, tol: float):

    MAX_ITER = 100
    
    f, df, f_sym = _parse_function(funcion)

    tabla = []
    proceso = ""
    proceso += "Método Newton-Raphson (Clásico)\n"
    proceso += f"Función: f(x) = {f_sym}\n"
    proceso += f"Punto inicial: x0 = {x0}\n"
    proceso += f"Tolerancia: {tol}\n\n"

    xi = x0
    iteracion = 1

    while iteracion <= MAX_ITER:
        fxi = f(xi)
        dfxi = df(xi)

        if dfxi == 0:
            raise ValueError("La derivada es 0. El método no puede continuar.")

        xi1 = xi - fxi / dfxi
        Ea = abs(xi1 - xi)

        tabla.append({
            "Iteración": f"{iteracion} (i = {iteracion - 1})",
            "xi": round(xi, 6),
            "xi+1": round(xi1, 6),
            "Ea": round(Ea, 6),
            "f(xi)": round(fxi, 6),
            "f'(xi)": round(dfxi, 6)
        })

        proceso += f"\n\nIteración {iteracion} (i = {iteracion-1})\n\n"
        proceso += f"f(x{iteracion-1}) = {fxi:.6f}\n"
        proceso += f"f'(x{iteracion-1}) = {dfxi:.6f}\n\n"
        proceso += "xi+1 = xi - f(xi)/f'(xi)\n"
        proceso += f"xi+1 = {xi:.6f} - ({fxi:.6f}/{dfxi:.6f})\n"
        proceso += f"xi+1 = {xi1:.6f}\n\n"
        proceso += f"Ea = |{xi1:.6f} - {xi:.6f}| = {Ea:.6f}\n"

        if Ea < tol:
            valor_final = f(xi1)
            proceso += f"\n\nEl método converge en: {iteracion} iteraciones\n"
            proceso += f"La raíz aproximada es: x ≈ {xi1:.6f}"
            proceso += f"\nf(x_final) = {valor_final:.6e}"
            break

        xi = xi1
        iteracion += 1

    if iteracion > MAX_ITER:
        raise RuntimeError("Se alcanzó el límite máximo de iteraciones sin convergencia.")

    return tabla, iteracion, proceso

def newton_subintervalos(funcion: str, a: float, b: float, n: int,
                         x0: float, tol: float):

    MAX_ITER = 100

    f, df, f_sym = _parse_function(funcion)

    tabla = []
    proceso = ""

    # PASO h
    h = (b - a) / n
    proceso += "Paso (anchura de subintervalo):\n"
    proceso += f"h = (b - a) / n\n"
    proceso += f"h = ({b} - {a}) / {n}\n"
    proceso += f"h = {h:.6f}\n\n"

    proceso += "Coordenadas Xk y Valores Yk:\n\n"
    for k in range(n + 1):
        xk = a + k * h
        yk = f(xk)
        proceso += f"x{k} = {a} + {k} * {h:.6f} = {xk:.2f}\n"
        proceso += f"y{k} = f({xk:.2f}) = {yk:.6f}\n\n"

    xi = x0
    iteracion = 1

    while iteracion <= MAX_ITER:
        fxi = f(xi)
        dfxi = df(xi)

        if dfxi == 0:
            raise ValueError("La derivada es cero. No se puede continuar.")

        xi1 = xi - fxi / dfxi
        Ea = abs(xi1 - xi)

        tabla.append({
            "Iteración": f"{iteracion} (i = {iteracion - 1})",
            "xi": round(xi, 6),
            "xi+1": round(xi1, 6),
            "Ea": round(Ea, 6),
            "f(xi)": round(fxi, 6),
            "f'(xi)": round(dfxi, 6)
        })

        proceso += f"\n\nIteración {iteracion} (i = {iteracion - 1})\n"
        proceso += f"f(xi) = {fxi:.6f}\n"
        proceso += f"f'(xi) = {dfxi:.6f}\n\n"
        proceso += "xi+1 = xi - f(xi)/f'(xi)\n"
        proceso += f"xi+1 = {xi:.6f} - ({fxi:.6f}/{dfxi:.6f})\n"
        proceso += f"xi+1 = {xi1:.6f}\n\n"
        proceso += f"Ea = |{xi1:.6f} - {xi:.6f}| = {Ea:.6f}\n"

        if Ea < tol:
            valor_final = f(xi1)
            proceso += f"\n\nEl método converge en: {iteracion} iteraciones\n"
            proceso += f"La raíz aproximada es: x ≈ {xi1:.6f}"
            proceso += f"\nf(x_final) = {valor_final:.6e}\n"
            break

        xi = xi1
        iteracion += 1

    if iteracion > MAX_ITER:
        raise RuntimeError("Se alcanzó el límite máximo de iteraciones sin convergencia.")

    return tabla, iteracion, proceso

def secante(funcion: str, xm1: float, x0: float, tol: float):
    """
    Método de la Secante
    xm1 = x_{i-1}
    x0  = x_i
    """

    MAX_ITER = 100

    f, _, f_sym = _parse_function(funcion)

    tabla = []
    proceso = ""
    proceso += "Método de la Secante\n"
    proceso += f"Función: f(x) = {f_sym}\n"
    proceso += f"x₋₁ = {xm1}\n"
    proceso += f"x₀ = {x0}\n"
    proceso += f"Tolerancia: {tol}\n\n"

    xi_1 = xm1
    xi = x0

    iteracion = 1

    while iteracion <= MAX_ITER:
        fxi = f(xi)
        fxi_1 = f(xi_1)

        if fxi == fxi_1:
            raise ValueError("f(xi) y f(xi-1) son iguales. División por cero.")

        xi1 = xi - fxi * (xi - xi_1) / (fxi - fxi_1)
        Ea = abs(xi1 - xi)

        tabla.append({
            "Iteración": f"{iteracion} (i = {iteracion - 1})",
            "xi-1": round(xi_1, 6),
            "xi": round(xi, 6),
            "f(xi-1)": round(fxi_1, 6),
            "f(xi)": round(fxi, 6),
            "xi+1": round(xi1, 6),
            "Ea": round(Ea, 6)
        })

        proceso += f"\n\nIteración {iteracion} (i = {iteracion-1})\n"
        proceso += f"f(x_{iteracion}) = {fxi:.6f}\n"
        proceso += f"f(x_{iteracion-1}) = {fxi_1:.6f}\n\n"
        proceso += "xi+1 = xi - f(xi)(xi-1 - xi) / (f(xi-1) - f(xi))\n"
        proceso += (
            f"xi+1 = {xi:.6f} - ({fxi:.6f}({xi_1:.6f} - {xi:.6f}) / "
            f"({fxi_1:.6f} - {fxi:.6f}))\n"
        )
        proceso += f"xi+1 = {xi1:.6f}\n\n"
        proceso += f"Ea = |{xi1:.6f} - {xi:.6f}| = {Ea:.6f}\n"

        if Ea < tol:
            valor_final = f(xi1)
            proceso += f"\n\nEl método alcanzó la tolerancia {tol} en la iteración {iteracion}\n"
            proceso += f"La raíz aproximada es: x ≈ {xi1:.6f}\n"
            proceso += f"f(x_final) = {valor_final:.6e}"
            break

        xi_1 = xi
        xi = xi1
        iteracion += 1

    if iteracion > MAX_ITER:
        raise RuntimeError("Se alcanzó el máximo de iteraciones sin convergencia.")

    return tabla, iteracion, proceso

def graficar_funcion(funcion_str, xmin=-10, xmax=10):
    f, _, f_sym = _parse_function(funcion_str)
    
    xs = np.linspace(xmin, xmax, 400)
    ys = f(xs)

    plt.figure(figsize=(6,4))
    plt.axhline(0, color='black')
    plt.plot(xs, ys, label=f"f(x) = {f_sym}")
    plt.grid(True)
    plt.legend()
    plt.title("Gráfica de la función")
    plt.xlabel("x")
    plt.ylabel("f(x)")
    plt.show()

def exportar_a_excel_newton(tabla, nombre_archivo="resultadosnewtonraphson_secant.xlsx"): 
    df = pd.DataFrame(tabla) 
    df.to_excel(nombre_archivo, index=False) 
    return f"Archivo guardado como {nombre_archivo}"