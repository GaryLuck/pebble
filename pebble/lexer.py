import sys

class TokenType:
    # Keywords
    IF = 'IF'
    ELSE = 'ELSE'
    WHILE = 'WHILE'
    FOR = 'FOR'
    RETURN = 'RETURN'
    INT = 'INT'
    STRING = 'STRING'
    BOOL = 'BOOL'
    VOID = 'VOID'
    TRUE = 'TRUE'
    FALSE = 'FALSE'
    FUNC = 'FUNC' # Implicitly handled? No, user said "func" is not a keyword, but return type is required.
    # Wait, the prompt said: "3. i'd like function definitions with arguments... func myFunc(arg) { ... } or is it a single main script?"
    # User response: "1. please require a return type... 6. yes, look for main() { ... }"
    # So syntax is `int add(int a, int b)`. No `func` keyword.

    # Literals
    INTEGER_LIT = 'INTEGER_LIT'
    STRING_LIT = 'STRING_LIT'

    # Identifiers
    IDENTIFIER = 'IDENTIFIER'

    # Operators
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    MUL = 'MUL'
    DIV = 'DIV'
    MOD = 'MOD'
    ASSIGN = 'ASSIGN'
    EQ = 'EQ'
    NEQ = 'NEQ'
    LT = 'LT'
    GT = 'GT'
    LTE = 'LTE'
    GTE = 'GTE'
    AND = 'AND'
    OR = 'OR'
    NOT = 'NOT'

    # Delimiters
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    LBRACE = 'LBRACE'
    RBRACE = 'RBRACE'
    LBRACKET = 'LBRACKET'
    RBRACKET = 'RBRACKET'
    SEMI = 'SEMI'
    COMMA = 'COMMA'

    EOF = 'EOF'

KEYWORDS = {
    'if': TokenType.IF,
    'else': TokenType.ELSE,
    'while': TokenType.WHILE,
    'for': TokenType.FOR,
    'return': TokenType.RETURN,
    'int': TokenType.INT,
    'string': TokenType.STRING,
    'bool': TokenType.BOOL,
    'void': TokenType.VOID,
    'true': TokenType.TRUE,
    'false': TokenType.FALSE,
}

class Token:
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, line={self.line}, col={self.column})"

    def __eq__(self, other):
        if isinstance(other, Token):
            return self.type == other.type and self.value == other.value
        return False

class LexerError(Exception):
    pass

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.current_char = self.text[self.pos] if self.text else None

    def error(self, msg=None):
        if msg is None:
            msg = f"Invalid character '{self.current_char}'"
        raise LexerError(f"{msg} at line {self.line}, column {self.column}")

    def advance(self):
        if self.current_char == '\n':
            self.line += 1
            self.column = 0

        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]
            self.column += 1

    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        return self.text[peek_pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def skip_comment(self):
        while self.current_char is not None and self.current_char != '\n':
            self.advance()
        # Ensure we consume the newline if present, or just let skip_whitespace handle it next time
        if self.current_char == '\n':
             self.advance()

    def number(self):
        result = ''
        start_col = self.column
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return Token(TokenType.INTEGER_LIT, int(result), self.line, start_col)

    def string(self):
        result = ''
        start_col = self.column
        self.advance()  # Skip opening quote
        while self.current_char is not None and self.current_char != '"':
            result += self.current_char
            self.advance()

        if self.current_char is None:
            raise LexerError(f"Unterminated string literal at line {self.line}")

        self.advance()  # Skip closing quote
        return Token(TokenType.STRING_LIT, result, self.line, start_col)

    def _id(self):
        result = ''
        start_col = self.column
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()

        token_type = KEYWORDS.get(result, TokenType.IDENTIFIER)
        value = result
        if token_type == TokenType.TRUE:
            value = True
        elif token_type == TokenType.FALSE:
            value = False

        return Token(token_type, value, self.line, start_col)

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char == '/' and self.peek() == '/':
                self.skip_comment()
                continue

            if self.current_char.isdigit():
                return self.number()

            if self.current_char == '"':
                return self.string()

            if self.current_char.isalpha() or self.current_char == '_':
                return self._id()

            if self.current_char == '&':
                if self.peek() == '&':
                    token = Token(TokenType.AND, '&&', self.line, self.column)
                    self.advance()
                    self.advance()
                    return token
                else:
                    self.error("Expected '&'")

            if self.current_char == '|':
                if self.peek() == '|':
                    token = Token(TokenType.OR, '||', self.line, self.column)
                    self.advance()
                    self.advance()
                    return token
                else:
                    self.error("Expected '|'")

            if self.current_char == '+':
                token = Token(TokenType.PLUS, '+', self.line, self.column)
                self.advance()
                return token

            if self.current_char == '-':
                token = Token(TokenType.MINUS, '-', self.line, self.column)
                self.advance()
                return token

            if self.current_char == '*':
                token = Token(TokenType.MUL, '*', self.line, self.column)
                self.advance()
                return token

            if self.current_char == '/':
                token = Token(TokenType.DIV, '/', self.line, self.column)
                self.advance()
                return token

            if self.current_char == '%':
                token = Token(TokenType.MOD, '%', self.line, self.column)
                self.advance()
                return token

            if self.current_char == '(':
                token = Token(TokenType.LPAREN, '(', self.line, self.column)
                self.advance()
                return token

            if self.current_char == ')':
                token = Token(TokenType.RPAREN, ')', self.line, self.column)
                self.advance()
                return token

            if self.current_char == '{':
                token = Token(TokenType.LBRACE, '{', self.line, self.column)
                self.advance()
                return token

            if self.current_char == '}':
                token = Token(TokenType.RBRACE, '}', self.line, self.column)
                self.advance()
                return token

            if self.current_char == '[':
                token = Token(TokenType.LBRACKET, '[', self.line, self.column)
                self.advance()
                return token

            if self.current_char == ']':
                token = Token(TokenType.RBRACKET, ']', self.line, self.column)
                self.advance()
                return token

            if self.current_char == ';':
                token = Token(TokenType.SEMI, ';', self.line, self.column)
                self.advance()
                return token

            if self.current_char == ',':
                token = Token(TokenType.COMMA, ',', self.line, self.column)
                self.advance()
                return token

            if self.current_char == '=':
                if self.peek() == '=':
                    token = Token(TokenType.EQ, '==', self.line, self.column)
                    self.advance()
                    self.advance()
                    return token
                else:
                    token = Token(TokenType.ASSIGN, '=', self.line, self.column)
                    self.advance()
                    return token

            if self.current_char == '!':
                if self.peek() == '=':
                    token = Token(TokenType.NEQ, '!=', self.line, self.column)
                    self.advance()
                    self.advance()
                    return token
                else:
                    token = Token(TokenType.NOT, '!', self.line, self.column)
                    self.advance()
                    return token

            if self.current_char == '<':
                if self.peek() == '=':
                    token = Token(TokenType.LTE, '<=', self.line, self.column)
                    self.advance()
                    self.advance()
                    return token
                else:
                    token = Token(TokenType.LT, '<', self.line, self.column)
                    self.advance()
                    return token

            if self.current_char == '>':
                if self.peek() == '=':
                    token = Token(TokenType.GTE, '>=', self.line, self.column)
                    self.advance()
                    self.advance()
                    return token
                else:
                    token = Token(TokenType.GT, '>', self.line, self.column)
                    self.advance()
                    return token

            self.error()

        return Token(TokenType.EOF, None, self.line, self.column)
