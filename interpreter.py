# interpreter.py
from parser_es import (
    NodoLiteral, NodoVariable, NodoAsignacion, NodoImprimir,
    NodoOpBinaria, NodoOpUnaria, NodoSi, NodoMientras,
    NodoLeer, NodoConversion
)

class Interprete:
    def __init__(self):
        self.variables = {}

    def ejecutar(self, instrucciones):
        for inst in instrucciones:
            self.visitar(inst)

    def visitar(self, nodo):
        if isinstance(nodo, NodoLiteral):
            return nodo.valor
        elif isinstance(nodo, NodoVariable):
            if nodo.nombre in self.variables:
                return self.variables[nodo.nombre]
            raise Exception(f"La variable '{nodo.nombre}' no está definida.")
        elif isinstance(nodo, NodoAsignacion):
            val = self.visitar(nodo.expresion)
            self.variables[nodo.nombre] = val
            return val
        elif isinstance(nodo, NodoImprimir):
            print(self.visitar(nodo.expresion))
        elif isinstance(nodo, NodoOpUnaria):
            return not bool(self.visitar(nodo.expr))
        elif isinstance(nodo, NodoOpBinaria):
            if nodo.op == 'y': return bool(self.visitar(nodo.izq)) and bool(self.visitar(nodo.der))
            if nodo.op == 'o': return bool(self.visitar(nodo.izq)) or bool(self.visitar(nodo.der))
            
            i, d = self.visitar(nodo.izq), self.visitar(nodo.der)
            ops = {'+': i + d, '-': i - d, '*': i * d, '/': i / d if d != 0 else Exception("División entre cero"),
                   '>': i > d, '<': i < d, '>=': i >= d, '<=': i <= d, '==': i == d}
            if isinstance(ops[nodo.op], Exception): raise ops[nodo.op]
            return ops[nodo.op]
        elif isinstance(nodo, NodoSi):
            if self.visitar(nodo.condicion):
                self.ejecutar(nodo.bloque_si)
            elif nodo.bloque_sino:
                self.ejecutar(nodo.bloque_sino)
        elif isinstance(nodo, NodoMientras):
            while self.visitar(nodo.condicion):
                self.ejecutar(nodo.bloque)
        elif isinstance(nodo, NodoLeer):
            msg = str(self.visitar(nodo.mensaje)) if nodo.mensaje else ""
            return input(msg)
        elif isinstance(nodo, NodoConversion):
            v = self.visitar(nodo.expresion)
            if nodo.tipo_destino == 'ENTERO': return int(v)
            if nodo.tipo_destino == 'DECIMAL': return float(v)
            elif nodo.tipo_destino == 'TEXTO_FUNC': 
                # Convertimos a string y quitamos espacios para validar si solo hay letras/caracteres
                val_str = str(v)
                # Permite letras, tildes, 'ñ' y espacios, pero rechaza números
                texto_sin_espacios = val_str.replace(" ", "")
                if texto_sin_espacios and not texto_sin_espacios.isalpha():
                    raise Exception(f"Error de tipo: Se esperaba solo texto, pero se ingresó un número o carácter no válido ('{val_str}')")
                return val_str
            if nodo.tipo_destino == 'BOOLEANO':
                return v.strip().lower() in ('si', 's', 'verdadero', 'true', '1') if isinstance(v, str) else bool(v)