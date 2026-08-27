def eval_vector_expression(variables, expression):
    """
    variables: dict, nombre del vector -> lista de números
    expression: str, por ejemplo "4*u + (-3)*v"
    
    Returns:
        dict con pasos y resultado final
    """
    steps = []

    # 1. Reemplazar nombres de vectores en la expresión por listas
    expr = expression
    for name, vec in variables.items():
        expr = expr.replace(name, f"variables['{name}']")
    
    # 2. Evalua la expresión (solo operaciones con listas y números)
    # Sobreescribimos operaciones para que + y - hagan suma/resta de vectores
    def vector_add(a, b):
        return [x+y for x,y in zip(a,b)]
    def vector_sub(a, b):
        return [x-y for x,y in zip(a,b)]
    def vector_mul(a, b):
        # Si b es lista: multiplicación elemento a elemento
        if isinstance(b, list):
            return [x*y for x,y in zip(a,b)]
        return [x*b for x in a]
    
    local_dict = {"variables": variables, "vector_add": vector_add,
                  "vector_sub": vector_sub, "vector_mul": vector_mul}

    # Reescribir la expresión para usar vector_add/vector_sub/vector_mul
    expr = expr.replace("+", ", vector_add(").replace("-", ", vector_sub(")  # idea inicial
    # O podemos usar parsing más seguro

    # Aquí podemos usar eval de manera controlada
    try:
        result = eval(expression, {"__builtins__": None}, local_dict)
        steps.append(f"Resultado final: {result}")
    except Exception as e:
        steps.append(f"Error evaluando expresión: {e}")
        result = None

    return {"steps": steps, "result": result}