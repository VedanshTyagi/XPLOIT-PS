import sys

def compile_wut(filepath):
    try:
        with open(filepath, 'r') as f:
            code = f.read().strip()
    except FileNotFoundError:
        print(f"Error: cannot open file '{filepath}'")
        return

    stack = []
    i = 0
    
    while i < len(code):
        char = code[i]
        
        if char == '~':
            stack.append(65)
        elif char == '(':
            i += 1
            num_str = ""
            while i < len(code) and code[i].isdigit():
                num_str += code[i]
                i += 1
            stack.append(int(num_str))
            continue # Skip the i+=1 to process the trailing symbol next
        elif char == '%':
            if len(stack) < 2: raise Exception("Error: stack underflow")
            stack.append(stack.pop() + stack.pop())
        elif char == '#':
            if len(stack) < 1: raise Exception("Error: stack underflow")
            stack.append(-stack.pop())
        elif char == '@':
            if len(stack) < 1: raise Exception("Error: stack underflow")
            stack.append(stack.pop() - 1)
        elif char == '!':
            if len(stack) < 1: raise Exception("Error: stack underflow")
            stack.append(stack.pop() + 1)
        elif char == '^':
            if len(stack) < 1: raise Exception("Error: stack empty")
            print(chr(stack[-1]), end="")
        elif char == '$':
            if len(stack) < 2: raise Exception("Error: stack underflow")
            a, b = stack.pop(), stack.pop()
            stack.append(a)
            stack.append(b)
        elif char == '&':
            if len(stack) < 1: raise Exception("Error: stack empty")
            if stack[-1] == 0:
                depth = 1
                while depth > 0:
                    i += 1
                    if i >= len(code): raise Exception("Error: unmatched &")
                    if code[i] == '&': depth += 1
                    elif code[i] == '*': depth -= 1
        elif char == '*':
            if len(stack) < 1: raise Exception("Error: stack empty")
            if stack[-1] != 0:
                depth = 1
                while depth > 0:
                    i -= 1
                    if i < 0: raise Exception("Error: unmatched *")
                    if code[i] == '*': depth += 1
                    elif code[i] == '&': depth -= 1
        elif char == '`':
            print('!', end="")
            break
            
        i += 1
    print() # Output a clean newline at EOF

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python wut_compiler.py <source file>")
    else:
        compile_wut(sys.argv[1])