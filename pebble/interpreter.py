from pebble.lexer import TokenType
from pebble.ast import *
import sys

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class Environment:
    def __init__(self, enclosing=None):
        self.enclosing = enclosing
        self.values = {}

    def define(self, name, value):
        self.values[name] = value

    def get(self, name):
        if name in self.values:
            return self.values[name]
        if self.enclosing:
            return self.enclosing.get(name)
        raise Exception(f"Undefined variable '{name}'")

    def assign(self, name, value):
        if name in self.values:
            self.values[name] = value
            return
        if self.enclosing:
            self.enclosing.assign(name, value)
            return
        raise Exception(f"Undefined variable '{name}'")

class Interpreter:
    def __init__(self, parser):
        self.parser = parser
        self.globals = Environment()
        self.environment = self.globals
        self.functions = {}

    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f'No visit_{type(node).__name__} method')

    def interpret(self):
        tree = self.parser.program()
        return self.visit(tree)

    def visit_Program(self, node):
        # First pass: register all functions and global variables
        for decl in node.declarations:
            if isinstance(decl, FunctionDecl):
                self.functions[decl.name] = decl
            elif isinstance(decl, VarDecl) or isinstance(decl, ArrayDecl):
                self.visit(decl)

        # Look for main function
        main = self.functions.get('main')
        if not main:
            raise Exception("No main function found")

        try:
            self.call_function(main, [])
        except ReturnException as e:
            pass # main returned

    def call_function(self, func_decl, args):
        # check args length
        if len(args) != len(func_decl.params):
            raise Exception(f"Function {func_decl.name} expects {len(func_decl.params)} arguments, got {len(args)}")

        previous_env = self.environment
        new_env = Environment(self.globals) # Functions are closures over globals only in this simple language, or should they be lexical?
        # Standard procedural languages usually have lexical scope, but if functions are only top-level, then enclosing is globals.
        # User said: "variables have block scope, and also globals defined at the beginning of the program."
        # This implies functions can access globals.

        self.environment = new_env

        for param, arg in zip(func_decl.params, args):
            self.environment.define(param.name, arg)

        try:
            self.visit(func_decl.block)
        except ReturnException as r:
            self.environment = previous_env
            return r.value

        self.environment = previous_env
        return None

    def visit_Block(self, node):
        # Create new scope
        previous_env = self.environment
        self.environment = Environment(previous_env)

        try:
            for stmt in node.statements:
                self.visit(stmt)
        finally:
            self.environment = previous_env

    def visit_VarDecl(self, node):
        value = None
        if node.value:
            value = self.visit(node.value)
        else:
             # Default values
             if node.type_node.value == 'int': value = 0
             elif node.type_node.value == 'string': value = ""
             elif node.type_node.value == 'bool': value = False
        self.environment.define(node.name, value)

    def visit_ArrayDecl(self, node):
        if node.values:
            values = [self.visit(v) for v in node.values]
            self.environment.define(node.name, values)
        else:
            size = node.size
            if size is None: # Should be caught by parser
                size = 0
            default_val = 0
            if node.type_node.value == 'string': default_val = ""
            elif node.type_node.value == 'bool': default_val = False
            self.environment.define(node.name, [default_val] * size)

    def visit_FunctionDecl(self, node):
        # Already handled in visit_Program
        pass

    def visit_Assign(self, node):
        value = self.visit(node.value)
        if node.index:
            # Array assignment
            index = self.visit(node.index)
            arr = self.environment.get(node.name)
            if not isinstance(arr, list):
                raise Exception(f"Variable {node.name} is not an array")
            if index < 0 or index >= len(arr):
                raise Exception(f"Array index out of bounds: {index}")
            arr[index] = value
        else:
            self.environment.assign(node.name, value)

    def visit_If(self, node):
        if self.visit(node.condition):
            self.visit(node.then_stmt)
        elif node.else_stmt:
            self.visit(node.else_stmt)

    def visit_While(self, node):
        while self.visit(node.condition):
            self.visit(node.body)

    def visit_For(self, node):
        # Create a scope for the loop variable if declared in init
        previous_env = self.environment
        self.environment = Environment(previous_env) # Loop scope? Usually for loop variable scope depends on language.
        # C99 allows `for (int i=...)` which is block scoped to the loop.

        try:
            if node.init:
                self.visit(node.init)

            while True:
                if node.condition:
                    if not self.visit(node.condition):
                        break
                else:
                    # Infinite loop if no condition? Standard C behavior.
                    pass

                self.visit(node.body)

                if node.update:
                    self.visit(node.update)
        finally:
            self.environment = previous_env

    def visit_Return(self, node):
        value = None
        if node.value:
            value = self.visit(node.value)
        raise ReturnException(value)

    def visit_ExprStmt(self, node):
        self.visit(node.expr)

    def visit_BinOp(self, node):
        left = self.visit(node.left)

        # Short-circuit logical operators
        if node.op.type == TokenType.AND:
            if not left: return False
            return self.visit(node.right)
        if node.op.type == TokenType.OR:
            if left: return True
            return self.visit(node.right)

        right = self.visit(node.right)

        if node.op.type == TokenType.PLUS:
            # String concatenation
            if isinstance(left, str) or isinstance(right, str):
                return str(left) + str(right)
            return left + right
        elif node.op.type == TokenType.MINUS:
            return left - right
        elif node.op.type == TokenType.MUL:
            return left * right
        elif node.op.type == TokenType.DIV:
            return int(left / right) # Integer division
        elif node.op.type == TokenType.MOD:
            return left % right
        elif node.op.type == TokenType.EQ:
            return left == right
        elif node.op.type == TokenType.NEQ:
            return left != right
        elif node.op.type == TokenType.LT:
            return left < right
        elif node.op.type == TokenType.GT:
            return left > right
        elif node.op.type == TokenType.LTE:
            return left <= right
        elif node.op.type == TokenType.GTE:
            return left >= right
        else:
            raise Exception(f"Unknown operator {node.op.type}")

    def visit_UnaryOp(self, node):
        val = self.visit(node.expr)
        if node.op.type == TokenType.MINUS:
            return -val
        elif node.op.type == TokenType.NOT:
            return not val
        elif node.op.type == TokenType.PLUS:
            return +val

    def visit_Literal(self, node):
        return node.value

    def visit_Var(self, node):
        return self.environment.get(node.value)

    def visit_ArrayAccess(self, node):
        index = self.visit(node.index)
        arr = self.environment.get(node.name)
        if not isinstance(arr, list):
            raise Exception(f"Variable {node.name} is not an array")
        if index < 0 or index >= len(arr):
             raise Exception(f"Array index out of bounds: {index}")
        return arr[index]

    def visit_Call(self, node):
        # Handle built-ins first
        if node.name == 'print':
            val = self.visit(node.args[0])
            print(val) # prints to stdout with newline
            return None
        elif node.name == 'read_int':
            try:
                # Use sys.stdin.readline() to allow mocking in tests
                line = sys.stdin.readline()
                if not line:
                    raise Exception("End of input")
                return int(line.strip())
            except ValueError:
                return 0
        elif node.name == 'read_line':
            line = sys.stdin.readline()
            if not line:
                 raise Exception("End of input")
            return line.strip()
        elif node.name == 'length':
            s = self.visit(node.args[0])
            return len(s)
        elif node.name == 'left':
            s = self.visit(node.args[0])
            n = self.visit(node.args[1])
            return s[:n]
        elif node.name == 'right':
            s = self.visit(node.args[0])
            n = self.visit(node.args[1])
            return s[-n:]
        elif node.name == 'mid':
            s = self.visit(node.args[0])
            start = self.visit(node.args[1])
            length = self.visit(node.args[2])
            return s[start:start+length]
        elif node.name == 'instr':
            s = self.visit(node.args[0])
            sub = self.visit(node.args[1])
            return s.find(sub)

        # User defined functions
        func = self.functions.get(node.name)
        if not func:
            raise Exception(f"Undefined function '{node.name}'")

        args = [self.visit(arg) for arg in node.args]
        return self.call_function(func, args)
