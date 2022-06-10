# BKG za našu Snail implementaciju
#
# start -> naredbe
# naredbe -> naredbe naredba | naredba
#
# naredba   -> pridruživanje
#            | printanje
#            | grananje
#            | definiranje
#            | vraćanje
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
# vraćanje  -> VRATI TOČKAZ
#            | VRATI izraz TOČKAZ
#
# definiranje -> DEF ime OTV parametri ZATV naredbe ENDDEF
# parametri -> ime | parametri ZAREZ ime
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
#            | IME# poziv
#            | OTV izraz ZATV
#            | MINUS faktor
#
# poziv -> OTV ZATV | OTV argumenti ZATV
# argumenti -> izraz | argumenti ZAREZ izraz

from inspect import Parameter
from vepar import *

from lekser import *
from snailast import *
from util import get_test_dir


class P(Parser):
    def start(p) -> 'Program':
        p.imef = None
        p.parametrif = None
        p.funkcije = Memorija(redefinicija=False)
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
            return p.pridruživanje(ime)
        elif p >= T.PRINT:
            return p.printanje()
        elif p >= T.IF:
            return p.grananje()
        elif p >= T.DEF:
            return p.definiranje()
        elif p >> T.RETURN:
            return p.vraćanje()

    def pridruživanje(p, ime) -> 'Pridruživanje':
        p >> T.PRIDRUŽI
        izraz = p.izraz()
        p >> T.TOČKAZ
        return Pridruživanje(ime, izraz)

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

    def definiranje(p) -> 'Funkcija':
        ime = p >> T.IME
        p >> T.OTV
        parametri = p.parametri()
        p >> T.ZATV
        tijelo = p.naredbe(T.ENDDEF, pojedi=True)
        fja = Funkcija(ime, parametri, tijelo)
        p.imef = ime
        p.parametrif = parametri
        p.funkcije[ime] = fja
        return fja

    def vraćanje(p):
        if p > T.TOČKAZ:
            return Vraćanje(nenavedeno)
        else:
            vratiti = p.izraz()
            p >> T.TOČKAZ
            return vratiti

    def izraz(p):
        stablo = p.član()
        while op := p >= {T.PLUS, T.MINUS, T.MANJE, T.VECE, T.JMANJE, T.JVECE, T.JEDNAKO, T.NEJEDNAKO}:
            desni = p.član()
            stablo = Infix(op, stablo, desni)
        return stablo

    def član(p) -> 'faktor|Infix':
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
            return Infix(T.MINUS, 0, p.faktor())
        elif broj := p >= T.BROJ:
            return broj
        else:
            ime = p >> T.IME
            return p.možda_poziv(ime)

    def možda_poziv(p, ime) -> 'Poziv|IME':
        if ime in p.funkcije:
            funkcija = p.funkcije[ime]
            return Poziv(funkcija, p.argumenti(funkcija.parametri))
        elif ime == p.imef:
            return Poziv(nenavedeno, p.argumenti(p.parametrif))
        else:
            return ime

    def parametri(p):
        parametri = [p >> T.IME]
        while p >= T.ZAREZ:
            parametri.append(p >> T.IME)
        return parametri

    def argumenti(p):
        izrazi = [p.izraz()]
        while p >= T.ZAREZ:
            izrazi.append(p.izraz())
        return izrazi


def test(src):
    snail(src)
    prikaz(kod := P(src), 8)


if __name__ == "__main__":
    from util import test_on
    test_on(test, path=get_test_dir())
