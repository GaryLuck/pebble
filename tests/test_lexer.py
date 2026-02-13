import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pebble.lexer import Lexer, TokenType, Token, LexerError

class TestLexer(unittest.TestCase):
    def test_keywords_and_identifiers(self):
        text = "if else while for return int string bool void true false myVar"
        lexer = Lexer(text)

        expected_types = [
            TokenType.IF, TokenType.ELSE, TokenType.WHILE, TokenType.FOR,
            TokenType.RETURN, TokenType.INT, TokenType.STRING, TokenType.BOOL,
            TokenType.VOID, TokenType.TRUE, TokenType.FALSE, TokenType.IDENTIFIER
        ]

        for t in expected_types:
            token = lexer.get_next_token()
            self.assertEqual(token.type, t)

        token = lexer.get_next_token()
        self.assertEqual(token.type, TokenType.EOF)

    def test_literals(self):
        text = '123 "hello"'
        lexer = Lexer(text)

        t1 = lexer.get_next_token()
        self.assertEqual(t1.type, TokenType.INTEGER_LIT)
        self.assertEqual(t1.value, 123)

        t2 = lexer.get_next_token()
        self.assertEqual(t2.type, TokenType.STRING_LIT)
        self.assertEqual(t2.value, "hello")

    def test_operators(self):
        text = "+ - * / % = == != < > <= >= && || !"
        lexer = Lexer(text)

        types = [
            TokenType.PLUS, TokenType.MINUS, TokenType.MUL, TokenType.DIV, TokenType.MOD,
            TokenType.ASSIGN, TokenType.EQ, TokenType.NEQ, TokenType.LT, TokenType.GT,
            TokenType.LTE, TokenType.GTE, TokenType.AND, TokenType.OR, TokenType.NOT
        ]

        for t in types:
            token = lexer.get_next_token()
            self.assertEqual(token.type, t)

    def test_delimiters(self):
        text = "( ) { } [ ] ; ,"
        lexer = Lexer(text)

        types = [
            TokenType.LPAREN, TokenType.RPAREN, TokenType.LBRACE, TokenType.RBRACE,
            TokenType.LBRACKET, TokenType.RBRACKET, TokenType.SEMI, TokenType.COMMA
        ]

        for t in types:
            token = lexer.get_next_token()
            self.assertEqual(token.type, t)

    def test_comments(self):
        text = """
        // This is a comment
        int x = 5; // another comment
        """
        lexer = Lexer(text)

        t1 = lexer.get_next_token()
        self.assertEqual(t1.type, TokenType.INT)

        t2 = lexer.get_next_token()
        self.assertEqual(t2.type, TokenType.IDENTIFIER)
        self.assertEqual(t2.value, 'x')

        t3 = lexer.get_next_token()
        self.assertEqual(t3.type, TokenType.ASSIGN)

        t4 = lexer.get_next_token()
        self.assertEqual(t4.type, TokenType.INTEGER_LIT)
        self.assertEqual(t4.value, 5)

        t5 = lexer.get_next_token()
        self.assertEqual(t5.type, TokenType.SEMI)

        t6 = lexer.get_next_token()
        self.assertEqual(t6.type, TokenType.EOF)

    def test_unknown_char(self):
        text = "@"
        lexer = Lexer(text)
        with self.assertRaises(LexerError):
            lexer.get_next_token()

    def test_unterminated_string(self):
        text = '"hello'
        lexer = Lexer(text)
        with self.assertRaises(LexerError):
            lexer.get_next_token()

if __name__ == '__main__':
    unittest.main()
