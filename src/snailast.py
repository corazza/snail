# Apstraktna sintaksna stabla
# Program: naredbe: [naredba]
# naredba:

from vepar import *


class Program(AST):
    naredbe: 'naredba*'

    def izvrši(program):
        rt.mem = Memorija()
        for naredba in program.naredbe:
            naredba.izvrši()


class Pridruživanje(AST):
    ime: 'IME'
    izraz: 'izraz'


class Printanje(AST):
    sadržaj: 'izraz|STRING#|NEWLINE'


class Grananje(AST):
    provjera: 'izraz'
    ako: 'naredba+'
    inače: '(naredba+)?'


class Infix(AST):
    operator: 'PLUS|MINUS|...'
    lijevi: 'faktor'
    desni: 'faktor'
