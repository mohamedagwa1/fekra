from lexer import lexer
from parser import Parser
from semantic_analyzer import SemanticAnalyzer
from intermediate_code_generator import IntermediateCodeGenerator
from optimizer import Optimizer
from target_code_generator import TargetCodeGenerator
from virtual_machine import VirtualMachine

# Input source code
code = """
عرف س = 10 ؟
لو (س > 5) {
    عرض ("س اكبر من 5") ؟
}
"""

code2 = """
عرف عدد = 20 ؟
عرف ناتج = 1 ؟
لو (ناتج < عدد){
     عرض ("ناتج اصغر من عدد") ؟
}

لو (ناتج > عدد){
     عرض ("ناتج اكبر من عدد") ؟
}

"""

# Step 1: Tokenize the source code
tokens = lexer(code2)
print("Tokens:", tokens)

# Step 2: Parse tokens into an AST
parser = Parser(tokens)
ast = parser.parse_program()
print("AST:", ast)

# Step 3: Perform semantic analysis
semantic_analyzer = SemanticAnalyzer(ast)
try:
    semantic_analyzer.analyze()
    print("Semantic analysis passed!")
except ValueError as e:
    print(f"Semantic analysis error: {e}")

# Step 4: Generate Intermediate Code
icg = IntermediateCodeGenerator(ast)
ir_code = icg.generate()
print("Intermediate Code:")
print("\n".join(ir_code))

# Step 5: Optimize Intermediate Code
optimizer = Optimizer(ir_code)
optimized_code = optimizer.optimize()
print("Optimized Code:")
print("\n".join(optimized_code))

# Step 6: Generate Target Code
tcg = TargetCodeGenerator(ir_code)
target_code = tcg.generate()
print("Target Code:")
print("\n".join(target_code))

# Step 7: Execute with Virtual Machine
vm = VirtualMachine(target_code)
output = vm.run()
print("VM Execution Output:")
print(output)
