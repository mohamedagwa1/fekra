class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current_token(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def advance(self):
        self.pos += 1

    def match(self, token_type):
        token = self.current_token()
        if token and token[0] == token_type:
            self.advance()
            return token
        raise SyntaxError(f"Expected {token_type} at position {self.pos}, got {token}")

    def parse_program(self):
        statements = []
        while self.current_token():
            statements.append(self.parse_statement())
        return {"type": "Program", "body": statements}

    def parse_statement(self):
        token = self.current_token()
        if token[0] == "KEYWORD" and token[1] == "عرف":
            return self.parse_variable_decl()
        elif token[0] == "KEYWORD" and token[1] == "لو":
            return self.parse_if_statement()
        elif token[0] == "KEYWORD" and token[1] == "بينما":
            return self.parse_while_statement()
        elif token[0] == "KEYWORD" and token[1] == "دالة":
            return self.parse_function_decl()
        elif token[0] == "KEYWORD" and token[1] == "عرض":
            return self.parse_print_statement()
        elif token[0] == "IDENTIFIER":
            return self.parse_assignment_or_function_call()
        elif token[0] == "KEYWORD" and token[1] == "اعد":
            return self.parse_return_statement()
        elif token[0] == "COMMENT":
            return self.parse_comment()
        else:
            raise SyntaxError(f"Unexpected token {token} at position {self.pos}")

    def parse_variable_decl(self):
        self.match("KEYWORD")  # "عرف"
        identifier = self.match("IDENTIFIER")
        value = None
        if self.current_token() and self.current_token()[0] == "OPERATOR" and self.current_token()[1] == "=":
            self.advance()
            value = self.parse_expression()
        self.match("TERMINATOR")  # "؟"
        return {"type": "VariableDecl", "id": identifier[1], "init": value}
    
    # 1-7-2025
    def parse_assignment_or_function_call(self):
        identifier = self.match("IDENTIFIER")[1]
        if self.current_token() and self.current_token()[0] == "OPERATOR" and self.current_token()[1] == "=":
            # Assignment
            self.match("OPERATOR")  # "="
            value = self.parse_expression()
            self.match("TERMINATOR")  # "؟"
            return {"type": "Assignment", "id": identifier, "value": value}
        elif self.current_token() and self.current_token()[0] == "LPAREN":
            # Function call
            return self.parse_function_call(identifier)
        else:
            raise SyntaxError(f"Expected assignment or function call at position {self.pos}")
    
    def parse_function_call(self, identifier):
        self.match("LPAREN")
        args = []
        if self.current_token() and self.current_token()[0] != "RPAREN":
            args.append(self.parse_expression())
            while self.current_token() and self.current_token()[0] == "COMMA":
                self.advance()
                args.append(self.parse_expression())
        self.match("RPAREN")
        
        if self.current_token() and self.current_token()[0] == "TERMINATOR":
            self.match("TERMINATOR") 

        return {"type": "FunctionCall", "callee": identifier, "arguments": args}

    

    def parse_expression(self):
        return self.parse_logical_expr()

    def parse_logical_expr(self):
        left = self.parse_comparison_expr()
        while self.current_token() and self.current_token()[0] == "OPERATOR" and self.current_token()[1] in ("&&", "||"):
            operator = self.match("OPERATOR")
            right = self.parse_comparison_expr()
            left = {"type": "LogicalExpression", "operator": operator[1], "left": left, "right": right}
        return left

    def parse_comparison_expr(self):
        left = self.parse_arith_expr()
        while self.current_token() and self.current_token()[0] == "COMPARISON_OP":
            operator = self.match("COMPARISON_OP")
            right = self.parse_arith_expr()
            left = {"type": "BinaryExpression", "operator": operator[1], "left": left, "right": right}
        return left

    def parse_arith_expr(self):
        left = self.parse_term()
        while self.current_token() and self.current_token()[0] == "OPERATOR" and self.current_token()[1] in ("+", "-"):
            operator = self.match("OPERATOR")
            right = self.parse_term()
            left = {"type": "BinaryExpression", "operator": operator[1], "left": left, "right": right}
        return left

    def parse_term(self):
        left = self.parse_factor()
        while self.current_token() and self.current_token()[0] == "OPERATOR" and self.current_token()[1] in ("*", "/"):
            operator = self.match("OPERATOR")
            right = self.parse_factor()
            left = {"type": "BinaryExpression", "operator": operator[1], "left": left, "right": right}
        return left

    def parse_factor(self):
        token = self.current_token()
        if token[0] == "NUMBER":
            self.advance()
            return {"type": "Literal", "value": int(token[1])}
        elif token[0] == "STRING":
            self.advance()
            return {"type": "Literal", "value": token[1]}
        elif token[0] == "IDENTIFIER":
            identifier = self.match("IDENTIFIER")[1]
            if self.current_token() and self.current_token()[0] == "LPAREN":
                return self.parse_function_call(identifier)
            else:
                return {"type": "Identifier", "name": identifier}
        elif token[0] == "LPAREN":
            self.advance()
            expr = self.parse_expression()
            self.match("RPAREN")
            return expr
        else:
            raise SyntaxError(f"Unexpected token {token} at position {self.pos}")

    def parse_if_statement(self):
        self.match("KEYWORD")  # "لو"
        self.match("LPAREN")
        condition = self.parse_expression()
        self.match("RPAREN")
        self.match("LBRACE")
        body = []
        while self.current_token() and self.current_token()[0] != "RBRACE":
            body.append(self.parse_statement())
        self.match("RBRACE")
        return {"type": "IfStatement", "test": condition, "consequent": body}

    def parse_while_statement(self):
        self.match("KEYWORD")  # "بينما"
        self.match("LPAREN")
        condition = self.parse_expression()
        self.match("RPAREN")
        self.match("LBRACE")
        body = []
        while self.current_token() and self.current_token()[0] != "RBRACE":
            body.append(self.parse_statement())
        self.match("RBRACE")
        return {"type": "WhileStatement", "test": condition, "body": body}

    def parse_function_decl(self):
        self.match("KEYWORD")  # "دالة"
        name = self.match("IDENTIFIER")[1]
        self.match("LPAREN")
        params = []
        if self.current_token() and self.current_token()[0] == "IDENTIFIER":
            params.append(self.match("IDENTIFIER")[1])
            while self.current_token() and self.current_token()[0] == "COMMA":
                self.advance()
                params.append(self.match("IDENTIFIER")[1])
        self.match("RPAREN")
        self.match("LBRACE")
        body = []
        while self.current_token() and self.current_token()[0] != "RBRACE":
            body.append(self.parse_statement())
        self.match("RBRACE")
        return {"type": "FunctionDeclaration", "name": name, "params": params, "body": body}
    
    def parse_return_statement(self):
        self.match("KEYWORD")
        self.match("LPAREN") 
        value = None
        if self.current_token() and self.current_token()[0] != "RPAREN":
            value = self.parse_expression()
        self.match("RPAREN")  
        self.match("TERMINATOR")  
        return {"type": "ReturnStatement", "value": value}

    
    def parse_comment(self):
        comment = self.match("COMMENT")
        return {"type": "Comment", "value": comment[1]}

    def parse_print_statement(self):
        self.match("KEYWORD")  # "عرض"
        self.match("LPAREN")
        expr = self.parse_expression()
        self.match("RPAREN")
        self.match("TERMINATOR")
        return {"type": "PrintStatement", "expression": expr}
    
