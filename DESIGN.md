# Pebble Language Design Document

## Introduction
Pebble is a small, procedural programming language with C-like syntax. It supports basic data types, arrays, control flow structures, and functions (including recursion).

## File Extension
Source files should have the extension `.pebble`.

## Comments
Single-line comments start with `//` and extend to the end of the line.

## Data Types
*   `int`: Signed integer.
*   `string`: String of characters.
*   `bool`: Boolean values (`true`, `false`).
*   Arrays: Fixed-size arrays of `int`, `string`, or `bool`.
    *   Declaration: `int[5] numbers;` (initialized to defaults)
    *   Initialization: `int[] numbers = {1, 2, 3, 4, 5};`

## Keywords
`if`, `else`, `while`, `for`, `return`, `func` (implied by type declaration?), `int`, `string`, `bool`, `void`, `true`, `false`.

**Note**: Functions are declared with a return type, e.g., `int add(int a, int b) { ... }`. `void` is used if no value is returned.

## Operators
*   Arithmetic: `+`, `-`, `*`, `/`, `%`
*   Comparison: `==`, `!=`, `<`, `>`, `<=`, `>=`
*   Logical: `&&`, `||`, `!` (implied by standard C-like behavior, though not explicitly requested, they are essential for control flow)
*   Assignment: `=`

## Built-in Functions
*   **I/O**:
    *   `print(expr)`: Prints the expression to stdout (followed by newline).
    *   `read_int()`: Reads an integer from stdin.
    *   `read_line()`: Reads a line of text from stdin.
*   **String Manipulation**:
    *   `length(s)`: Returns the length of string `s`.
    *   `left(s, n)`: Returns the first `n` characters of `s`.
    *   `right(s, n)`: Returns the last `n` characters of `s`.
    *   `mid(s, start, len)`: Returns a substring of `s` starting at `start` (0-indexed) with length `len`.
    *   `instr(s, sub)`: Returns the index of the first occurrence of `sub` in `s`, or -1 if not found.

## Grammar (EBNF-like)

```ebnf
program         ::= { declaration }

declaration     ::= variable_decl | function_decl

variable_decl   ::= type IDENTIFIER [ "=" expression ] ";"
                  | type "[" INTEGER_LITERAL "]" IDENTIFIER ";"
                  | type "[]" IDENTIFIER "=" "{" [ expression { "," expression } ] "}" ";"

function_decl   ::= type IDENTIFIER "(" [ parameter_list ] ")" block

parameter_list  ::= parameter { "," parameter }
parameter       ::= type IDENTIFIER [ "[]" ]  // Arrays passed by reference

block           ::= "{" { statement } "}"

statement       ::= variable_decl
                  | assignment
                  | if_stmt
                  | while_stmt
                  | for_stmt
                  | return_stmt
                  | expression_stmt
                  | block

assignment      ::= IDENTIFIER [ "[" expression "]" ] "=" expression ";"

if_stmt         ::= "if" "(" expression ")" statement [ "else" statement ]

while_stmt      ::= "while" "(" expression ")" statement

for_stmt        ::= "for" "(" ( variable_decl | assignment | ";" ) expression ";" ( assignment | expression ) ")" statement

return_stmt     ::= "return" [ expression ] ";"

expression_stmt ::= expression ";"

expression      ::= ... (standard precedence logic)

type            ::= "int" | "string" | "bool" | "void"
```

## Examples

### Hello World
```pebble
void main() {
    print("Hello, World!");
}
```

### Fibonacci (Recursion)
```pebble
int fib(int n) {
    if (n <= 1) {
        return n;
    }
    return fib(n - 1) + fib(n - 2);
}

void main() {
    int n = 10;
    print("Fibonacci of " + n + " is " + fib(n));
}
```

### Array Usage
```pebble
void main() {
    int[] nums = {10, 20, 30};
    int i = 0;
    while (i < 3) {
        print(nums[i]);
        i = i + 1;
    }
}
```
