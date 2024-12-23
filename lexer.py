import re

# Lexer Configuration
KEYWORDS = {"عرف", "لو", "بينما", "دالة", "عرض", "اعد", "؟", "//", "/*", "*/"}
COMPARISON_OPS = {"==", "!=", "<", "<=", ">", ">=", "===", "!=="}
OPERATORS = {"+", "-", "*", "/", "&&", "||", "!", "="}

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
        elif kind in ['COMMENT', 'KEYWORD', 'IDENTIFIER', 'NUMBER', 'STRING', 
                      'COMPARISON_OP', 'OPERATOR', 'LPAREN', 'RPAREN', 
                      'LBRACE', 'RBRACE', 'COMMA', 'TERMINATOR']:
            tokens.append((kind, value))
        elif kind == 'NEWLINE':
            line_num += 1
            line_start = mo.end()
        elif kind == 'MISMATCH':
            raise RuntimeError(
                f'Unexpected character {value!r} at line {line_num}, column {column + 1}'
            )
    return tokens
