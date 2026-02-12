from pebble.lexer import TokenType
from pebble.ast import (
    Program, VarDecl, ArrayDecl, FunctionDecl, Param, Block, Assign, If, While, For, Return,
    ExprStmt, BinOp, UnaryOp, Literal, Var, ArrayAccess, Call, Type
)

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self, msg=None):
        if msg is None:
            msg = f"Invalid syntax at {self.current_token}"
        raise Exception(msg)

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(f"Expected {token_type}, got {self.current_token}")

    def program(self):
        declarations = []
        while self.current_token.type != TokenType.EOF:
            declarations.append(self.declaration())
        return Program(declarations)

    def type_spec(self):
        token = self.current_token
        if token.type in (TokenType.INT, TokenType.STRING, TokenType.BOOL, TokenType.VOID):
            self.eat(token.type)
            return Type(token)
        else:
            self.error("Expected type")

    def declaration(self):
        # Peek ahead logic is simulated by parsing step by step
        type_node = self.type_spec()

        if self.current_token.type == TokenType.LBRACKET:
            return self.array_decl(type_node)
        else:
            name = self.current_token.value
            self.eat(TokenType.IDENTIFIER)

            if self.current_token.type == TokenType.LPAREN:
                return self.function_decl(type_node, name)
            else:
                return self.variable_decl(type_node, name)

    def array_decl(self, type_node):
        self.eat(TokenType.LBRACKET)
        if self.current_token.type == TokenType.RBRACKET:
            # type [] name = { ... }
            self.eat(TokenType.RBRACKET)
            name = self.current_token.value
            self.eat(TokenType.IDENTIFIER)
            self.eat(TokenType.ASSIGN)
            self.eat(TokenType.LBRACE)
            values = []
            if self.current_token.type != TokenType.RBRACE:
                values.append(self.expr())
                while self.current_token.type == TokenType.COMMA:
                    self.eat(TokenType.COMMA)
                    values.append(self.expr())
            self.eat(TokenType.RBRACE)
            self.eat(TokenType.SEMI)
            return ArrayDecl(type_node, name, None, values)
        else:
            # type [size] name;
            size = self.current_token.value
            self.eat(TokenType.INTEGER_LIT)
            self.eat(TokenType.RBRACKET)
            name = self.current_token.value
            self.eat(TokenType.IDENTIFIER)
            self.eat(TokenType.SEMI)
            return ArrayDecl(type_node, name, size, None)

    def function_decl(self, type_node, name):
        self.eat(TokenType.LPAREN)
        params = []
        if self.current_token.type != TokenType.RPAREN:
            params.append(self.param())
            while self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                params.append(self.param())
        self.eat(TokenType.RPAREN)
        block = self.block()
        return FunctionDecl(type_node, name, params, block)

    def param(self):
        type_node = self.type_spec()
        name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        is_array = False
        if self.current_token.type == TokenType.LBRACKET:
            self.eat(TokenType.LBRACKET)
            self.eat(TokenType.RBRACKET)
            is_array = True
        return Param(type_node, name, is_array)

    def variable_decl(self, type_node, name):
        value = None
        if self.current_token.type == TokenType.ASSIGN:
            self.eat(TokenType.ASSIGN)
            value = self.expr()
        self.eat(TokenType.SEMI)
        return VarDecl(type_node, name, value)

    def block(self):
        self.eat(TokenType.LBRACE)
        statements = []
        while self.current_token.type != TokenType.RBRACE and self.current_token.type != TokenType.EOF:
            statements.append(self.statement())
        self.eat(TokenType.RBRACE)
        return Block(statements)

    def statement(self):
        if self.current_token.type in (TokenType.INT, TokenType.STRING, TokenType.BOOL, TokenType.VOID):
            # Variable declaration inside block
            type_node = self.type_spec()
            if self.current_token.type == TokenType.LBRACKET:
                return self.array_decl(type_node)
            else:
                name = self.current_token.value
                self.eat(TokenType.IDENTIFIER)
                return self.variable_decl(type_node, name)
        elif self.current_token.type == TokenType.LBRACE:
            return self.block()
        elif self.current_token.type == TokenType.IF:
            return self.if_stmt()
        elif self.current_token.type == TokenType.WHILE:
            return self.while_stmt()
        elif self.current_token.type == TokenType.FOR:
            return self.for_stmt()
        elif self.current_token.type == TokenType.RETURN:
            return self.return_stmt()
        elif self.current_token.type == TokenType.IDENTIFIER:
            # Assignment or Call
            # We need to peek. But Identifier is start of expression too.
            # Assign: id = ...
            # Assign Array: id[expr] = ...
            # Call: id(...)

            # Since my lexer doesn't support peeking multiple tokens easily without saving state,
            # I can parse the 'id' part, check next token.
            # But `expr` also starts with `IDENTIFIER`.

            # If I treat `assignment` as separate from `expr_stmt`, I need to distinguish.

            # Assignment grammar: IDENTIFIER [ "[" expression "]" ] "=" expression ";"
            # Expression statement: expression ";"

            # Let's try to parse as assignment if it looks like one.
            # Note: `call` is an expression.

            # Implementing a simple lookahead here would be useful.
            # Or I can just start parsing an expression. If it's just an identifier (Var node) or ArrayAccess node, check if next is `=`.

            # However, `expr` parsing is complex.

            # Simpler approach:
            # Save current token state? No, Lexer is stateful.

            # Let's peek the next token using a temporary lookahead if possible.
            # My lexer has `peek()`, but that only returns one char.

            # Let's rely on the fact that `assignment` must start with ID.

            # I'll implement a `peek_token` in Lexer or Parser?
            # Lexer's `peek` is for characters.

            # I will modify Lexer or add a buffer to Parser.
            # But let's try to do it without modifying Lexer if possible.

            # Actually, `assignment` is NOT an expression in my grammar (it's a statement).
            # But `call` IS an expression.

            # If I see IDENTIFIER:
            # It could be `x = 5;`
            # It could be `x[0] = 5;`
            # It could be `func();`

            # If next is `=`, it is assignment.
            # If next is `[`, it COULD be assignment (`x[0]=1`) or expression `x[0]`.
            # If next is `(`, it is call (expression).

            # So:
            # Parse ID.
            # If next `(`, it's a call. -> parse rest of call. Then expect `;`.
            # If next `=`, it's assignment.
            # If next `[`, parse index. Then check if next is `=`.

            # BUT `x + 1;` is also a valid statement (expr stmt).
            # `x;` is valid.

            # So, really, I should parse an expression.
            # If the resulting expression is a `Var` or `ArrayAccess`, AND the next token is `=`, then it's an assignment.
            # Otherwise it's an expression statement.

            expr_node = self.expr()
            if self.current_token.type == TokenType.ASSIGN:
                self.eat(TokenType.ASSIGN)
                value = self.expr()
                self.eat(TokenType.SEMI)

                if isinstance(expr_node, Var):
                    return Assign(expr_node.token.value, value)
                elif isinstance(expr_node, ArrayAccess):
                    return Assign(expr_node.name, value, expr_node.index)
                else:
                    self.error("Invalid assignment target")
            else:
                self.eat(TokenType.SEMI)
                return ExprStmt(expr_node)

        else:
            return self.expr_stmt()

    def if_stmt(self):
        self.eat(TokenType.IF)
        self.eat(TokenType.LPAREN)
        condition = self.expr()
        self.eat(TokenType.RPAREN)
        then_stmt = self.statement()
        else_stmt = None
        if self.current_token.type == TokenType.ELSE:
            self.eat(TokenType.ELSE)
            else_stmt = self.statement()
        return If(condition, then_stmt, else_stmt)

    def while_stmt(self):
        self.eat(TokenType.WHILE)
        self.eat(TokenType.LPAREN)
        condition = self.expr()
        self.eat(TokenType.RPAREN)
        body = self.statement()
        return While(condition, body)

    def for_stmt(self):
        self.eat(TokenType.FOR)
        self.eat(TokenType.LPAREN)

        # Init: variable_decl | assignment | ;
        init = None
        if self.current_token.type == TokenType.SEMI:
            self.eat(TokenType.SEMI)
        elif self.current_token.type in (TokenType.INT, TokenType.STRING, TokenType.BOOL):
             # variable decl
             type_node = self.type_spec()
             name = self.current_token.value
             self.eat(TokenType.IDENTIFIER)
             init = self.variable_decl(type_node, name) # consumes semi
        else:
             # assignment or expr?
             # My grammar said: variable_decl | assignment | ";"
             # Let's reuse the logic from `statement` but restrict it?
             # Or just parse an expression/assignment.

             # Re-using statement logic is hard because statement eats semicolon.
             # Variable decl eats semicolon.
             # Assignment logic I wrote above eats semicolon.

             # So I can reuse `statement` logic if I'm careful.
             # But `statement` parses `if`, `while`... we don't want those.

             # Let's implement specific logic.

             # Parse expr. Check for `=`.
             expr_node = self.expr()
             if self.current_token.type == TokenType.ASSIGN:
                 self.eat(TokenType.ASSIGN)
                 value = self.expr()
                 self.eat(TokenType.SEMI)
                 if isinstance(expr_node, Var):
                     init = Assign(expr_node.token.value, value)
                 elif isinstance(expr_node, ArrayAccess):
                     init = Assign(expr_node.name, value, expr_node.index)
                 else:
                     self.error("Invalid assignment in for loop init")
             else:
                 # It's just an expression statement
                 self.eat(TokenType.SEMI)
                 init = ExprStmt(expr_node)

        # Condition
        condition = None
        if self.current_token.type != TokenType.SEMI:
            condition = self.expr()
        self.eat(TokenType.SEMI)

        # Update
        update = None
        if self.current_token.type != TokenType.RPAREN:
             expr_node = self.expr()
             if self.current_token.type == TokenType.ASSIGN:
                 self.eat(TokenType.ASSIGN)
                 value = self.expr()
                 if isinstance(expr_node, Var):
                     update = Assign(expr_node.token.value, value)
                 elif isinstance(expr_node, ArrayAccess):
                     update = Assign(expr_node.name, value, expr_node.index)
                 else:
                     self.error("Invalid assignment in for loop update")
             else:
                 update = ExprStmt(expr_node)

        self.eat(TokenType.RPAREN)
        body = self.statement()
        return For(init, condition, update, body)

    def return_stmt(self):
        self.eat(TokenType.RETURN)
        value = None
        if self.current_token.type != TokenType.SEMI:
            value = self.expr()
        self.eat(TokenType.SEMI)
        return Return(value)

    def expr_stmt(self):
        node = self.expr()
        self.eat(TokenType.SEMI)
        return ExprStmt(node)

    def expr(self):
        return self.logic_or()

    def logic_or(self):
        node = self.logic_and()
        while self.current_token.type == TokenType.OR:
            token = self.current_token
            self.eat(TokenType.OR)
            node = BinOp(left=node, op=token, right=self.logic_and())
        return node

    def logic_and(self):
        node = self.equality()
        while self.current_token.type == TokenType.AND:
            token = self.current_token
            self.eat(TokenType.AND)
            node = BinOp(left=node, op=token, right=self.equality())
        return node

    def equality(self):
        node = self.relational()
        while self.current_token.type in (TokenType.EQ, TokenType.NEQ):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(left=node, op=token, right=self.relational())
        return node

    def relational(self):
        node = self.additive()
        while self.current_token.type in (TokenType.LT, TokenType.LTE, TokenType.GT, TokenType.GTE):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(left=node, op=token, right=self.additive())
        return node

    def additive(self):
        node = self.term()
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(left=node, op=token, right=self.term())
        return node

    def term(self):
        node = self.factor()
        while self.current_token.type in (TokenType.MUL, TokenType.DIV, TokenType.MOD):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(left=node, op=token, right=self.factor())
        return node

    def factor(self):
        token = self.current_token
        if token.type == TokenType.PLUS:
            self.eat(TokenType.PLUS)
            return UnaryOp(token, self.factor())
        elif token.type == TokenType.MINUS:
            self.eat(TokenType.MINUS)
            return UnaryOp(token, self.factor())
        elif token.type == TokenType.NOT:
            self.eat(TokenType.NOT)
            return UnaryOp(token, self.factor())
        elif token.type == TokenType.INTEGER_LIT:
            self.eat(TokenType.INTEGER_LIT)
            return Literal(token.value, 'int')
        elif token.type == TokenType.STRING_LIT:
            self.eat(TokenType.STRING_LIT)
            return Literal(token.value, 'string')
        elif token.type == TokenType.TRUE:
            self.eat(TokenType.TRUE)
            return Literal(True, 'bool')
        elif token.type == TokenType.FALSE:
            self.eat(TokenType.FALSE)
            return Literal(False, 'bool')
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expr()
            self.eat(TokenType.RPAREN)
            return node
        elif token.type == TokenType.IDENTIFIER:
            return self.variable()
        else:
            self.error("Unexpected token in factor")

    def variable(self):
        node = Var(self.current_token)
        self.eat(TokenType.IDENTIFIER)
        if self.current_token.type == TokenType.LBRACKET:
            self.eat(TokenType.LBRACKET)
            index = self.expr()
            self.eat(TokenType.RBRACKET)
            return ArrayAccess(node.value, index)
        elif self.current_token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            args = []
            if self.current_token.type != TokenType.RPAREN:
                args.append(self.expr())
                while self.current_token.type == TokenType.COMMA:
                    self.eat(TokenType.COMMA)
                    args.append(self.expr())
            self.eat(TokenType.RPAREN)
            return Call(node.value, args)
        else:
            return node
