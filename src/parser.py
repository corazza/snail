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
# izraz -> član
#        | izraz PLUS član
#        | izraz MINUS član
#
# član -> faktor
#       | član PUTA faktor
#       | član DIV faktor
#       | član MANJE faktor
#       | član VECE faktor
#       | član JMANJE faktor
#       | član JVECE faktor
#       | član JEDNAKO faktor
#       | član NEJEDNAKO faktor
#
# faktor    -> BROJ#
#            | IME#
#            | OTV izraz ZATV
#            | MINUS faktor

from vepar import *

from lekser import *
from snailast import *
from util import get_test_dir


class P(Parser):
    def start(p) -> 'Program':
        return Program(p.naredbe(KRAJ))

    def naredbe(p, until, pojedi=False) -> 'naredba+':
        naredbe = [p.naredba()]
        while not p > until:
            naredbe.append(p.naredba())
        if pojedi:
            p >> until
        return naredbe

    def naredba(p) -> 'pridruživanje|printanje|grananje':
        if ime := p >= T.IME:
            vrati = p.pridruživanje(ime)
        elif p >= T.PRINT:
            vrati = p.printanje()
        elif p >> T.IF:
            vrati = p.grananje()
        return vrati

    def pridruživanje(p, ime) -> 'Pridruživanje':
        p >> T.PRIDRUŽI
        izraz = p.izraz()
        p >> T.TOČKAZ
        return Pridruživanje(ime, izraz)

    def izraz(p):
        stablo = p.član()
        while op := p >= {T.PLUS, T.MINUS, T.MANJE, T.VECE, T.JMANJE, T.JVECE, T.JEDNAKO, T.NEJEDNAKO}:
            desni = p.član()
            stablo = Infix(op, stablo, desni)
        return stablo

    def član(p) -> 'Faktor|Infix':
        stablo = p.faktor()
        while op := p >= {T.PUTA, T.DIV}:
            desni = p.faktor()
            stablo = Infix(op, stablo, desni)
        return stablo

    def faktor(p):
        if p >= T.OTV:
            izraz = p.izraz()
            p >> T.ZATV
            return izraz
        elif p >= T.MINUS:
            return Suprotan(p.faktor())
        elif broj := p >= T.BROJ:
            return broj
        else:
            ime = p >> T.IME
            return ime

    def grananje(p) -> 'Grananje':
        provjera = p.izraz()
        p >> T.THEN
        ako = p.naredbe({T.ELSE, T.ENDIF})
        if p >= T.ENDIF:
            return Grananje(provjera, ako, nenavedeno)
        elif p >= T.ELSE:
            inače = p.naredbe(T.ENDIF, pojedi=True)
            return Grananje(provjera, ako, inače)
        else:
            exit("Sintaktička greška")

    def printanje(p) -> 'Printanje':
        if p >= T.NEWLINE:
            p >> T.TOČKAZ
            return Printanje(T.NEWLINE)
        elif string := p >= T.STRING:
            p >> T.TOČKAZ
            return Printanje(string)
        else:
            izraz = p.izraz()
            p >> T.TOČKAZ
            return Printanje(izraz)


def test(src):
    snail(src)
    prikaz(kod := P(src), 8)


if __name__ == "__main__":
    from util import test_on
    test_on(test, path=get_test_dir())
