class VirtualMachine:
    def __init__(self, instructions):
        self.instructions = instructions
        self.stack = []
        self.memory = {}
        self.labels = self.scan_labels()
        self.functions = {}
        self.call_stack = []
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
        elif command == "RETURN":
            self.handle_return()
        elif command == "FUNC_DEFINE":
            self.handle_func_define(parts[1])
        elif command == "FUNC_START":
            pass  
        elif command == "FUNC_END":
            self.handle_func_end() 
        elif command == "PARAM":
            self.handle_param(parts[1])
        elif command == "CALL":
            self.handle_call(parts[1])
        elif command in {"ADD", "SUB", "MUL", "DIV"}:
            self.handle_arithmetic(command)
        elif command.startswith("COMPARE"):
            self.handle_comparison(command)
        elif command in {"LOGICAL_AND", "LOGICAL_OR"}:
            self.handle_logical(command)
        elif command == "PRINT":
            return self.handle_print()
        elif command == "JUMP":
            self.handle_jump(parts[1:])
        elif command == "JUMP_IF_TRUE":
            self.handle_jump_if_true(parts[1:])
        elif command == "JUMP_IF_FALSE":
            self.handle_jump_if_false(parts[1:])
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
        elif command == "COMPARE_GTE":
            self.stack.append(1 if a >= b else 0)
        elif command == "COMPARE_LTE":
            self.stack.append(1 if a <= b else 0)

    def handle_logical(self, command):
        if len(self.stack) < 2:
            raise ValueError("Stack underflow: Not enough values for logical operation.")
        b = self.stack.pop()
        a = self.stack.pop()
        if command == "LOGICAL_AND":
            self.stack.append(1 if a and b else 0)
        elif command == "LOGICAL_OR":
            self.stack.append(1 if a or b else 0)

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
    def handle_jump_if_false(self, args):
        if not self.stack:
            raise ValueError("Stack underflow: Nothing to evaluate for JUMP_IF_FALSE.")
        condition = self.stack.pop()
        label = args[0]
        if label not in self.labels:
            raise ValueError(f"Invalid jump label: {label}")
        if not condition:
            self.pc = self.labels[label] - 1
    


    def handle_func_define(self, func_name):
        self.functions[func_name] = self.pc + 1
        # Skip to FUNC_END
        while not self.instructions[self.pc].startswith("FUNC_END"):
            if self.pc >= len(self.instructions):
                raise ValueError(f"FUNC_END not found for function {func_name}")
            self.pc += 1

    def handle_param(self, param_name):
        if not self.call_stack:
            raise ValueError("No active function call to assign parameter.")
        if not self.stack:
            raise ValueError("Stack underflow: Cannot assign parameter without a value on the stack.")
        value = self.stack.pop(0)
        self.memory[param_name] = value

    def handle_call(self, func_name):
        if func_name not in self.functions:
            raise ValueError(f"Undefined function: {func_name}")
        self.call_stack.append(self.pc)  # Save the current program counter
        self.pc = self.functions[func_name] - 1  # Jump to the function's start

    def handle_return(self):
        if self.call_stack:
            self.pc = self.call_stack.pop() 
    
    def handle_func_end(self):
        if self.call_stack:
            self.pc = self.call_stack.pop() 
