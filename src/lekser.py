from vepar import *


class T(TipoviTokena):
    IF, THEN, ELSE, ENDIF, PRINT, NEWLINE = 'if', 'then', 'else', 'endif', 'print', 'newline'
    PLUS, MINUS, PUTA, DIV = '+-*/'
    MANJE, VECE, JMANJE, JVECE, JJEDNAKO, NEJEDNAKO = '<', '>', '<=', '>=', '==', '!='
    OTV, ZATV, PRIDRUŽI, TOČKAZ, NAVODNIK = '()=;"'

    class BROJ(Token):
        def vrijednost(self): return int(self.sadržaj)

    class STRING(Token):
        def vrijednost(self): return self.sadržaj.strip('"')

    class IME(Token):
        def vrijednost(self): return rt.mem[self]


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
            yield lex.token(T.JJEDNAKO if lex >= '=' else T.PRIDRUŽI)
        elif znak == '/':
            if lex > '/':
                lex <= '\n'
                lex.zanemari()
            elif lex > '*':
                while True:
                    lex.pročitaj_do('*', uključivo=True, više_redova=True)
                    if lex > '/':
                        break
                lex.zanemari()
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
    test_on(snail, path='../primjeri_test')

# prikaz(F := P(ulaz))
# prikaz(F := F.optim())
