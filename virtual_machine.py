class VirtualMachine:
    def __init__(self, instructions):
        self.instructions = instructions
        self.stack = []
        self.memory = {}
        self.labels = self.scan_labels()
        self.pc = 0  # Program counter

    def scan_labels(self):
        labels = {}
        for index, instr in enumerate(self.instructions):
            if instr.startswith("LABEL"):
                _, label_name = instr.split()
                labels[label_name] = index
        return labels

    def debug_state(self):
        print(f"PC: {self.pc}, Instruction: {self.instructions[self.pc]}")
        print(f"Stack: {self.stack}")
        print(f"Memory: {self.memory}")
        print("-------------")

    def run(self):
        output = []
        while self.pc < len(self.instructions):
            self.debug_state()
            instr = self.instructions[self.pc]
            result = self.execute(instr)
            if result is not None:
                output.append(result)
            self.pc += 1
        return output

    def execute(self, instr):
        parts = instr.split()
        command = parts[0]

        if command == "PUSH":
            self.handle_push(parts[1:])
        elif command == "STORE":
            self.handle_store(parts[1:])
        elif command in {"ADD", "SUB", "MUL", "DIV"}:
            self.handle_arithmetic(command)
        elif command.startswith("COMPARE"):
            self.handle_comparison(command)
        elif command == "PRINT":
            return self.handle_print()
        elif command == "JUMP":
            self.handle_jump(parts[1:])
        elif command == "JUMP_IF_TRUE":
            self.handle_jump_if_true(parts[1:])
        elif command.startswith("LABEL"):
            pass
        else:
            raise ValueError(f"Unknown instruction: {instr}")

    def handle_push(self, args):
        value = " ".join(args)
        if value.startswith('"') and value.endswith('"'):
            self.stack.append(value.strip('"'))
        elif value in self.memory:
            self.stack.append(self.memory[value])
        elif value.replace('.', '', 1).lstrip('-').isdigit():  # Handles integers and floats
            self.stack.append(float(value) if '.' in value else int(value))
        else:
            print(f"DEBUG: Undefined variable or invalid value: {value}")
            raise ValueError(f"Undefined variable or invalid value: {value}")

    def handle_store(self, args):
        if not self.stack:
            raise ValueError("Stack underflow: Cannot STORE without a value on the stack.")
        var_name = args[0]
        self.memory[var_name] = self.stack.pop()
        print(f"DEBUG: Stored {self.memory[var_name]} in {var_name}")

    def handle_arithmetic(self, command):
        if len(self.stack) < 2:
            raise ValueError("Stack underflow: Not enough values for arithmetic operation.")
        b = self.stack.pop()
        a = self.stack.pop()
        if command == "ADD":
            self.stack.append(a + b)
        elif command == "SUB":
            self.stack.append(a - b)
        elif command == "MUL":
            self.stack.append(a * b)
        elif command == "DIV":
            if b == 0:
                raise ZeroDivisionError("Division by zero.")
            self.stack.append(a / b)

    def handle_comparison(self, command):
        if len(self.stack) < 2:
            raise ValueError("Stack underflow: Not enough values for comparison.")
        b = self.stack.pop()
        a = self.stack.pop()
        if command == "COMPARE_GT":
            self.stack.append(1 if a > b else 0)
        elif command == "COMPARE_LT":
            self.stack.append(1 if a < b else 0)
        elif command == "COMPARE_EQ":
            self.stack.append(1 if a == b else 0)
        elif command == "COMPARE_NE":
            self.stack.append(1 if a != b else 0)

    def handle_print(self):
        if not self.stack:
            raise ValueError("Stack underflow: Nothing to PRINT.")
        value = self.stack.pop()
        print(f"OUTPUT: {value}")
        return value

    def handle_jump(self, args):
        label = args[0]
        if label not in self.labels:
            raise ValueError(f"Invalid jump label: {label}")
        self.pc = self.labels[label] - 1

    def handle_jump_if_true(self, args):
        if not self.stack:
            raise ValueError("Stack underflow: Nothing to evaluate for JUMP_IF_TRUE.")
        condition = self.stack.pop()
        label = args[0]
        if label not in self.labels:
            raise ValueError(f"Invalid jump label: {label}")
        if condition:
            self.pc = self.labels[label] - 1
