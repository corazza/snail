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


class Definiranje(AST):
    ime: 'IME'  # TODO provjeri sve ove deklaracije
    tip: 'T'
    izraz: 'izraz'

    def izvrši(self, mem, unutar):
        (vrijednost, tip) = self.izraz.vrijednost(mem, unutar)
        if tip is not self.tip:
            raise SemantičkaGreška('tipovi se ne podudaraju')
        mem[self.ime] = (vrijednost, tip)


class Pridruživanje(AST):
    ime: 'IME'
    izraz: 'izraz'

    def izvrši(self, mem, unutar):  # TODO provjera tipa
        if self not in mem:
            raise SemantičkaGreška(
                f'korištenje {self.ime} prije definiranja (let {self.ime}: TIP = IZRAZ;)')

        (vrijednost, tip) = mem[self.ime]
        (vrijednost2, tip2) = self.izraz.vrijednost(mem, unutar)

        if tip is not tip2:
            raise SemantičkaGreška(f'{self.ime} je tipa {tip} a izraz {tip2}')

        mem[self.ime] = (vrijednost2, tip2)


class Printanje(AST):
    sadržaj: 'izraz|STRING#|NEWLINE'

    def izvrši(self, mem, unutar):
        if self.sadržaj ^ T.NEWLINE:
            print()
        else:
            print(self.sadržaj.vrijednost(mem, unutar)[0], end='')


class Unos(AST):
    ime: 'IME'

    def izvrši(self, mem, unutar):
        mem[self.ime] = (int(input()), Token(T.INT))


class Grananje(AST):
    provjera: 'izraz'
    ako: 'naredba+'
    inače: '(naredba+)?'

    def izvrši(self, mem, unutar):
        (vrijednost, tip) = self.provjera.vrijednost(mem, unutar)

        if not tip ^ T.BOOL:
            raise SemantičkaGreška(f'provjera mora biti tipa {T.BOOL}')

        if vrijednost:
            return self.ako.izvrši(mem, unutar)
        elif self.inače:
            return self.inače.izvrši(mem, unutar)


class Infix(AST):
    operator: 'PLUS|MINUS|...'
    lijevi: 'faktor|član|Infix'  # TODO provjeri ima li ova deklaracija smisla
    desni: 'faktor|član|Infix'

    def vrijednost(self, mem, unutar):
        op = self.operator
        (lijevi, lijevi_tip) = self.lijevi.vrijednost(mem, unutar)
        (desni, desni_tip) = self.desni.vrijednost(mem, unutar)

        if op ^ T.PLUS:
            if not (lijevi_tip ^ T.INT and desni_tip ^ T.INT):
                raise SemantičkaGreška(
                    f'oba operanda moraju biti tipa {T.INT}')
            return (lijevi + desni, lijevi_tip)
        elif op ^ T.MINUS:
            if not (lijevi_tip ^ T.INT and desni_tip ^ T.INT):
                raise SemantičkaGreška(
                    f'oba operanda moraju biti tipa {T.INT}')
            return (lijevi - desni, lijevi_tip)
        elif op ^ T.PUTA:
            if not (lijevi_tip ^ T.INT and desni_tip ^ T.INT):
                raise SemantičkaGreška(
                    f'oba operanda moraju biti tipa {T.INT}')
            return (lijevi * desni, lijevi_tip)
        elif op ^ T.DIV:
            if not (lijevi_tip ^ T.INT and desni_tip ^ T.INT):
                raise SemantičkaGreška(
                    f'oba operanda moraju biti tipa {T.INT}')
            if desni == 0:
                raise SemantičkaGreška('dijeljenje s 0')
            return (lijevi / desni, lijevi_tip)
        elif op ^ T.MANJE:
            if not (lijevi_tip ^ T.INT and desni_tip ^ T.INT):
                raise SemantičkaGreška(
                    f'oba operanda moraju biti tipa {T.INT}')
            return (1 if lijevi < desni else 0, Token(T.BOOL))
        elif op ^ T.JMANJE:
            if not (lijevi_tip ^ T.INT and desni_tip ^ T.INT):
                raise SemantičkaGreška(
                    f'oba operanda moraju biti tipa {T.INT}')
            return (1 if lijevi <= desni else 0, Token(T.BOOL))
        elif op ^ T.VECE:
            if not (lijevi_tip ^ T.INT and desni_tip ^ T.INT):
                raise SemantičkaGreška(
                    f'oba operanda moraju biti tipa {T.INT}')
            return (1 if lijevi > desni else 0, Token(T.BOOL))
        elif op ^ T.JVECE:
            if not (lijevi_tip ^ T.INT and desni_tip ^ T.INT):
                raise SemantičkaGreška(
                    f'oba operanda moraju biti tipa {T.INT}')
            return (1 if lijevi >= desni else 0, Token(T.BOOL))
        elif op ^ T.JEDNAKO:
            if lijevi_tip != desni_tip:
                raise SemantičkaGreška(
                    f'oba operanda moraju biti istog tipa {lijevi_tip}')
            return (1 if lijevi == desni else 0, Token(T.BOOL))
        elif op ^ T.NEJEDNAKO:
            if lijevi_tip != desni_tip:
                raise SemantičkaGreška(
                    f'oba operanda moraju biti istog tipa {lijevi_tip}')
            return (1 if lijevi != desni else 0, Token(T.BOOL))
        else:
            raise SemantičkaGreška(f'nepoznat operator {op}')


class Funkcija(AST):
    ime: 'IME'
    parametri: 'IME*'
    tijelo: 'naredba*'

    def pozovi(funkcija, mem, unutar, argumenti):
        lokalni = Memorija(zip([p.ime for p in funkcija.parametri], argumenti))
        try:
            funkcija.tijelo.izvrši(mem=lokalni, unutar=funkcija)
        except Povratak as exc:
            return exc.preneseno
        else:
            raise GreškaIzvođenja(f'{funkcija.ime} nije ništa vratila')

    def izvrši(self, mem, unutar):
        """Definicije se ne izvršavaju u runtimeu."""


class Poziv(AST):
    funkcija: 'Funkcija?'
    argumenti: 'izraz*'

    def vrijednost(poziv, mem, unutar):
        pozvana = poziv.funkcija
        if pozvana is nenavedeno:
            pozvana = unutar  # rekurzivni poziv
        argumenti = [a.vrijednost(mem, unutar) for a in poziv.argumenti]
        for (p, a) in zip(pozvana.parametri, argumenti):
            if p.tip != a[1]:
                raise SemantičkaGreška(f'očekivan tip {p.tip}, a dan {a[1]}')
        return pozvana.pozovi(mem, unutar, argumenti)

    def izvrši(poziv, mem, unutar):
        poziv.vrijednost(mem, unutar)

    def za_prikaz(poziv):  # samo za ispis, da se ne ispiše čitava funkcija
        r = {'argumenti': poziv.argumenti}
        if poziv.funkcija is nenavedeno:
            r['*rekurzivni'] = True
        else:
            r['*ime'] = poziv.funkcija.ime
        return r


class Vraćanje(AST):
    izraz: 'izraz?'
    tip: 'T'

    def izvrši(self, mem, unutar):
        if self.izraz is nenavedeno:
            raise Povratak()
        else:
            (vrijednost, tip) = self.izraz.vrijednost(mem, unutar)
            if self.tip != tip:
                raise SemantičkaGreška(
                    f'povratni tip bi trebao biti {self.tip}, dan je {tip}')
            raise Povratak((vrijednost, tip))


class Tipizirano(AST):
    ime: 'IME'
    tip: 'tip'


class Povratak(NelokalnaKontrolaToka):
    pass
