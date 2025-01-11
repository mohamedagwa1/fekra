class SymbolTable:
    def __init__(self):
        self.stack = [{}]  # Stack to track scopes

    def enter_scope(self):
        self.stack.append({})

    def exit_scope(self):
        self.stack.pop()

    def declare(self, name, value_type):
        current_scope = self.stack[-1]
        if name in current_scope:
            raise ValueError(f"Variable '{name}' already declared in this scope.")
        current_scope[name] = value_type

    def lookup(self, name):
        for scope in reversed(self.stack):
            if name in scope:
                return scope[name]
        raise ValueError(f"Variable '{name}' not declared.")

class SemanticAnalyzer:
    def __init__(self, ast):
        self.ast = ast
        self.symbol_table = SymbolTable()

    def analyze(self):
        self.visit(self.ast)

    def visit(self, node):
        node_type = node["type"]
        if node_type == "Program":
            for statement in node["body"]:
                self.visit(statement)
        elif node_type == "VariableDecl":
            self.symbol_table.declare(node["id"], "any") 
            if node["init"]:
                self.visit(node["init"])
        elif node_type == "Identifier":
            self.symbol_table.lookup(node["name"])
        elif node_type == "IfStatement":
            self.visit(node["test"])
            self.symbol_table.enter_scope()
            for stmt in node["consequent"]:
                self.visit(stmt)
            self.symbol_table.exit_scope()
        elif node_type == "WhileStatement":
            self.visit(node["test"])
            self.symbol_table.enter_scope()
            for stmt in node["body"]:
                self.visit(stmt)
            self.symbol_table.exit_scope()
        elif node_type == "PrintStatement":
            self.visit(node["expression"])
        elif node_type == "BinaryExpression":
            self.visit(node["left"])
            self.visit(node["right"])
        elif node_type == "Literal":
            pass  # Literals are valid as-is
        else:
            # raise ValueError(f"Unknown AST node type: {node_type}")
            pass
