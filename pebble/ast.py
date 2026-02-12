class AST:
    pass

class Program(AST):
    def __init__(self, declarations):
        self.declarations = declarations

class VarDecl(AST):
    def __init__(self, type_node, name, value=None):
        self.type_node = type_node
        self.name = name
        self.value = value

class ArrayDecl(AST):
    def __init__(self, type_node, name, size, values=None):
        self.type_node = type_node
        self.name = name
        self.size = size # Integer literal or None if initialized with values
        self.values = values # List of expressions

class FunctionDecl(AST):
    def __init__(self, type_node, name, params, block):
        self.type_node = type_node
        self.name = name
        self.params = params
        self.block = block

class Param(AST):
    def __init__(self, type_node, name, is_array=False):
        self.type_node = type_node
        self.name = name
        self.is_array = is_array

class Block(AST):
    def __init__(self, statements):
        self.statements = statements

class Assign(AST):
    def __init__(self, name, value, index=None):
        self.name = name
        self.value = value
        self.index = index # For array assignment

class If(AST):
    def __init__(self, condition, then_stmt, else_stmt=None):
        self.condition = condition
        self.then_stmt = then_stmt
        self.else_stmt = else_stmt

class While(AST):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class For(AST):
    def __init__(self, init, condition, update, body):
        self.init = init
        self.condition = condition
        self.update = update
        self.body = body

class Return(AST):
    def __init__(self, value):
        self.value = value

class ExprStmt(AST):
    def __init__(self, expr):
        self.expr = expr

class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class UnaryOp(AST):
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

class Literal(AST):
    def __init__(self, value, type_name):
        self.value = value
        self.type_name = type_name # 'int', 'string', 'bool'

class Var(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class ArrayAccess(AST):
    def __init__(self, name, index):
        self.name = name
        self.index = index

class Call(AST):
    def __init__(self, name, args):
        self.name = name
        self.args = args

class Type(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value
