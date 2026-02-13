import sys
import os

# Add current directory to path so we can import pebble package
sys.path.append(os.getcwd())

from pebble.lexer import Lexer, LexerError
from pebble.parser import Parser
from pebble.interpreter import Interpreter, ReturnException

def main():
    if len(sys.argv) != 2:
        print("Usage: python pebble.py <file.pebble>")
        sys.exit(1)

    filepath = sys.argv[1]
    try:
        with open(filepath, 'r') as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
        sys.exit(1)

    try:
        lexer = Lexer(text)
        parser = Parser(lexer)
        interpreter = Interpreter(parser)
        interpreter.interpret()
    except LexerError as e:
        print(f"Lexer Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Runtime Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
