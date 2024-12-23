class TargetCodeGenerator:
    def __init__(self, optimized_code):
        self.optimized_code = optimized_code
        self.target_code = []
        self.label_counter = 0

    def new_label(self):
        self.label_counter += 1
        return f"L{self.label_counter}"

    def generate(self):
        for line in self.optimized_code:
            self.translate(line)
        return self.target_code

    def translate(self, line):
        print(f"Translating IR Line: {line}")
        if "print" in line:
            self.handle_print(line)
        elif "=" in line:
            target, expr = map(str.strip, line.split("=", maxsplit=1))
            if any(op in expr for op in [">", "<", "==", ">=", "<=", "!="]):
                self.handle_comparison(target, expr)
            elif any(op in expr for op in ["+", "-", "*", "/"]):
                self.handle_arithmetic(target, expr)
            else:
                self.add_push(expr)
                self.target_code.append(f"STORE {target}")
        elif "if" in line:
            self.handle_if(line)
        elif "goto" in line:
            self.handle_goto(line)
        elif ":" in line:
            self.handle_label(line)
        else:
            raise ValueError(f"Unsupported line: {line}")
        
    def handle_print(self, line):
        # Extract the value to be printed
        _, value = line.split(maxsplit=1)

        # Check if the value is a string literal (with quotes)
        if value.startswith('"') and value.endswith('"'):
            self.add_push(value)  # Preserve the quotes for string literals
        elif value.isidentifier():  # Check if it's a valid identifier
            self.add_push(value)
        else:
            raise ValueError(f"Invalid print value: {value}")

        self.target_code.append("PRINT")


    def handle_comparison(self, target, expr):
        left, op, right = map(str.strip, expr.split())
        self.add_push(left)
        self.add_push(right)
        operator_map = self.get_operator_map()
        if op in operator_map:
            self.target_code.append(operator_map[op])
        else:
            raise ValueError(f"Unknown comparison operator: {op}")
        self.target_code.append(f"STORE {target}")

    def handle_arithmetic(self, target, expr):
        operands = expr.split()
        self.add_push(operands[0])
        self.add_push(operands[2])
        operator_map = {
            "+": "ADD",
            "-": "SUB",
            "*": "MUL",
            "/": "DIV",
        }
        op = operands[1]
        if op in operator_map:
            self.target_code.append(operator_map[op])
        else:
            raise ValueError(f"Unknown arithmetic operator: {op}")
        self.target_code.append(f"STORE {target}")

    def handle_if(self, line):
        # Split the "if" statement into components
        _, condition, _, label = line.split()

        # Check if the condition is a simple variable
        if condition.isidentifier():
            self.add_push(condition)  # Push the variable to the stack
            self.target_code.append(f"JUMP_IF_TRUE {label}")
        else:
            # Handle complex conditions (e.g., "t1 > 5")
            if any(op in condition for op in [">", "<", "==", ">=", "<=", "!="]):
                left, op, right = self.parse_condition(condition)
                self.add_push(left)
                self.add_push(right)
                operator_map = self.get_operator_map()
                if op in operator_map:
                    self.target_code.append(operator_map[op])
                else:
                    raise ValueError(f"Unknown comparison operator: {op}")
                self.target_code.append(f"JUMP_IF_TRUE {label}")
            else:
                raise ValueError(f"Invalid condition format: {condition}")

    def parse_condition(self, condition):
        """Helper method to parse a condition into left operand, operator, and right operand."""
        for op in [">=", "<=", "!=", "==", ">", "<"]:
            if op in condition:
                left, right = map(str.strip, condition.split(op, maxsplit=1))
                return left, op, right
        raise ValueError(f"Unable to parse condition: {condition}")


    def handle_goto(self, line):
        _, label = line.split()
        self.target_code.append(f"JUMP {label}")

    def handle_label(self, line):
        label = line.strip(":")
        self.target_code.append(f"LABEL {label}")
        

    def add_push(self, value):
        """Utility function to add a PUSH operation."""
        value = value.strip()
        if value.isdigit():
            self.target_code.append(f"PUSH {value}")
        elif value.isidentifier():
            self.target_code.append(f"PUSH {value}")
        elif value.startswith('"') and value.endswith('"'):
            # Handle string literals with surrounding quotes preserved
            self.target_code.append(f'PUSH {value}')
        else:
            raise ValueError(f"Invalid or undefined value: {value}")


    def get_operator_map(self):
        """Returns a map of comparison operators to VM instructions."""
        return {
            ">": "COMPARE_GT",
            "<": "COMPARE_LT",
            "==": "COMPARE_EQ",
            "!=": "COMPARE_NE",
            ">=": "COMPARE_GTE",
            "<=": "COMPARE_LTE",
        }
