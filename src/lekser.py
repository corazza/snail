from vepar import *

from util import *


class T(TipoviTokena):
    IF, THEN, ELSE, ENDIF, NEWLINE, DEF, AS, ENDDEF, RETURN =\
        'if', 'then', 'else', 'endif', 'newline', 'def', 'as', 'enddef', 'return'
    DATA, ENDDATA, MATCH, ENDMATCH = 'data', 'enddata', 'match', 'endmatch'
    PLUS, MINUS, PUTA, DIV = '+-*/'
    MANJE, VECE, JMANJE, JVECE, JEDNAKO, NEJEDNAKO, SLIJEDI = '<', '>', '<=', '>=', '==', '!=', '=>'
    OTV, ZATV, PRIDRUŽI, TOČKAZ, NAVODNIK, ZAREZ = '()=;",'
    LET, OFTYPE, FTYPE = 'let', ':', '->'
    INT, BOOL, STRINGT, UNITT = 'int', 'bool', 'string', 'unit'
    PRINT, INPUT = 'print', 'input'

    class BROJ(Token):
        def typecheck(self, scope, unutar):
            return Token(T.INT)

        def vrijednost(self, mem, unutar):
            return int(self.sadržaj)

    class STRING(Token):
        def typecheck(self, scope, unutar):
            return Token(T.STRING)

        def vrijednost(self, mem, unutar):
            return self.sadržaj.strip('"')

    class IME(Token):
        def typecheck(self, scope, unutar):
            return scope[self]
            # if self in scope:
            #     return scope[self]
            # else:
            #     return None # tip bi se trebao kasnije odlučiti

        def vrijednost(self, mem, unutar):
            if self in mem:
                return mem[self]
            else:
                return rt.mem[self]

    class VELIKOIME(Token):
        def typecheck(self, scope, unutar):
            raise SemantičkaGreška('tipovi nisu vrijednosti')

        def vrijednost(self, mem, unutar):
            raise SemantičkaGreška('tipovi nisu vrijednosti')

    class VARTIPA(Token):
        def typecheck(self, scope, unutar):
            """Shvaćeno je da se zapravo type checka vanjski kontekst, tj. postojanje VARTIPA"""
            if self not in scope:
                raise SemantičkaGreška(f'nije uvedena varijabla {self} za tip')
            return self

        def vrijednost(self, mem, unutar):
            raise SemantičkaGreška('varijable tipova nisu vrijednosti')


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
            if lex >= '=':
                yield lex.token(T.JEDNAKO)
            elif lex >= '>':
                yield lex.token(T.SLIJEDI)
            else:
                yield lex.token(T.PRIDRUŽI)
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
        elif znak.isalpha():
            if znak.isupper():
                if lex > str.isalpha:
                    lex * {str.isalnum, '_'}
                    yield lex.token(T.VELIKOIME)
                else:
                    lex * {str.isalnum, '_'}
                    yield lex.token(T.VARTIPA)
            else:
                lex * {str.isalnum, '_'}
                yield lex.literal_ili(T.IME)
        elif znak.isdecimal():
            lex.prirodni_broj(znak)
            yield lex.token(T.BROJ)
        else:
            # print('here1')
            # lex * {str.isalnum, '_'}
            # print('here2')
            yield lex.literal(T)


if __name__ == "__main__":
    from util import test_on
    test_on(snail)

# prikaz(F := P(ulaz))
# prikaz(F := F.optim())
