import re

token_specification = [
    ('NUMBER',    r'\d+'),              # Integer
    ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z_0-9]*'), # Identifiers
    ('ASSIGN',    r'='),                # Assignment operator
    ('END',       r';'),                # Statement terminator
    ('PLUS',      r'\+'),               # Addition operator
    ('MINUS',     r'-'),                # Subtraction operator
    ('TIMES',     r'\*'),               # Multiplication operator
    ('DIVIDE',    r'/'),                # Division operator
    ('LPAREN',    r'\('),               # Left Parenthesis
    ('RPAREN',    r'\)'),               # Right Parenthesis
    ('SKIP',      r'[ \t]+'),           # Skip over spaces and tabs
    ('NEWLINE',   r'\n'),               # Line endings
    ('MISMATCH',  r'.'),                # Any other character
]

def tokenize(code):
    tokens = []
    line_num = 1
    line_start = 0
    for mo in re.finditer('|'.join('(?P<%s>%s)' % pair for pair in token_specification), code):
        kind = mo.lastgroup
        value = mo.group(kind)
        column = mo.start() - line_start
        if kind == 'NUMBER':
            value = int(value)
        elif kind == 'SKIP' or kind == 'NEWLINE':
            if kind == 'NEWLINE':
                line_num += 1
                line_start = mo.end()
            continue
        elif kind == 'MISMATCH':
            raise RuntimeError(f'{value!r} unexpected on line {line_num}')
        tokens.append((kind, value, line_num, column))
    return tokens


# Parser class
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.symbols = set()  # For semantic analysis

    def expect(self, token_type):
        if self.tokens[self.pos][0] == token_type:
            self.pos += 1
        else:
            self.error(token_type)

    def error(self, expected):
        raise SyntaxError(f"Expected {expected} at {self.tokens[self.pos]}")

    def parse(self):
        while self.pos < len(self.tokens):
            self.statement()

    def statement(self):
        if self.tokens[self.pos][0] == 'IDENTIFIER':
            self.assignment()
        elif self.tokens[self.pos][0] == 'NUMBER':
            self.expression()
        elif self.tokens[self.pos][0] == 'int':
            self.var_decl()
        else:
            self.error('statement')

    def var_decl(self):
        self.expect('int')
        identifier = self.tokens[self.pos][1]
        self.symbols.add(identifier)
        self.expect('IDENTIFIER')
        self.expect('END')

    def assignment(self):
        identifier = self.tokens[self.pos][1]
        if identifier not in self.symbols:
            raise NameError(f"Variable {identifier} not declared")
        self.expect('IDENTIFIER')
        self.expect('ASSIGN')
        self.expression()
        self.expect('END')

    def expression(self):
        self.term()
        while self.tokens[self.pos][0] in ('PLUS', 'MINUS'):
            self.pos += 1
            self.term()

    def term(self):
        self.factor()
        while self.tokens[self.pos][0] in ('TIMES', 'DIVIDE'):
            self.pos += 1
            self.factor()

    def factor(self):
        token = self.tokens[self.pos]
        if token[0] == 'NUMBER':
            self.pos += 1
        elif token[0] == 'IDENTIFIER':
            if token[1] not in self.symbols:
                raise NameError(f"Variable {token[1]} not declared")
            self.pos += 1
        elif token[0] == 'LPAREN':
            self.pos += 1
            self.expression()
            self.expect('RPAREN')
        else:
            self.error('factor')

# Main function to take user input and compile
def main():
    print("Enter your program code (end input with an empty line):")
    code = []
    while True:
        line = input()
        if line == "":
            break
        code.append(line)
    code = "\n".join(code)

    # Tokenize the code
    tokens = tokenize(code)
    print("\nTokens:")
    for token in tokens:
        print(token)

    # Parse the tokens
    parser = Parser(tokens)
    try:
        parser.parse()
        print("\nParsing completed successfully.")
    except (SyntaxError, NameError) as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
