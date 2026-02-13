import unittest
from io import StringIO
import sys
from pebble.lexer import Lexer
from pebble.parser import Parser
from pebble.interpreter import Interpreter

class TestInterpreter(unittest.TestCase):
    def setUp(self):
        # Capture stdout
        self.held, sys.stdout = sys.stdout, StringIO()
        self.stdin_held, sys.stdin = sys.stdin, StringIO()

    def tearDown(self):
        sys.stdout = self.held
        sys.stdin = self.stdin_held

    def interpret(self, text):
        lexer = Lexer(text)
        parser = Parser(lexer)
        interpreter = Interpreter(parser)
        interpreter.interpret()
        return sys.stdout.getvalue()

    def test_hello_world(self):
        text = """
        void main() {
            print("Hello World");
        }
        """
        output = self.interpret(text)
        self.assertEqual(output.strip(), "Hello World")

    def test_variables(self):
        text = """
        void main() {
            int x = 10;
            int y = 20;
            print(x + y);
        }
        """
        output = self.interpret(text)
        self.assertEqual(output.strip(), "30")

    def test_recursion(self):
        text = """
        int fib(int n) {
            if (n <= 1) return n;
            return fib(n-1) + fib(n-2);
        }
        void main() {
            print(fib(10));
        }
        """
        output = self.interpret(text)
        self.assertEqual(output.strip(), "55")

    def test_array(self):
        text = """
        void main() {
            int[] arr = {1, 2, 3};
            arr[0] = 10;
            print(arr[0] + arr[1]);
        }
        """
        output = self.interpret(text)
        self.assertEqual(output.strip(), "12")

    def test_loops(self):
        text = """
        void main() {
            int i = 0;
            while (i < 5) {
                print(i);
                i = i + 1;
            }
        }
        """
        output = self.interpret(text)
        lines = output.strip().split('\n')
        lines = [line for line in lines if line]
        self.assertEqual(lines, ["0", "1", "2", "3", "4"])

    def test_for_loop(self):
        text = """
        void main() {
            for (int i = 0; i < 3; i = i + 1) {
                print(i);
            }
        }
        """
        output = self.interpret(text)
        lines = output.strip().split('\n')
        lines = [line for line in lines if line]
        self.assertEqual(lines, ["0", "1", "2"])

    def test_strings(self):
        text = """
        void main() {
            string s = "hello";
            print(length(s));
            print(left(s, 2));
            print(right(s, 2));
        }
        """
        output = self.interpret(text)
        lines = output.strip().split('\n')
        lines = [line for line in lines if line]
        self.assertEqual(lines[0], "5")
        self.assertEqual(lines[1], "he")
        self.assertEqual(lines[2], "lo")

    def test_array_out_of_bounds(self):
        text = """
        void main() {
            int[] arr = {1, 2, 3};
            print(arr[3]);
        }
        """
        with self.assertRaises(Exception):
            self.interpret(text)

    def test_string_concat(self):
        text = """
        void main() {
            string a = "hello";
            string b = " world";
            print(a + b);
        }
        """
        output = self.interpret(text)
        self.assertEqual(output.strip(), "hello world")

    def test_string_funcs_advanced(self):
        text = """
        void main() {
            string s = "hello world";
            print(mid(s, 6, 5));
            print(instr(s, "world"));
            print(instr(s, "foo"));
        }
        """
        output = self.interpret(text)
        lines = output.strip().split('\n')
        lines = [line for line in lines if line]
        self.assertEqual(lines[0], "world")
        self.assertEqual(lines[1], "6")
        self.assertEqual(lines[2], "-1")

    def test_input(self):
        sys.stdin.write("42\nhello\n")
        sys.stdin.seek(0)

        text = """
        void main() {
            int n = read_int();
            string s = read_line();
            print(n);
            print(s);
        }
        """
        output = self.interpret(text)
        lines = output.strip().split('\n')
        lines = [line for line in lines if line]
        self.assertEqual(lines[0], "42")
        self.assertEqual(lines[1], "hello")

if __name__ == '__main__':
    unittest.main()
