# Apstraktna sintaksna stabla
# Program: naredbe: [naredba]
# naredba:

from vepar import *

from lekser import *
from scope import *

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


class Definiranje(AST):
    ime: 'IME'  # TODO provjeri sve ove deklaracije
    tip: 'T'
    izraz: 'izraz'

    def typecheck(self, scope, unutar):
        tip = self.izraz.typecheck(scope, unutar)
        if tip != self.tip:
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

        if moj_tip != pridruživanje_tip:
            raise SemantičkaGreška(f'{self.ime} je tipa {moj_tip} a izraz {pridruživanje_tip}')

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
        if scope[self.ime] != Token(T.INT):
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
        if not tip ^ T.BOOL:
            raise SemantičkaGreška(f'provjera mora biti tipa {T.BOOL}')
        self.ako.typecheck(scope, unutar)
        self.inače.typecheck(scope, unutar)

    def izvrši(self, mem, unutar):
        vrijednost = self.provjera.vrijednost(mem, unutar)

        if vrijednost:
            return self.ako.izvrši(mem, unutar)
        elif self.inače:
            return self.inače.izvrši(mem, unutar)


class Infix(AST):
    operator: 'PLUS|MINUS|...'
    lijevi: 'faktor|član|Infix'  # TODO provjeri ima li ova deklaracija smisla
    desni: 'faktor|član|Infix'


    def typecheck(self, scope, unutar):
        op = self.operator
        lijevi_tip = self.lijevi.typecheck(scope, unutar)
        desni_tip = self.desni.typecheck(scope, unutar)

        if op ^ {T.PLUS, T.MINUS, T.PUTA, T.DIV, T.MANJE, T.JMANJE, T.VECE, T.JVECE}:
            if not (lijevi_tip ^ T.INT and desni_tip ^ T.INT):
                raise SemantičkaGreška(
                    f'oba operanda moraju biti tipa {T.INT}')            
        elif op ^ {T.JEDNAKO, T.NEJEDNAKO}:
            if lijevi_tip != desni_tip:
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

class Tip(AST):
    ime: 'IME'
    parametri: 'IME*'
    varijante: 'varijanta*'

class Varijanta(AST):
    ime: 'IME'

class Funkcija(AST):
    ime: 'IME'
    tip: 'tip'
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
        for (p, a) in zip(pozvana.parametri, argumenti):
            if p.tip != a:
                raise SemantičkaGreška(f'očekivan tip {p.tip}, a dan {a[1]}')
        return pozvana.tip

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


class Vraćanje(AST):
    izraz: 'izraz?'

    def typecheck(self, scope, unutar):
        tip = self.izraz.typecheck(scope, unutar)
        if self.tip != tip:
            raise SemantičkaGreška(
                f'povratni tip bi trebao biti {self.tip}, dan je {tip}')


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
