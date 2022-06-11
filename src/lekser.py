from vepar import *

from util import *


class T(TipoviTokena):
    IF, THEN, ELSE, ENDIF, PRINT, INPUT, NEWLINE, DEF, AS, ENDDEF, RETURN =\
        'if', 'then', 'else', 'endif', 'print', 'input', 'newline', 'def', 'as', 'enddef', 'return'
    PLUS, MINUS, PUTA, DIV = '+-*/'
    MANJE, VECE, JMANJE, JVECE, JEDNAKO, NEJEDNAKO = '<', '>', '<=', '>=', '==', '!='
    OTV, ZATV, PRIDRUŽI, TOČKAZ, NAVODNIK, ZAREZ = '()=;",'
    LET, OFTYPE, FTYPE = 'let', ':', '->'
    INT, BOOL, STRINGT, UNIT = 'int', 'bool', 'string', 'unit'

    class BROJ(Token):
        def typecheck(self, scope, unutar):
            return self

        def vrijednost(self, mem, unutar):
            return int(self.sadržaj)

    class STRING(Token):
        def typecheck(self, scope, unutar):
            return self

        def vrijednost(self, mem, unutar):
            return self.sadržaj.strip('"')

    class IME(Token):
        def typecheck(self, scope, unutar):
            return scope[self]

        def vrijednost(self, mem, unutar):
            if self in mem:
                return mem[self]
            else:
                return rt.mem[self]


@lexer
def snail(lex):
    for znak in lex:
        if znak.isspace():
            lex.zanemari()
        elif znak == '<':
            yield lex.token(T.JMANJE if lex >= '=' else T.MANJE)
        elif znak == '>':
            yield lex.token(T.JVECE if lex >= '=' else T.VECE)
        elif znak == '=':
            yield lex.token(T.JEDNAKO if lex >= '=' else T.PRIDRUŽI)
        elif znak == '/':
            if lex > '/':
                lex <= '\n'
                lex.zanemari()
            elif lex > '*':
                while True:
                    lex.pročitaj_do('*', uključivo=True, više_redova=True)
                    if lex > '/':
                        next(lex)
                        break
                lex.zanemari()
            else:
                yield lex.literal(T)
        elif znak == '-':
            yield lex.token(T.FTYPE if lex >= '>' else T.MINUS)
        elif znak == '"':
            lex <= '"'
            yield lex.token(T.STRING)
        elif znak.isalpha() or znak == '_':
            lex * {str.isalnum, '_'}
            yield lex.literal_ili(T.IME)
        elif znak.isdecimal():
            lex.prirodni_broj(znak)
            yield lex.token(T.BROJ)
        else:
            yield lex.literal(T)


if __name__ == "__main__":
    from util import test_on
    test_on(snail)

# prikaz(F := P(ulaz))
# prikaz(F := F.optim())
