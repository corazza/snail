# Apstraktna sintaksna stabla
# Program: naredbe: [naredba]
# naredba:

from vepar import *


class Program(AST):
    naredba: 'naredba*'

    def izvrši(program):
        rt.mem = Memorija()
        for naredba in program.naredbe:
            naredba.izvrši()


class Pridruživanje(AST):
    ime: 'IME'
    izraz: 'izraz'


class Printanje(AST):
    sadržaj: 'izraz|STRING#|NEWLINE'


class Infix(AST):
    operator: 'PLUS|MINUS|PUTA|DIV|MANJE|VECE|JMANJE|JVECE|JEDNAKO|NEJEDNAKO'
    lijevi: 'izraz'
    desni: 'izraz'

class Grananje(AST):
    provjera: 'izraz'
    ako: 'naredba+'
    inače: '(naredba+)?'
