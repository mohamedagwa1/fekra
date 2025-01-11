import re

KEYWORDS = {
    "عرف", "لو", "بينما", "دالة", "عرض", "اعد", "؟", "//", "/*", "*/"
}

COMPARISON_OPS = {
    "==", "!=", "<", "<=", ">", ">=", "===", "!=="
}

OPERATORS = {
    "+", "-", "*", "/", "&&", "||", "!", "="
}

token_specification = [
    ('COMMENT', r'//[^\n]*|/\*.*?\*/'), 
    ('KEYWORD', r'\b(?:عرف|لو|بينما|دالة|عرض|اعد)\b'), 
    ('IDENTIFIER', r'[ء-ي_][ء-ي0-9_]*'),  
    ('NUMBER', r'\b\d+(\.\d*)?\b'), 
    ('STRING', r'"([^"\\]|\\.)*"|"""([^"\\]|\\.)*"""'), 
    ('COMPARISON_OP', r'==|!=|<=|>=|<|>|===|!=='), 
    ('OPERATOR', r'\+|\-|\*|\/|\&\&|\|\||\!|\='),  
    ('LPAREN', r'\('),  
    ('RPAREN', r'\)'), 
    ('LBRACE', r'\{'), 
    ('RBRACE', r'\}'), 
    ('COMMA', r','),  
    ('TERMINATOR', r'؟'),  
    ('SKIP', r'[ \t]+'),
    ('NEWLINE', r'\n'),
    ('MISMATCH', r'.'),  
]

master_pattern = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in token_specification)


def lexer(code):
    line_num = 1
    line_start = 0
    tokens = []
    for mo in re.finditer(master_pattern, code):
        kind = mo.lastgroup
        value = mo.group()
        column = mo.start() - line_start

        if kind == 'SKIP':
            continue
        elif kind == 'COMMENT':
            tokens.append(('COMMENT', value))
        elif kind == 'KEYWORD':
            tokens.append(('KEYWORD', value))
        elif kind == 'IDENTIFIER':
            tokens.append(('IDENTIFIER', value))
        elif kind == 'NUMBER':
            tokens.append(('NUMBER', value))
        elif kind == 'STRING':
            tokens.append(('STRING', value))
        elif kind == 'COMPARISON_OP':
            tokens.append(('COMPARISON_OP', value))
        elif kind == 'OPERATOR':
            tokens.append(('OPERATOR', value))
        elif kind == 'LPAREN':
            tokens.append(('LPAREN', value))
        elif kind == 'RPAREN':
            tokens.append(('RPAREN', value))
        elif kind == 'LBRACE':
            tokens.append(('LBRACE', value))
        elif kind == 'RBRACE':
            tokens.append(('RBRACE', value))
        elif kind == 'COMMA':
            tokens.append(('COMMA', value))
        elif kind == 'TERMINATOR':
            tokens.append(('TERMINATOR', value))
        elif kind == 'NEWLINE':
            line_num += 1
            line_start = mo.end()
        elif kind == 'MISMATCH':
            raise RuntimeError(
                f'start Unexpected character {value!r} at line {line_num}, column {column + 1} end'
            )

    return tokens

