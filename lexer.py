# lexer.py
import re

class Token:
    def __init__(self, tipo, valor=None):
        self.tipo = tipo
        self.valor = valor

    def __repr__(self):
        return f"Token({self.tipo}, {repr(self.valor)})"

class Lexer:
    PALABRAS_CLAVE = {
        'imprimir': 'IMPRIMIR', 'leer': 'LEER', 'entero': 'ENTERO',
        'decimal': 'DECIMAL', 'texto': 'TEXTO_FUNC', 'booleano': 'BOOLEANO',
        'variable': 'VARIABLE', 'si': 'SI', 'sino': 'SINO',
        'mientras': 'MIENTRAS', 'Verdadero': 'VERDADERO', 'Falso': 'FALSO',
        'y': 'Y', 'o': 'O', 'no': 'NO'
    }

    def __init__(self, codigo):
        self.codigo = codigo
        self.pos = 0
        self.pila_indent = [0]

    def generar_tokens(self):
        tokens = []
        lineas = self.codigo.splitlines()

        for linea in lineas:
            # Eliminar comentarios
            linea_limpia = linea.split('#')[0]
            if not linea_limpia.strip():
                continue

            # Calcular indentación
            indent = len(linea_limpia) - len(linea_limpia.lstrip(' '))
            if indent > self.pila_indent[-1]:
                self.pila_indent.append(indent)
                tokens.append(Token('INDENT'))
            elif indent < self.pila_indent[-1]:
                while self.pila_indent[-1] > indent:
                    self.pila_indent.pop()
                    tokens.append(Token('DEDENT'))

            # Tokenizar línea mediante Regex
            patron = r'(".*?"|\d+\.\d+|\d+|\w+|==|>=|<=|>|<|=|\+|\-|\*|\/|\(|\)|:)'
            for match in re.findall(patron, linea_limpia.strip()):
                if match.startswith('"'):
                    tokens.append(Token('TEXTO', match[1:-1]))
                elif match.replace('.', '', 1).isdigit():
                    val = float(match) if '.' in match else int(match)
                    tokens.append(Token('NUMERO', val))
                elif match in self.PALABRAS_CLAVE:
                    tokens.append(Token(self.PALABRAS_CLAVE[match], match))
                elif match.isidentifier():
                    tokens.append(Token('IDENTIFICADOR', match))
                else:
                    MAPA_OP = {'=': 'ASIGNAR', '+': 'SUMA', '-': 'RESTA', '*': 'MULT', '/': 'DIV',
                               '==': 'IGUAL_IGUAL', '>=': 'MAYOR_IGUAL', '<=': 'MENOR_IGUAL',
                               '>': 'MAYOR', '<': 'MENOR', '(': 'PAR_IZQ', ')': 'PAR_DER', ':': 'DOS_PUNTOS'}
                    tokens.append(Token(MAPA_OP.get(match, 'DESCONOCIDO'), match))

            tokens.append(Token('NUEVA_LINEA', '\n'))

        while len(self.pila_indent) > 1:
            self.pila_indent.pop()
            tokens.append(Token('DEDENT'))

        tokens.append(Token('FIN'))
        return tokens