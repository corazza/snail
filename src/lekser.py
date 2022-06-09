from vepar import *


class T(TipoviTokena):
    FOR, COUT, ENDL, IF = 'for', 'cout', 'endl', 'if'
    OOTV, OZATV, VOTV, VZATV, MANJE, JEDNAKO, TOČKAZ = '(){}<=;'
    PLUSP, PLUSJ, MMANJE, JJEDNAKO = '++', '+=', '<<', '=='
    class BREAK(Token):
        literal = 'break'
        def izvrši(self): raise Prekid
    class BROJ(Token):
        def vrijednost(self): return int(self.sadržaj)
    class IME(Token):
        def vrijednost(self): return rt.mem[self]

@lexer
def snail(lex):
    for znak in lex:
        if znak.isspace(): lex.zanemari()
        elif znak == '+':
            if lex >= '+': yield lex.token(T.PLUSP)
            elif lex >= '=': yield lex.token(T.PLUSJ)
            else: raise lex.greška('u ovom jeziku nema samostalnog +')
        elif znak == '<': yield lex.token(T.MMANJE if lex >= '<' else T.MANJE)
        elif znak == '=':
            yield lex.token(T.JJEDNAKO if lex >= '=' else T.JEDNAKO)
        elif znak.isalpha() or znak == '_':
            lex * {str.isalnum, '_'}
            yield lex.literal_ili(T.IME)
        elif znak.isdecimal():
            lex.prirodni_broj(znak)
            yield lex.token(T.BROJ)
        else: yield lex.literal(T)

snail(ulaz := '''
    for ( i = 8 ; i < 13 ; i += 2 ) {
        for(j=0; j<5; j++) {
            cout<<i<<j;
            if(i == 10) if (j == 1) break;
        }
        cout<<i<<endl;
    }
''')

# prikaz(F := P(ulaz))
# prikaz(F := F.optim())
