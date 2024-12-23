class Optimizer:
    def __init__(self, code):
        self.code = code

    def optimize(self):
        self.constant_folding()
        self.dead_code_elimination()
        self.common_subexpression_elimination()
        return self.code

    def constant_folding(self):
        """Evaluate constant expressions and replace them with results."""
        import ast
        import operator

        def safe_eval(expr):
            """Safely evaluate simple arithmetic expressions."""
            allowed_operators = {
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
                ast.Div: operator.truediv,
            }

            def eval_node(node):
                if isinstance(node, ast.BinOp) and type(node.op) in allowed_operators:
                    left = eval_node(node.left)
                    right = eval_node(node.right)
                    return allowed_operators[type(node.op)](left, right)
                elif isinstance(node, ast.Num):
                    return node.n
                else:
                    raise ValueError("Unsupported expression")

            try:
                tree = ast.parse(expr, mode="eval")
                return eval_node(tree.body)
            except Exception:
                return None

        new_code = []
        for line in self.code:
            if "=" in line and any(op in line for op in "+-*/"):
                parts = line.split("=")
                target = parts[0].strip()
                expr = parts[1].strip()
                result = safe_eval(expr)
                if result is not None:
                    new_code.append(f"{target} = {result}")
                else:
                    new_code.append(line)
            else:
                new_code.append(line)
        self.code = new_code

    def dead_code_elimination(self):
        used_vars = set()
        new_code = []
        for line in reversed(self.code):
            if "=" in line:
                target = line.split("=")[0].strip()
                if target in used_vars or "if" in line or "goto" in line or "print" in line:
                    used_vars.update(line.split())  # Add used vars
                    new_code.insert(0, line)
                else:
                    # Remove unused assignments
                    pass
            else:
                new_code.insert(0, line)
        self.code = new_code

    def common_subexpression_elimination(self):
        """Eliminate redundant evaluations of the same expression."""
        expr_map = {}
        new_code = []
        for line in self.code:
            if "=" in line and any(op in line for op in "+-*/"):
                parts = line.split("=")
                target = parts[0].strip()
                expr = parts[1].strip()
                if expr in expr_map:
                    new_code.append(f"{target} = {expr_map[expr]}")
                else:
                    expr_map[expr] = target
                    new_code.append(line)
            else:
                new_code.append(line)
        self.code = new_code
