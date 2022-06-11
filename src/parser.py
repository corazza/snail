# TODO provjeriti i urediti BKG
## BKG za našu Snail implementaciju
#
# start -> naredbe
# naredbe -> naredbe naredba | naredba
#
# naredba   -> pridruživanje
#            | definiranje
#            | definiranje_tipa
#            | printanje
#            | grananje
#            | funkcija
#            | vraćanje
#            | INPUT IME#
#            | IME# poziv
#
# definiranje_tipa -> DATA IME# MANJE parametri_tipa VECE AS varijante ENDDATA
# parametri_tipa -> VARTIPA# | parametri_tipa ZAREZ VARTIPA#
# varijante -> varijanta | varijante ZAREZ varijanta
# varijanta -> IME# | OTV članovi_varijante ZATV
# članovi_varijante -> IME# | članovi_varijante ZAREZ tip
# tip -> INT | BOOL | STRINGT | UNIT | IMETIPA#
#
# definiranje -> LET tipizirano JEDNAKO izraz TOČKAZ
# tipizirano -> IME# OFTYPE tip
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
# funkcija -> DEF ime OTV parametri ZATV FTYPE tip AS naredbe ENDDEF
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
from signal import default_int_handler
from vepar import *

from lekser import *
from snailast import *
from util import *


class P(Parser):
    def start(p) -> 'Program':
        p.imef = None
        p.parametrif = None
        p.tipf = None
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
            return p.funkcija()
        elif p >= T.LET:
            return p.definiranje()
        elif p >= T.DATA:
            return p.definiranje_tipa()
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

    def definiranje(p) -> 'Definiranje':
        tipizirano = p.tipizirano()
        p >> T.PRIDRUŽI
        izraz = p.izraz()
        p >> T.TOČKAZ
        return Definiranje(tipizirano.ime, tipizirano.tip, izraz)

    def input(p) -> 'Input':
        ime = p >> T.IME
        p >> T.TOČKAZ
        return Unos(ime)

    def definiranje_tipa(p) -> 'Tip':
        ime = p >> T.IME
        parametri_tipa = p.parametri_tipa()
        p >> T.AS
        članovi = p.članovi_tipa()
        p >> T.ENDDATA
        return 

    def funkcija(p) -> 'Funkcija':
        staro_imef = p.imef
        stari_parametrif = p.parametrif
        stari_tipf = p.tipf
        # TODO istražiti: memorija u parseru je loša ideja, može li se ovo preseliti drugdje?
        ime = p >> T.IME
        p.imef = ime
        parametri = p.parametri()
        p.parametrif = parametri
        p >> T.FTYPE
        tip = p.tip()
        p.tipf = tip
        p >> T.AS
        tijelo = p.naredbe(T.ENDDEF, pojedi=True)
        fja = Funkcija(ime, tip, parametri, tijelo)
        p.funkcije[ime] = fja

        p.imef = staro_imef
        p.parametrif = stari_parametrif
        p.tipf = stari_tipf

        return fja

    def vraćanje(p):
        if p >= T.TOČKAZ:
            return Vraćanje(nenavedeno)
        else:
            izraz = p.izraz()
            p >> T.TOČKAZ
            return Vraćanje(izraz)

    def tipizirano(p) -> 'Tipizirano':
        ime = p >> T.IME
        p >> T.OFTYPE
        tip = p.tip()
        return Tipizirano(ime, tip)

    def tip(p) -> 'tip':
        return p >> {T.INT, T.BOOL, T.STRINGT, T.UNIT}

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

    def parametri(p) -> 'tipizirano*':
        p >> T.OTV
        parametri = [p.tipizirano()]
        while p >= T.ZAREZ:
            parametri.append(p.tipizirano())
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
