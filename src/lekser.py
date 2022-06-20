from vepar import *

from util import *


class T(TipoviTokena):
    IF, THEN, ELSE, ENDIF, DEF, MEMO, AS, ENDDEF =\
        'if', 'then', 'else', 'endif', 'def', 'memo', 'as', 'enddef'
    DATA, ENDDATA, MATCH, ENDMATCH = 'data', 'enddata', 'match', 'endmatch'
    PLUS, MINUS, PUTA, DIV = '+-*/'
    MANJE, VECE, JMANJE, JVECE, JEDNAKO, NEJEDNAKO, SLIJEDI = '<', '>', '<=', '>=', '==', '!=', '=>'
    TERNARNI = '?'
    NEGACIJA, KONJEKSP = '!$'
    LOGI, LOGILI = '&', '|'
    OTV, ZATV, PRIDRUŽI, TOČKAZ, NAVODNIK, ZAREZ = '()=;",'
    LET, OFTYPE, FTYPE = 'let', ':', '->'
    INT, BOOL, STRINGT, UNITT = 'int', 'bool', 'string', 'unit'
    PRINT, INPUT, NEWLINE, TOINT = '__print', '__input', '__newline', '__to_int'
    RETURN, IMPORT = 'return', 'import'

    class BROJ(Token):
        def typecheck(self, scope, unutar, meta):
            return Token(T.INT)

        def vrijednost(self, mem, unutar):
            return int(self.sadržaj)

    class STRING(Token):
        def typecheck(self, scope, unutar, meta):
            return Token(T.STRINGT)

        def vrijednost(self, mem, unutar):
            return self.sadržaj.strip('"')

    class UNIT(Token):
        def typecheck(self, scope, unutar, meta):
            return Token(T.UNITT)

        def __str__(self):
            # Vraća self kao vrijednost, pa treba __str__
            return "()"

        def vrijednost(self, mem, unutar):
            return self

    class IME(Token):
        def typecheck(self, scope, unutar, meta):
            return scope[self]

        def vrijednost(self, scope, unutar):
            return scope[self]

        def __str__(self):
            return self.sadržaj

    class VELIKOIME(Token):
        def typecheck(self, scope, unutar, meta):
            raise SemantičkaGreška('tipovi nisu vrijednosti')

        def vrijednost(self, mem, unutar):
            raise SemantičkaGreška('tipovi nisu vrijednosti')

        def __str__(self):
            return self.sadržaj

    class VARTIPA(Token):
        def typecheck(self, scope, unutar, meta):
            """Shvaćeno je da se zapravo type checka vanjski kontekst, tj. postojanje VARTIPA"""
            if self not in scope:
                raise SemantičkaGreška(f'nije uvedena varijabla {self} za tip')
            return self

        def vrijednost(self, mem, unutar):
            raise SemantičkaGreška('varijable tipova nisu vrijednosti')

        def __str__(self):
            return self.sadržaj


@lexer
def snail(lex):
    for znak in lex:
        if znak.isspace():
            lex.zanemari()
        elif znak == '?':
            yield lex.token(T.TERNARNI)
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
                lex <= {'\n', ''}
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
        elif znak == '_':
            lex * {str.isalpha, '_'}
            yield lex.literal(T)
        elif znak.isalpha():
            if znak.isupper() and lex > str.isupper:
                lex * {str.isalpha}
                yield lex.token(T.UNIT)
            elif znak.isupper():
                if lex > str.isalpha:
                    lex * {str.isalnum, '_'}
                    yield lex.literal_ili(T.VELIKOIME)
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
            yield lex.literal(T)


if __name__ == "__main__":
    from util import test_on
    test_on(snail)
