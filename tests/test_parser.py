import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pebble.lexer import Lexer, TokenType
from pebble.parser import Parser
from pebble.ast import *

class TestParser(unittest.TestCase):
    def test_var_decl(self):
        text = "int x = 5;"
        lexer = Lexer(text)
        parser = Parser(lexer)
        program = parser.program()

        self.assertEqual(len(program.declarations), 1)
        decl = program.declarations[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, 'x')
        self.assertIsInstance(decl.value, Literal)
        self.assertEqual(decl.value.value, 5)

    def test_array_decl(self):
        text = "int[] arr = {1, 2, 3};"
        lexer = Lexer(text)
        parser = Parser(lexer)
        program = parser.program()

        decl = program.declarations[0]
        self.assertIsInstance(decl, ArrayDecl)
        self.assertEqual(decl.name, 'arr')
        self.assertEqual(len(decl.values), 3)

    def test_func_decl(self):
        text = "void main() { return; }"
        lexer = Lexer(text)
        parser = Parser(lexer)
        program = parser.program()

        decl = program.declarations[0]
        self.assertIsInstance(decl, FunctionDecl)
        self.assertEqual(decl.name, 'main')
        self.assertEqual(len(decl.params), 0)
        self.assertEqual(len(decl.block.statements), 1)
        self.assertIsInstance(decl.block.statements[0], Return)

    def test_arithmetic_precedence(self):
        text = """
        void main() {
            int x = 1 + 2 * 3;
        }
        """
        lexer = Lexer(text)
        parser = Parser(lexer)
        program = parser.program()

        func = program.declarations[0]
        stmt = func.block.statements[0]
        expr = stmt.value

        # 1 + (2 * 3)
        self.assertIsInstance(expr, BinOp)
        self.assertEqual(expr.op.type, TokenType.PLUS)
        self.assertIsInstance(expr.left, Literal)
        self.assertEqual(expr.left.value, 1)

        self.assertIsInstance(expr.right, BinOp)
        self.assertEqual(expr.right.op.type, TokenType.MUL)
        self.assertEqual(expr.right.left.value, 2)
        self.assertEqual(expr.right.right.value, 3)

    def test_if_stmt(self):
        text = """
        void test() {
            if (x > 0) {
                x = x - 1;
            } else {
                x = 0;
            }
        }
        """
        lexer = Lexer(text)
        parser = Parser(lexer)
        program = parser.program()

        func = program.declarations[0]
        stmt = func.block.statements[0]
        self.assertIsInstance(stmt, If)
        self.assertIsInstance(stmt.condition, BinOp)
        self.assertIsInstance(stmt.then_stmt, Block)
        self.assertIsInstance(stmt.else_stmt, Block)

    def test_call_expr(self):
        text = """
        void main() {
            print("hello");
        }
        """
        lexer = Lexer(text)
        parser = Parser(lexer)
        program = parser.program()

        func = program.declarations[0]
        stmt = func.block.statements[0]
        self.assertIsInstance(stmt, ExprStmt)
        self.assertIsInstance(stmt.expr, Call)
        self.assertEqual(stmt.expr.name, 'print')
        self.assertEqual(len(stmt.expr.args), 1)

if __name__ == '__main__':
    unittest.main()
