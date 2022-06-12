# Apstraktna sintaksna stabla
# Program: naredbe: [naredba]
# naredba:

from vepar import *

from lekser import *
from scope import *
from tipovi import *


class Program(AST):
    naredbe: 'naredbe'

    def typecheck(self):
        global_scope = Scope()
        self.naredbe.typecheck(global_scope, None)

    def izvrši(self):
        rt.mem = Memorija()
        self.naredbe.izvrši(rt.mem, None)


class Naredbe(AST):
    naredbe: 'naredba*'

    def typecheck(self, scope, unutar):
        for naredba in self.naredbe:
            naredba.typecheck(scope, unutar)

    def izvrši(self, mem, unutar):
        for naredba in self.naredbe:
            naredba.izvrši(mem, unutar)


class Match(AST):
    izraz: 'izraz'
    varijante: 'Varijanta+'

    def typecheck(self, scope, unutar):
        tip_izraza = self.izraz.typecheck(scope, unutar)
        for v in self.varijante:
            v.ako.konstruktor = tip_u_konstruktor(
                tip_izraza, v.ako.konstruktor, scope, unutar)
            if not equiv_types(tip_izraza, v.typecheck(scope, unutar), scope, unutar):
                # TODO subclass TypeError
                raise SemantičkaGreška(
                    f'matchana vrijednost se ne podudara s varijantom u tipu')


class Varijanta(AST):
    ako: 'Pattern'
    onda: 'naredba'

    def typecheck(self, scope, unutar):
        """Ova metoda signalizira Matchu tip 'ako' polja u varijanti,
           iako bi bilo logičnije da se što više elemenata shvati kao
           izraz a ne naredba, pa bi onda tip varijante zapravo bio tip
           'onda' polja, a Match.typecheck bi bio zadužen za poklapanje
           svih 'ako' polja sa 'izraz'om Matcha."""
        # import IPython
        # IPython.embed()
        lokalni = Scope(scope)
        for (varijabla, parametar) in zip(self.ako.varijable, self.ako.konstruktor.parametri):
            lokalni[varijabla] = self.mapiranje_varijabli[parametar]
        self.onda.typecheck(scope, unutar)
        return self.ako.typecheck(scope, unutar)


class Pattern(AST):
    konstruktor: 'Konstruktor'
    varijable: 'ime*'

    def typecheck(self, scope, unutar):
        return konstruktor_u_tip(self.konstruktor, [None] * len(self.konstruktor.parametri), scope, unutar)


class Definiranje(AST):
    ime: 'IME'  # TODO provjeri sve ove deklaracije
    tip: 'T'
    izraz: 'izraz'

    def typecheck(self, scope, unutar):
        tip = self.izraz.typecheck(scope, unutar)
        if not equiv_types(tip, self.tip, scope, unutar):
            raise SemantičkaGreška('tipovi se ne podudaraju')
        scope[self.ime] = tip

    def izvrši(self, mem, unutar):
        vrijednost = self.izraz.vrijednost(mem, unutar)
        mem[self.ime] = vrijednost


class Pridruživanje(AST):
    ime: 'IME'
    izraz: 'izraz'

    def typecheck(self, scope, unutar):
        if self.ime not in scope:
            raise SemantičkaGreška(
                f'korištenje {self.ime} prije definiranja (let {self.ime}: TIP = IZRAZ;)')

        moj_tip = scope[self.ime]
        pridruživanje_tip = self.izraz.typecheck(scope, unutar)

        if not equiv_types(moj_tip, pridruživanje_tip, scope, unutar):
            raise SemantičkaGreška(
                f'{self.ime} je tipa {moj_tip} a izraz {pridruživanje_tip}')

    def izvrši(self, mem, unutar):  # TODO provjera tipa
        if self.ime not in mem:
            raise SemantičkaGreška(
                f'korištenje {self.ime} prije definiranja (let {self.ime}: TIP = IZRAZ;)')
        mem[self.ime] = self.izraz.izvrši(mem, unutar)


class Printanje(AST):
    sadržaj: 'izraz|STRING#|NEWLINE'

    def typecheck(self, scope, unutar):
        return

    def izvrši(self, mem, unutar):
        if self.sadržaj ^ T.NEWLINE:
            print()
        else:
            print(self.sadržaj.vrijednost(mem, unutar), end='')


class Unos(AST):
    ime: 'IME'

    def typecheck(self, scope, unutar):
        if not equiv_types(scope[self.ime], Token(T.INT)):
            raise SemantičkaGreška(f'unos mora biti u varijablu tipa {T.INT}')
        scope[self.ime] = Token(T.INT)

    def izvrši(self, mem, unutar):
        mem[self.ime] = int(input())


class Grananje(AST):
    provjera: 'izraz'
    ako: 'naredba+'
    inače: '(naredba+)?'

    def typecheck(self, scope, unutar):
        tip = self.provjera.typecheck(scope, unutar)
        if not equiv_types(tip, Token(T.BOOL)):
            raise SemantičkaGreška(f'provjera mora biti tipa {T.BOOL}')
        self.ako.typecheck(scope, unutar)
        self.inače.typecheck(scope, unutar)

    def izvrši(self, mem, unutar):
        vrijednost = self.provjera.vrijednost(mem, unutar)

        if vrijednost:
            return self.ako.izvrši(mem, unutar)
        elif self.inače:
            return self.inače.izvrši(mem, unutar)


class Data(AST):
    ime: 'IME'
    parametri: 'IME*'
    konstruktori: 'konstruktor*'

    def typecheck(self, scope, unutar):
        scope[self.ime] = self
        lokalni = Scope(scope)
        for p in self.parametri:
            lokalni[p] = p
        for konstruktor in self.konstruktori:
            konstruktor.typecheck(lokalni, unutar)


class Konstruktor(AST):
    od: 'VELIKOIME'
    ime: 'VELIKOIME'
    parametri: 'tip*'

    def typecheck(self, scope, unutar):
        for p in self.parametri:
            p.typecheck(scope, unutar)
        # scope[self.ime]


class Infix(AST):
    operator: 'PLUS|MINUS|...'
    lijevi: 'faktor|član|Infix'  # TODO provjeri ima li ova deklaracija smisla
    desni: 'faktor|član|Infix'

    def typecheck(self, scope, unutar):
        op = self.operator
        lijevi_tip = self.lijevi.typecheck(scope, unutar)
        desni_tip = self.desni.typecheck(scope, unutar)

        if op ^ {T.PLUS, T.MINUS, T.PUTA, T.DIV, T.MANJE, T.JMANJE, T.VECE, T.JVECE}:
            if not (equiv_types(lijevi_tip, Token(T.INT)) and equiv_types(desni_tip, Token(T.INT))):
                raise SemantičkaGreška(
                    f'oba operanda moraju biti tipa {T.INT}')
        elif op ^ {T.JEDNAKO, T.NEJEDNAKO}:
            if not equiv_types(lijevi_tip, desni_tip):
                raise SemantičkaGreška(
                    f'oba operanda moraju biti istog tipa {lijevi_tip}')
        else:
            raise SemantičkaGreška(f'nepoznat operator {op}')

        return Token(T.BOOL)

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
    tip: 'tip'
    vartipa: 'VELIKOIME*'
    parametri: 'Tipizirano*'
    tijelo: 'naredba*'

    def typecheck(funkcija, scope, unutar):
        lokalni = Scope(scope)
        for p in funkcija.parametri:
            lokalni[p.ime] = p.tip
        funkcija.tijelo.typecheck(lokalni, funkcija)

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

    def typecheck(poziv, scope, unutar):
        pozvana = poziv.funkcija
        if pozvana is nenavedeno:
            pozvana = unutar  # rekurzivni poziv
        argumenti = [a.typecheck(scope, unutar) for a in poziv.argumenti]

        if isinstance(pozvana, Funkcija):
            for (p, a) in zip(pozvana.parametri, argumenti):
                if not equiv_types(p.tip, a, scope, unutar):
                    raise SemantičkaGreška(
                        f'očekivan tip {p.tip}, a dan {a[1]}')
            return pozvana.tip
        else:  # TODO ujedini funkcije i konstruktore
            assert(isinstance(pozvana, Konstruktor))
            assert(len(argumenti) == len(pozvana.parametri))
            # exit("OVDJE TIPIZIRAJ")
            # for (p, a) in zip(pozvana.parametri, argumenti):
            #     if not equiv_types(p, a, scope, unutar):
            #         import IPython
            #         IPython.embed()

            #         raise SemantičkaGreška(
            #             f'očekivan tip {p.tip}, a dan {a}')
            return konstruktor_u_tip(pozvana, argumenti, scope, unutar)

    def vrijednost(poziv, mem, unutar):
        pozvana = poziv.funkcija
        if pozvana is nenavedeno:
            pozvana = unutar  # rekurzivni poziv
        argumenti = [a.vrijednost(mem, unutar) for a in poziv.argumenti]
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


# TODO provjeri: rekurzivni pozivi ne preko unutar/nedefinirano

class Vraćanje(AST):
    izraz: 'izraz?'

    def typecheck(self, scope, unutar):
        return self.izraz.typecheck(scope, unutar)

    def izvrši(self, mem, unutar):
        if self.izraz is nenavedeno:
            raise Povratak()
        else:
            vrijednost = self.izraz.vrijednost(mem, unutar)
            raise Povratak(vrijednost)


class Tipizirano(AST):
    ime: 'IME'
    tip: 'tip'


class Povratak(NelokalnaKontrolaToka):
    pass


class UnitValue(AST):
    def typecheck(self, scope, unutar):
        return Token(T.UNITT)

    def vrijednost(self, mem, unutar):
        return self
