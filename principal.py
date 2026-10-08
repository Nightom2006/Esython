# principal.py
import sys
from lexer import Lexer
from parser_es import Parser
from interpreter import Interprete

def ejecutar_codigo(codigo, interprete):
    try:
        # 1. Lexer: Convierte el texto en tokens
        lexer = Lexer(codigo)
        tokens = lexer.generar_tokens()
        
        # Si la línea está vacía, no hace nada
        if len(tokens) == 1 and tokens[0].tipo == 'FIN':
            return
        
        # 2. Parser: Convierte los tokens en el árbol AST
        parser = Parser(tokens)
        ast = parser.parsear()
        
        # 3. Intérprete: Ejecuta el AST
        interprete.ejecutar(ast)
    except Exception as e:
        print(f"Error: {e}")

def modo_repl():
    print("=== Consola Interactiva de Esython ===")
    print("Escribe 'salir' para cerrar la consola.\n")
    interprete = Interprete()
    
    while True:
        try:
            linea = input("esython>>> ")
            if linea.strip() == "salir":
                break
            if not linea.strip():
                continue
            
            # Si la línea termina en ':', acumular las líneas del bloque
            codigo_acumulado = linea + "\n"
            if linea.strip().endswith(":"):
                while True:
                    sub_linea = input("...       ")
                    if not sub_linea.strip():  # Enter en blanco para finalizar el bloque
                        break
                    codigo_acumulado += sub_linea + "\n"
            
            ejecutar_codigo(codigo_acumulado, interprete)
        except (KeyboardInterrupt, EOFError):
            print("\nSaliendo de Esython...")
            break

def modo_archivo(ruta_archivo):
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            codigo = f.read()
        interprete = Interprete()
        ejecutar_codigo(codigo, interprete)
    except FileNotFoundError:
        print(f"Error: El archivo '{ruta_archivo}' no existe.")

if __name__ == "__main__":
    # Si le pasas un archivo como argumento: python principal.py prueba.esy
    if len(sys.argv) > 1:
        modo_archivo(sys.argv[1])
    # Si ejecutas solo: python principal.py
    else:
        modo_repl()