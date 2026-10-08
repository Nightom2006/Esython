# parser_es.py
from dataclasses import dataclass

@dataclass
class NodoLiteral: valor: object
@dataclass
class NodoVariable: nombre: str
@dataclass
class NodoAsignacion: nombre: str; expresion: object
@dataclass
class NodoImprimir: expresion: object
@dataclass
class NodoOpBinaria: izq: object; op: str; der: object
@dataclass
class NodoOpUnaria: op: str; expr: object
@dataclass
class NodoSi: condicion: object; bloque_si: list; bloque_sino: list = None
@dataclass
class NodoMientras: condicion: object; bloque: list
@dataclass
class NodoLeer: mensaje: object = None
@dataclass
class NodoConversion: tipo_destino: str; expresion: object

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    @property
    def actual(self):
        return self.tokens[self.pos]

    def consumir(self, tipo):
        tok = self.actual
        if tok.tipo == tipo or tok.valor == tipo:
            self.pos += 1
            return tok
        raise Exception(f"Sintaxis inválida: se esperaba '{tipo}' y se encontró '{tok.tipo}' ({tok.valor})")

    def parsear(self):
        instrucciones = []
        while self.actual.tipo != 'FIN':
            if self.actual.tipo in ('NUEVA_LINEA', 'DEDENT'):
                self.pos += 1
                continue
            instrucciones.append(self.parsear_instruccion())
        return instrucciones

    def parsear_bloque(self):
        self.consumir('DOS_PUNTOS')
        if self.actual.tipo == 'NUEVA_LINEA': self.pos += 1
        self.consumir('INDENT')
        bloque = []
        while self.actual.tipo not in ('DEDENT', 'FIN'):
            if self.actual.tipo == 'NUEVA_LINEA':
                self.pos += 1
                continue
            bloque.append(self.parsear_instruccion())
        if self.actual.tipo == 'DEDENT': self.pos += 1
        return bloque

    def parsear_instruccion(self):
        t = self.actual.tipo
        if t == 'IMPRIMIR':
            self.pos += 1
            return NodoImprimir(self.parsear_expr())
        elif t == 'VARIABLE':
            self.pos += 1
            nom = self.consumir('IDENTIFICADOR').valor
            self.consumir('ASIGNAR')
            return NodoAsignacion(nom, self.parsear_expr())
        elif t == 'SI':
            self.pos += 1
            cond = self.parsear_expr()
            bloque_si = self.parsear_bloque()
            bloque_sino = self.parsear_bloque() if self.actual.tipo == 'SINO' and self.consumir('SINO') else None
            return NodoSi(cond, bloque_si, bloque_sino)
        elif t == 'MIENTRAS':
            self.pos += 1
            return NodoMientras(self.parsear_expr(), self.parsear_bloque())
        return self.parsear_expr()

    def parsear_expr(self):
        return self._binario(self.parsear_and, ('O',))

    def parsear_and(self):
        return self._binario(self.parsear_not, ('Y',))

    def parsear_not(self):
        if self.actual.tipo == 'NO':
            self.pos += 1
            return NodoOpUnaria('no', self.parsear_not())
        return self.parsear_comp()

    def parsear_comp(self):
        return self._binario(self.parsear_suma, ('MAYOR', 'MENOR', 'MAYOR_IGUAL', 'MENOR_IGUAL', 'IGUAL_IGUAL'))

    def parsear_suma(self):
        return self._binario(self.parsear_mult, ('SUMA', 'RESTA'))

    def parsear_mult(self):
        return self._binario(self.parsear_prim, ('MULT', 'DIV'))

    def _binario(self, func_sig, tipos):
        izq = func_sig()
        while self.actual.tipo in tipos:
            op = self.actual.valor
            self.pos += 1
            izq = NodoOpBinaria(izq, op, func_sig())
        return izq

    def parsear_prim(self):
        tok = self.actual
        if tok.tipo == 'PAR_IZQ':
            self.pos += 1
            expr = self.parsear_expr()
            self.consumir('PAR_DER')
            return expr
        elif tok.tipo in ('ENTERO', 'DECIMAL', 'TEXTO_FUNC', 'BOOLEANO'):
            self.pos += 1
            self.consumir('PAR_IZQ')
            expr = self.parsear_expr()
            self.consumir('PAR_DER')
            return NodoConversion(tok.tipo, expr)
        elif tok.tipo == 'LEER':
            self.pos += 1
            msg = None
            if self.actual.tipo == 'PAR_IZQ':
                self.pos += 1
                if self.actual.tipo != 'PAR_DER': msg = self.parsear_expr()
                self.consumir('PAR_DER')
            return NodoLeer(msg)
        elif tok.tipo in ('NUMERO', 'TEXTO'):
            self.pos += 1
            return NodoLiteral(tok.valor)
        elif tok.tipo in ('VERDADERO', 'FALSO'):
            self.pos += 1
            return NodoLiteral(tok.tipo == 'VERDADERO')
        elif tok.tipo == 'IDENTIFICADOR':
            self.pos += 1
            return NodoVariable(tok.valor)
        raise Exception(f"Expresión no válida cerca de '{tok.valor}'")