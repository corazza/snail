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
#            | INPUT IME#
#            | IME# poziv
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
from util import *


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
        return Naredbe(naredbe)

    def naredba(p) -> 'pridruživanje|printanje|grananje':
        if ime := p >= T.IME:
            return p.poziv_ili_pridruživanje(ime)
        elif p >= T.PRINT:
            return p.printanje()
        elif p >= T.INPUT:
            return p.input()
        elif p >= T.IF:
            return p.grananje()
        elif p >= T.DEF:
            return p.definiranje()
        elif p >> T.RETURN:
            return p.vraćanje()

    def poziv_ili_pridruživanje(p, ime) -> 'Poziv|Pridruživanje':
        if p >= T.PRIDRUŽI:
            izraz = p.izraz()
            p >> T.TOČKAZ
            return Pridruživanje(ime, izraz)
        else:
            if ime in p.funkcije:
                funkcija = p.funkcije[ime]
                parametri = funkcija.parametri
            elif ime == p.imef:
                funkcija = nenavedeno
                parametri = p.parametrif
            else:
                raise SintaksnaGreška('nepoznata funkcija')
            argumenti = p.argumenti(parametri)
            p >> T.TOČKAZ
            return Poziv(funkcija, argumenti)

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
        if newline := p >= T.NEWLINE:
            p >> T.TOČKAZ
            return Printanje(newline)
        elif string := p >= T.STRING:
            p >> T.TOČKAZ
            return Printanje(string)
        else:
            izraz = p.izraz()
            p >> T.TOČKAZ
            return Printanje(izraz)

    def input(p) -> 'Input':
        ime = p >> T.IME
        p >> T.TOČKAZ
        return Unos(ime)

    def definiranje(p) -> 'Funkcija':
        ime = p >> T.IME
        p.imef = ime
        parametri = p.parametri()
        p.parametrif = parametri
        tijelo = p.naredbe(T.ENDDEF, pojedi=True)
        fja = Funkcija(ime, parametri, tijelo)
        p.funkcije[ime] = fja
        return fja

    def vraćanje(p):
        if p >= T.TOČKAZ:
            return Vraćanje(nenavedeno)
        else:
            izraz = p.izraz()
            p >> T.TOČKAZ
            return Vraćanje(izraz)

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
        elif minus := p >= T.MINUS:
            return Infix(minus, 0, p.faktor())
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
        p >> T.OTV
        parametri = [p >> T.IME]
        while p >= T.ZAREZ:
            parametri.append(p >> T.IME)
        p >> T.ZATV
        return parametri

    def argumenti(p, parametri):
        broj_parametara = len(parametri)
        izrazi = []
        p >> T.OTV
        for i in range(broj_parametara):
            izrazi.append(p.izraz())
            if i < broj_parametara - 1:
                p >> T.ZAREZ
        p >> T.ZATV
        return izrazi


def test(src):
    prikaz(program := P(src), 8)
    print()
    print('=== pokretanje ===')
    program.izvrši()


if __name__ == "__main__":
    from util import test_on
    test_on(test)
