# Apstraktna sintaksna stabla
# Program: naredbe: [naredba]
# naredba:

from vepar import *

from lekser import *


class Program(AST):
    naredbe: 'naredbe'

    def izvrši(self):
        rt.mem = Memorija()
        self.naredbe.izvrši(rt.mem, nenavedeno)


class Naredbe(AST):
    naredbe: 'naredba*'

    def izvrši(self, mem, unutar):
        for naredba in self.naredbe:
            naredba.izvrši(mem, unutar)


class Pridruživanje(AST):
    ime: 'IME'
    izraz: 'izraz'

    def izvrši(self, mem, unutar):
        mem[self.ime] = self.izraz.vrijednost(mem, unutar)


class Printanje(AST):
    sadržaj: 'izraz|STRING#|NEWLINE'

    def izvrši(self, mem, unutar):
        if self.sadržaj ^ T.NEWLINE:
            print()
        else:
            print(self.sadržaj.vrijednost(mem, unutar), end='')


class Grananje(AST):
    provjera: 'izraz'
    ako: 'naredba+'
    inače: '(naredba+)?'

    def izvrši(self, mem, unutar):
        if self.provjera.vrijednost(mem, unutar) != 0:
            return self.ako.izvrši(mem, unutar)
        elif self.inače:
            return self.inače.izvrši(mem, unutar)


class Infix(AST):
    operator: 'PLUS|MINUS|...'
    lijevi: 'faktor|član|Infix'  # TODO provjeri ima li ova deklaracija smisla
    desni: 'faktor|član|Infix'

    def vrijednost(self, mem, unutar):
        op = self.operator
        lijevi = self.lijevi.vrijednost(mem, unutar)
        desni = self.desni.vrijednost(mem, unutar)
        if op ^ T.PLUS:
            return lijevi + desni
        elif op ^ T.MINUS:
            return lijevi - desni
        elif op ^ T.PUTA:
            return lijevi * desni
        elif op ^ T.DIV:
            if desni == 0:
                raise SemantičkaGreška('dijeljenje s 0')
            return lijevi / desni
        elif op ^ T.MANJE:
            return 1 if lijevi < desni else 0
        elif op ^ T.JMANJE:
            return 1 if lijevi <= desni else 0
        elif op ^ T.VECE:
            return 1 if lijevi > desni else 0
        elif op ^ T.JVECE:
            return 1 if lijevi >= desni else 0
        elif op ^ T.JEDNAKO:
            return 1 if lijevi == desni else 0
        elif op ^ T.NEJEDNAKO:
            return 1 if lijevi != desni else 0
        else:
            raise SemantičkaGreška(f'nepoznat operator {op}')


class Funkcija(AST):
    ime: 'IME'
    parametri: 'IME*'
    tijelo: 'naredba*'

    def pozovi(funkcija, argumenti):
        lokalni = Memorija(zip(funkcija.parametri, argumenti))
        try:
            funkcija.tijelo.izvrši(mem=lokalni, unutar=funkcija)
        except Povratak as exc:
            return exc.preneseno
        else:
            raise GreškaIzvođenja(f'{funkcija.ime} nije ništa vratila')

    def izvrši(self, mem, unutar):
        """Definicije se ne izvršavaju u runtimeu."""


class Vraćanje(AST):
    izraz: 'izraz?'

    def izvrši(self, mem, unutar):
        raise Povratak(self.izraz.vrijednost(mem, unutar))


class Povratak(NelokalnaKontrolaToka):
    pass


class Poziv(AST):
    funkcija: 'Funkcija?'
    argumenti: 'izraz*'

    def vrijednost(poziv, mem, unutar):
        pozvana = poziv.funkcija
        if pozvana is nenavedeno:
            pozvana = unutar  # rekurzivni poziv
        argumenti = [a.vrijednost(mem, unutar) for a in poziv.argumenti]
        return pozvana.pozovi(argumenti)

    def izvrši(poziv, mem, unutar):
        poziv.vrijednost(mem, unutar)

    def za_prikaz(poziv):  # samo za ispis, da se ne ispiše čitava funkcija
        r = {'argumenti': poziv.argumenti}
        if poziv.funkcija is nenavedeno:
            r['*rekurzivni'] = True
        else:
            r['*ime'] = poziv.funkcija.ime
        return r
