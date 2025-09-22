# calculadora_lineal/methods/vectors_mth/vector_expression_parser.py
import re
from fractions import Fraction

def tokenize(expr: str):
    """
    Convierte la expresión en tokens.
    Ejemplo: "2*(u1 + u2) - u3·u4" -> ['2', '*', '(', 'u1', '+', 'u2', ')', '-', 'u3', '·', 'u4']
    """
    expr = expr.replace(" ", "")
    tokens = re.findall(r'\d+/\d+|\d+|u\d+|[\+\-\*·\(\)]', expr)
    return tokens

def vec_str(vec):
    """
    Convierte un vector de Fracciones a string legible: [2 10 3/4]
    """
    return "[" + "  ".join(str(v.numerator) if v.denominator==1 else f"{v.numerator}/{v.denominator}" for v in vec) + "]"

def parse_expression(tokens, vectors, step_callback=None):
    """
    Parser recursivo con soporte para paréntesis.
    """
    def parse_term(index):
        token = tokens[index]
        if token == "(":
            result, new_index = parse_sum(index + 1)
            if tokens[new_index] != ")":
                raise ValueError("Paréntesis no balanceados")
            return result, new_index + 1
        elif token.startswith("u"):
            if token not in vectors:
                raise ValueError(f"Vector {token} no definido")
            return vectors[token], index + 1
        else:
            # Escalar como Fraction
            return Fraction(token), index + 1

    def apply_op(left, op, right):
        # Ambos vectores
        if isinstance(left, list) and isinstance(right, list):
            if op == "+":
                result = [a+b for a,b in zip(left,right)]
            elif op == "-":
                result = [a-b for a,b in zip(left,right)]
            elif op == "*":  # elemento a elemento
                result = [a*b for a,b in zip(left,right)]
            elif op == "·":  # producto escalar
                result = sum(a*b for a,b in zip(left,right))
            # Registrar paso solo si es suma/resta o multiplicación escalar-vector
            if step_callback:
                # Mostrar solo cuando el resultado es lista
                if isinstance(result, list):
                    step_callback(f"{vec_str(left)} {op} {vec_str(right)}", result)
            return result

        # Vector * escalar
        elif isinstance(left, list) and isinstance(right, (int, Fraction)):
            result = [x*right for x in left]
            if step_callback:
                step_callback(f"{right} * {vec_str(left)}", result)
            return result

        # Escalar * vector
        elif isinstance(left, (int, Fraction)) and isinstance(right, list):
            result = [left*x for x in right]
            if step_callback:
                step_callback(f"{left} * {vec_str(right)}", result)
            return result

        # Números puros
        else:
            return left*right if op=="*" else eval(f"{left}{op}{right}")

    def parse_product(index):
        left, index = parse_term(index)
        while index < len(tokens) and tokens[index] in ("*", "·"):
            op = tokens[index]
            right, index = parse_term(index + 1)
            left = apply_op(left, op, right)
        return left, index

    def parse_sum(index):
        left, index = parse_product(index)
        while index < len(tokens) and tokens[index] in ("+", "-"):
            op = tokens[index]
            right, index = parse_product(index + 1)
            left = apply_op(left, op, right)
        return left, index

    result, next_index = parse_sum(0)
    if next_index != len(tokens):
        raise ValueError("Error al parsear expresión")
    return result

def evaluate_expression(expr, vectors, step_callback=None):
    """
    Evalúa la expresión vectorial con fracciones y paso a paso.
    expr: str, p.ej. "1/2*u1 + 3*u2 - u3"
    vectors: dict, p.ej. {"u1": [1,2], "u2": [3,4], "u3": [5,6]}
    """
    # Convertir vectores a Fracciones
    vectors_frac = {}
    for name, vec in vectors.items():
        vectors_frac[name] = [Fraction(v) for v in vec]

    # Tokenizar
    tokens = tokenize(expr)
    result = parse_expression(tokens, vectors_frac, step_callback)
    return [v for v in result] if isinstance(result, list) else result