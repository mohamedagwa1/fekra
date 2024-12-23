class IntermediateCodeGenerator:
    def __init__(self, ast):
        self.ast = ast
        self.code = []
        self.temp_counter = 0
        self.label_counter = 0

    def new_temp(self):
        self.temp_counter += 1
        return f"t{self.temp_counter}"

    def new_label(self):
        self.label_counter += 1
        return f"L{self.label_counter}"

    def generate(self):
        self.visit(self.ast)
        return self.code

    def visit(self, node):
        node_type = node["type"]
        if node_type == "Program":
            for statement in node["body"]:
                self.visit(statement)
        elif node_type == "VariableDecl":
            self.handle_variable_decl(node)
        elif node_type == "IfStatement":
            self.handle_if_statement(node)
        elif node_type == "BinaryExpression":
            return self.handle_binary_expression(node)
        elif node_type == "Literal":
            return str(node["value"])
        elif node_type == "Identifier":
            return node["name"]
        elif node_type == "PrintStatement":
            self.handle_print_statement(node)
        else:
            raise ValueError(f"Unknown AST node type: {node_type}")

    def handle_variable_decl(self, node):
        if node["init"]:
            expr_result = self.visit(node["init"])
            self.code.append(f"{node['id']} = {expr_result}")
        else:
            self.code.append(f"{node['id']} = 0")  # Default to 0

    def handle_if_statement(self, node):
        condition = self.visit(node["test"])
        temp_condition = self.new_temp()
        self.code.append(f"{temp_condition} = {condition}")
        true_label = self.new_label()
        end_label = self.new_label()
        self.code.append(f"if {temp_condition} goto {true_label}")
        self.code.append(f"goto {end_label}")
        self.code.append(f"{true_label}:")
        for stmt in node["consequent"]:
            self.visit(stmt)
        self.code.append(f"{end_label}:")

    def handle_binary_expression(self, node):
        left = self.visit(node["left"])
        right = self.visit(node["right"])
        temp = self.new_temp()
        self.code.append(f"{temp} = {left} {node['operator']} {right}")
        return temp

    def handle_print_statement(self, node):
        expr_result = self.visit(node["expression"])
        self.code.append(f"print {expr_result}")
