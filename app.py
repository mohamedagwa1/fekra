from flask import Flask, request, jsonify
#from flask_cors import CORS 
from lexer import lexer
from parser import Parser
from semantic_analyzer import SemanticAnalyzer
from intermediate_code_generator import IntermediateCodeGenerator
from optimizer import Optimizer
from target_code_generator import TargetCodeGenerator
from virtual_machine import VirtualMachine

app = Flask(__name__)

#CORS(app)

@app.route('/run', methods=['POST'])
def run_code():
    try:
        # Extract the code from the request
        data = request.json
        code = data.get("code", "")
        
        if not code:
            return jsonify({"error": "No code provided"}), 400
        
        # Step 1: Tokenize the source code
        tokens = lexer(code)
        
        # Step 2: Parse tokens into an AST
        parser = Parser(tokens)
        ast = parser.parse_program()
        
        # Step 3: Perform semantic analysis
        semantic_analyzer = SemanticAnalyzer(ast)
        try:
            semantic_analyzer.analyze()
        except ValueError as e:
            return jsonify({"error": f"Semantic analysis error: {e}"}), 400
        
        # Step 4: Generate Intermediate Code
        icg = IntermediateCodeGenerator(ast)
        ir_code = icg.generate()
        
        # Step 5: Optimize Intermediate Code
        # optimizer = Optimizer(ir_code)
        # optimized_code = optimizer.optimize()
        
        # Step 6: Generate Target Code
        tcg = TargetCodeGenerator(ir_code)
        target_code = tcg.generate()
        
        # Step 7: Execute with Virtual Machine
        vm = VirtualMachine(target_code)
        output = vm.run()
        
        # Return all stages as a response
        return jsonify({
            "tokens": tokens,
            "ast": ast,
            "ir_code": ir_code,
            "target_code": target_code,
            "output": output
        }), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

if __name__ == "__main__":
    # Use the PORT environment variable provided by Render, default to 5000 locally
    #port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
