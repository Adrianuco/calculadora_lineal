from fractions import Fraction
import copy
import re

def to_fraction(x):
    """Convierte int/float/str/Fraction a Fraction."""
    if isinstance(x, Fraction):
        return x
    if isinstance(x, int):
        return Fraction(x)
    if isinstance(x, float):
        return Fraction(x).limit_denominator()
    if isinstance(x, str):
        s = x.strip()
        try:
            return Fraction(s)
        except Exception:
            return Fraction(float(s)).limit_denominator()
    raise ValueError(f"Tipo no soportado: {type(x)}")

def matrix_to_fraction(A):
    """Copia profunda convirtiendo todo a Fraction."""
    return [[to_fraction(x) for x in row] for row in copy.deepcopy(A)]

def pretty_frac(f: Fraction):
    """Formato legible para fracciones."""
    return str(f.numerator) if f.denominator == 1 else f"{f.numerator}/{f.denominator}"

class Matrix:
    def __init__(self, data, name=None, steps=None):
        self.data = matrix_to_fraction(data)
        self.rows = len(self.data)
        self.cols = len(self.data[0]) if self.rows > 0 else 0
        self.name = name
        self.steps = steps if steps is not None else []

    def copy(self):
        return Matrix(copy.deepcopy(self.data), name=self.name, steps=self.steps)

    @property
    def T(self):
        """Transpuesta de la matriz."""
        trans = [[self.data[i][j] for i in range(self.rows)] for j in range(self.cols)]
        op = f"({self.name})^T" if self.name else "( )^T"
        self.steps.append({
            "descripcion": op,
            "matriz": copy.deepcopy(trans)
        })
        return Matrix(trans, name=op, steps=self.steps)

    def __add__(self, other):
        if not isinstance(other, Matrix):
            raise ValueError("Solo se pueden sumar matrices entre sí.")
        if self.rows != other.rows or self.cols != other.cols:
            raise ValueError(f"No se pudo sumar {self.name} y {other.name} porque sus dimensiones son distintas.")
        res = [[self.data[i][j] + other.data[i][j] for j in range(self.cols)] for i in range(self.rows)]
        op = f"{self.name} + {other.name}"
        self.steps.append({"descripcion": op, "matriz": copy.deepcopy(res)})
        return Matrix(res, name=op, steps=self.steps)

    def __sub__(self, other):
        if not isinstance(other, Matrix):
            raise ValueError("Solo se pueden restar matrices entre sí.")
        if self.rows != other.rows or self.cols != other.cols:
            raise ValueError(f"No se pudo restar {self.name} y {other.name} porque sus dimensiones son distintas.")
        res = [[self.data[i][j] - other.data[i][j] for j in range(self.cols)] for i in range(self.rows)]
        op = f"{self.name} - {other.name}"
        self.steps.append({"descripcion": op, "matriz": copy.deepcopy(res)})
        return Matrix(res, name=op, steps=self.steps)

    def __mul__(self, other):
        if isinstance(other, Matrix):
            if self.cols != other.rows:
                raise ValueError(f"No se pudo multiplicar {self.name} y {other.name} por incompatibilidad de dimensiones.")
            C = [[Fraction(0) for _ in range(other.cols)] for _ in range(self.rows)]
            for i in range(self.rows):
                for j in range(other.cols):
                    s = Fraction(0)
                    for k in range(self.cols):
                        s += self.data[i][k] * other.data[k][j]
                    C[i][j] = s
            op = f"{self.name}{other.name}"  # sin asterisco
            self.steps.append({"descripcion": op, "matriz": copy.deepcopy(C)})
            return Matrix(C, name=op, steps=self.steps)
        else:
            s = to_fraction(other)
            C = [[s * self.data[i][j] for j in range(self.cols)] for i in range(self.rows)]
            op = f"{pretty_frac(s)}{self.name}"
            self.steps.append({"descripcion": op, "matriz": copy.deepcopy(C)})
            return Matrix(C, name=op, steps=self.steps)

    def __rmul__(self, other):
        s = to_fraction(other)
        C = [[s * self.data[i][j] for j in range(self.cols)] for i in range(self.rows)]
        op = f"{pretty_frac(s)}({self.name})"
        self.steps.append({"descripcion": op, "matriz": copy.deepcopy(C)})
        return Matrix(C, name=op, steps=self.steps)

    def as_list(self):
        return [[to_fraction(x) for x in row] for row in self.data]

    def __repr__(self):
        return f"<Matrix {self.rows}x{self.cols}>"

def parse_scalar_definitions(text):
    """Texto como 'r=2, s=1/2' -> {'r': Fraction(2), 's': Fraction(1,2)}"""
    res = {}
    if not text:
        return res
    parts = [p.strip() for p in text.split(",") if p.strip()]
    for p in parts:
        if "=" not in p:
            continue
        name, val = p.split("=", 1)
        name, val = name.strip(), val.strip()
        res[name] = to_fraction(val)
    return res

def _insert_implicit_multiplication(expr: str) -> str:
    expr = re.sub(r"(?<=\))(?=[A-Z\(])", "*", expr)
    expr = re.sub(r"(?<=\d)(?=[A-Z\(])", "*", expr)
    expr = re.sub(r"(?<=[A-Z])(?=\()", "*", expr)
    expr = re.sub(r"(?<=[A-Z])\s+(?=[A-Z])", "*", expr)
    return expr

def _replace_transpose_notation(expr: str) -> str:
    expr = re.sub(r"([A-Z])\^T\b", r"\1.T", expr)
    expr = re.sub(r"([A-Z])T\b", r"\1.T", expr)
    expr = re.sub(r"(\))\^T\b", r"\1.T", expr)
    expr = re.sub(r"(\))T\b", r"\1.T", expr)
    return expr

def evaluate_matrix_expression(expr: str, matrices: dict, scalars_text: str = ""):
    """
    Evalúa expresiones matriciales con matrices y escalares opcionales.
    Devuelve (resultado_matrix_as_list, pasos_list).
    """
    if not expr or expr.strip() == "":
        raise ValueError("Expresión vacía")

    steps = []

    env = {}
    for name, mat in matrices.items():
        if not re.fullmatch(r"[A-Z]", name):
            raise ValueError(f"Nombre de matriz inválido: {name}")
        env[name] = Matrix(mat, name=name, steps=steps)

    scalars = parse_scalar_definitions(scalars_text)
    for k, v in scalars.items():
        if not re.fullmatch(r"[a-z]\w*", k):
            raise ValueError(f"Nombre de escalar inválido: {k}")
        env[k] = v

    e = expr.replace(" ", "")
    e = _replace_transpose_notation(e)
    e = _insert_implicit_multiplication(e)

    if re.search(r"[^0-9A-Za-z\+\-\*\/\^\(\)\.\,]", e):
        raise ValueError("La expresión contiene caracteres no permitidos.")

    try:
        result = eval(e, {"__builtins__": None}, dict(env))
    except Exception as exc:
        msg = str(exc)
        msg = re.sub(r'\(.*line.*\)', '', msg)
        raise ValueError(f"Error al evaluar la expresión. {msg.strip()}")

    if isinstance(result, Matrix):
        return result.as_list(), steps
    else:
        raise ValueError("La expresión no produjo una matriz. Verifica las operaciones y dimensiones.")