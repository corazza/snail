# BKG za našu Snail implementaciju
#
# start -> naredbe
# naredbe -> naredbe naredba | naredba
#
# naredba   -> pridruživanje
#            | printanje
#            | grananje
#
# pridruživanje -> IME# JEDNAKO izraz TOČKAZ
#
# printanje -> PRINT izraz TOČKAZ
#            | PRINT STRING# TOČKAZ
#            | PRINT NEWLINE TOČKAZ
#
# grananje  -> IF izraz THEN naredbe ENDIF
#            | IF izraz THEN naredbe ELSE naredbe ENDIF
#
# izraz -> OTV izraz ZATV
#        | izraz PLUS izraz
#        | izraz MINUS izraz
#        | izraz PUTA izraz
#        | izraz DIV izraz
#        | izraz MANJE izraz
#        | izraz VECE izraz
#        | izraz JMANJE izraz
#        | izraz JVECE izraz
#        | izraz JEDNAKO izraz
#        | izraz NEJEDNAKO izraz
#        | MINUS izraz
#        | BROJ#
#        | IME#

from vepar import *

from lekser import *
from snailast import *


class P(Parser):
    def start(p) -> 'Program':
        return Program(p.naredbe(KRAJ))

    def naredbe(p, until) -> 'naredba+':
        naredbe = [p.naredba()]
        while not p > until:
            naredbe.append(p.naredba())
        return naredbe

    def naredba(p) -> 'pridruživanje|printanje|grananje':
        if p > T.IME:
            return p.pridruživanje()
        elif p > T.PRINT:
            return p.printanje()
        elif p > T.IF:
            return p.grananje()

    def pridruživanje(p) -> 'Pridruživanje':
        ime = p >> T.IME
        p >> T.PRIDRUŽI
        izraz = p >> p.izraz()
        return Pridruživanje(ime, izraz)

    def printanje(p) -> 'Printanje':
        if p > T.NEWLINE:
            return Printanje(T.NEWLINE)
        elif p > T.STRING:
            return Printanje(p >= T.STRING)
        else:
            return Printanje(p.izraz())

    def izraz(p) -> 'Infix':
        if p > T.OTV:
            p >> T.OTV
            izraz = p.izraz()
            p >> T.ZATV
            return izraz
        elif p > T.BROJ:
            return p >= T.BROJ
        elif p > T.IME:
            return p >= T.IME
        elif p > T.MINUS:
            p >> T.MINUS
            return Infix(T.MINUS, 0, p.izraz())
        else:
            lijevi = p.izraz()
            operator = p >= {T.PLUS, T.MINUS, T.PUTA, T.DIV, T.MANJE,
                             T.VECE, T.JMANJE, T.JVECE, T.JEDNAKO, T.NEJEDNAKO}
            desni = p.izraz()
            return Infix(operator, lijevi, desni)

    def grananje(p) -> 'Grananje':
        p >> T.IF
        p >> T.OTV
        provjera = p.izraz()
        p >> T.ZATV
        p >> T.THEN
        ako = p.naredbe()
        if p > T.ENDIF:
            return Grananje(provjera, ako, p.naredba())
        else:
            inače = p.naredbe