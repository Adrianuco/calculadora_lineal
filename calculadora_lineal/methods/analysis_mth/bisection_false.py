# calculadora_lineal/methods/analysis_mth/bisection_false.py
import sympy as sp
import pandas as pd
import math

def _parse_function(func_str: str):
    import re

    func_str = func_str.replace("^", "**")
    func_str = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', func_str)
    func_str = re.sub(r'(\))(\()', r'\1*\2', func_str)
    func_str = re.sub(r'([a-zA-Z])(\()', r'\1*\2', func_str)

    x = sp.symbols('x')

    funciones_permitidas = {
        'sin': sp.sin,
        'cos': sp.cos,
        'tan': sp.tan,
        'exp': sp.exp,
        'log': sp.log,
        'sqrt': sp.sqrt,
        'abs': sp.Abs
    }

    try:
        f = sp.sympify(func_str, locals={'x': x, **funciones_permitidas})
    except Exception as e:
        raise ValueError(f"Error al interpretar la función: {e}")

    return sp.lambdify(x, f, "numpy"), f

def biseccion(funcion: str, xl: float, xu: float, E: float):

    f, f_sym = _parse_function(funcion)
    tabla = []
    proceso = ""

    n_calc = (xu - xl) / E
    n_log = math.log2(n_calc)
    n_iter = math.ceil(n_log)

    proceso += "Cálculo del número de iteraciones necesarias:\n"
    proceso += f"n ≥ log2( ({xu} - {xl}) / {E} )\n"
    proceso += f"n ≥ log2( {(xu - xl) / E} )\n"
    proceso += f"n ≥ {n_log}\n\n"
    proceso += f"Por tanto se necesitan {n_iter} iteraciones para que la semi - Longitud sea menor que la tolerancia.\n\n"

    xr_prev = None

    for it in range(1, n_iter + 1):

        xr = (xl + xu) / 2
        vl = f(xl)
        vu = f(xu)
        vr = f(xr)

        if xr_prev is None:
            Ea = 0.0
        else:
            Ea = abs((xr - xr_prev) / xr)

        intervalo = round((xu - xl), 6)

        tabla.append({
            "Iteración": it,
            "xl": round(xl, 6),
            "xu": round(xu, 6),
            "xr": round(xr, 6),
            "Ea": round(Ea, 6),
            "vl": round(vl, 6),
            "vu": round(vu, 6),
            "vr": round(vr, 6),
            "xu-xl<E": intervalo
        })

        if intervalo < E:
            break

        proceso += f"\n\niteración {it}\n"
        proceso += f"xl = {xl:.6f}\n"
        proceso += f"xu = {xu:.6f}\n"

        proceso += "\nCálculo de xr:\n"
        proceso += f"xr = (xl + xu) / 2\n"
        proceso += f"xr = ({xl:.6f} + {xu:.6f}) / 2\n"
        proceso += f"xr = {xr:.6f}\n"

        proceso += "\nCálculo de valores de la función:\n"
        proceso += f"vl = f(xl) = f({xl:.6f}) = {vl:.6f}\n"
        proceso += f"vu = f(xu) = f({xu:.6f}) = {vu:.6f}\n"
        proceso += f"vr = f(xr) = f({xr:.6f}) = {vr:.6f}\n"

        signo = " < 0" if vl * vr < 0 else " > 0"
        proceso += f"\nf(xl) * f(xr) = {signo}\n"

        if vl * vr < 0:
            proceso += f"La raíz está entre [{xl:.6f} , {xr:.6f}]\n"
            xu = xr
        else:
            proceso += f"La raíz está entre [{xr:.6f} , {xu:.6f}]\n"
            xl = xr

        if it >= 2:
            proceso += "\nCálculo del error:\n"
            proceso += f"Ea = | xr(k) - xr(k-1) | / xr(k)\n"
            proceso += f"Ea = | {xr:.6f} - {xr_prev:.6f} | / {xr:.6f}\n"
            proceso += f"Ea = {Ea:.6f}\n"
            proceso += f"Ea = {Ea*100:.6f} %\n"
        else:
            proceso += "Ea = 0.000000\n"

        xr_prev = xr

    return tabla, n_iter, proceso

def falsa_posicion(funcion: str, xl: float, xu: float, E: float):

    f, f_sym = _parse_function(funcion)
    tabla = []
    proceso = ""

    n_calc = (xu - xl) / E
    n_log = math.log2(n_calc)
    n_iter = math.ceil(n_log)

    proceso += "Cálculo del número de iteraciones necesarias:\n"
    proceso += f"n ≥ log2( ({xu} - {xl}) / {E} )\n"
    proceso += f"n ≥ log2( {(xu - xl) / E} )\n"
    proceso += f"n ≥ {n_log}\n\n"
    proceso += f"Por tanto se necesitan {n_iter} iteraciones para que la semi - Longitud sea menor que la tolerancia.\n\n"

    xr_prev = None

    for it in range(1, n_iter + 1):

        vl = f(xl)
        vu = f(xu)

        xr = xu - vu * (xl - xu) / (vl - vu)
        vr = f(xr)

        # Error
        if xr_prev is None:
            Ea = 0.0
        else:
            Ea = abs((xr - xr_prev) / xr)

        tabla.append({
            "Iteración": it,
            "xl": round(xl, 6),
            "xu": round(xu, 6),
            "xr": round(xr, 6),
            "Ea": round(Ea, 6),
            "vl": round(vl, 6),
            "vu": round(vu, 6),
            "vr": round(vr, 6),
            "E<Ea": Ea < E
        })

        proceso += f"\n\niteración {it}\n"
        proceso += f"xl = {xl:.6f}\n"
        proceso += f"xu = {xu:.6f}\n"

        proceso += "\nCálculo de xr:\n"
        proceso += "xr = xu - f(xu) * (xl - xu) / (f(xl) - f(xu))\n"
        proceso += f"xr = {xu:.6f} - ({vu:.6f}) * ({xl:.6f} - {xu:.6f}) / ({vl:.6f} - {vu:.6f})\n"
        proceso += f"xr = {xr:.6f}\n"

        proceso += "\nCálculo de valores de la función:\n"
        proceso += f"vl = f(xl) = f({xl:.6f}) = {vl:.6f}\n"
        proceso += f"vu = f(xu) = f({xu:.6f}) = {vu:.6f}\n"
        proceso += f"vr = f(xr) = f({xr:.6f}) = {vr:.6f}\n"

        signo = " < 0" if vl * vr < 0 else " > 0"
        proceso += f"\nf(xl) * f(xr) = {signo}\n"

        if vl * vr < 0:
            proceso += f"La raíz está entre [{xl:.6f} , {xr:.6f}]\n"
            xu = xr
        else:
            proceso += f"La raíz está entre [{xr:.6f} , {xu:.6f}]\n"
            xl = xr

        if it >= 2:
            proceso += "\nCálculo del error:\n"
            proceso += f"Ea = | {xr:.6f} - {xr_prev:.6f} | / {xr:.6f}\n"
            proceso += f"Ea = {Ea:.6f}\n"
            proceso += f"Ea = {Ea*100:.6f} %\n"
        else:
            proceso += "Ea = 0.000000\n"

        if Ea < E:
            break

        xr_prev = xr

    return tabla, n_iter, proceso

def exportar_a_excel(tabla, nombre_archivo="resultados_bf.xlsx"):
    df = pd.DataFrame(tabla)
    df.to_excel(nombre_archivo, index=False)
    return f"Archivo guardado como {nombre_archivo}"