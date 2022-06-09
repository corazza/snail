from vepar import *


class T(TipoviTokena):
    IF, THEN, ELSE, ENDIF, PRINT, NEWLINE = 'if', 'then', 'else', 'endif', 'print', 'newline'
    PLUS, MINUS, PUTA, DIV = '+-*/'
    MANJE, VECE, JMANJE, JVECE, JJEDNAKO, NEJEDNAKO = '<', '>', '<=', '>=', '==', '!='
    OTV, ZATV, PRIDRUŽI, TOČKAZ, NAVODNIK = '()=;"'

    class BROJ(Token):
        def vrijednost(self): return int(self.sadržaj)
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
        elif znak == '!':
            lex >> '='
            yield lex.token(T.NEJEDNAKO)
        elif znak == '/' and lex > '/':
            lex <= '\n'
        elif znak.isalpha() or znak == '_':
            lex * {str.isalnum, '_'}
            yield lex.literal_ili(T.IME)
        elif znak.isdecimal():
            lex.prirodni_broj(znak)
            yield lex.token(T.BROJ)
        else: yield lex.literal(T)

if __name__ == "__main__":
    import os, glob
    path = '../snail'
    for filename in glob.glob(os.path.join(path, '*.txt')):
        with open(os.path.join(os.getcwd(), filename), 'r') as f:
            snail(f.read())

# prikaz(F := P(ulaz))
# prikaz(F := F.optim())
