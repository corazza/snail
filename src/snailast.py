# Apstraktna sintaksna stabla
# Program: naredbe: [naredba]
# naredba:

import os
from vepar import *

from lekser import *

import snailparser

import scopes
import tipovi


class Program(AST):
    naredbe: 'Naredbe'

    def typecheck(self, filename):
        directory = os.path.dirname(os.path.realpath(filename))
        meta = {'directory': directory, 'filename': filename}
        global_scope = scopes.Scope()
        self.naredbe.typecheck(global_scope, None, meta)
        return filter(lambda a: not isinstance(a[1], Data), global_scope.mem)

    def izvrši(self, filename):
        directory = os.path.dirname(os.path.realpath(filename))
        rt.mem = Memorija()
        rt.mem[Token(T.IME, '__file__')] = Token(T.STRING, filename)
        rt.mem[Token(T.IME, '__dir__')] = Token(T.STRING, directory)
        self.naredbe.izvrši(rt.mem, None)


class Naredbe(AST):
    naredbe: 'naredba*'

    def typecheck(self, scope, unutar, meta):
        for naredba in self.naredbe:
            naredba.typecheck(scope, unutar, meta)

    def izvrši(self, mem, unutar):
        for naredba in self.naredbe:
            naredba.izvrši(mem, unutar)


class Import(AST):
    path: 'STRING'

    def typecheck(self, scope, unutar, meta):
        # with open(meta['directory'] + '/' + self.path.sadržaj.strip('"'), 'r') as f:
        #     src = f.read()
        #     program = snailparser.P(src)
        return

    def izvrši(self, mem, unutar):
        return


class Match(AST):
    izraz: 'izraz'
    varijante: 'Varijanta+'

    def izvrši(self, scope, unutar):
        vrijednost = self.izraz.vrijednost(scope, unutar)
        izvršeno = False
        for v in self.varijante:
            if v.ako.does_match(vrijednost, scope, unutar):
                v.izvrši(vrijednost, scope, unutar)
                izvršeno = True
        assert(izvršeno) # pokreiveno u typecheck

    def typecheck(self, scope, unutar, meta):
        tip_izraza = self.izraz.typecheck(scope, unutar, meta)
        dtip = scope[tip_izraza.ime]
        pojave_konstruktora = {x.ime: 0 for x in dtip.konstruktori}
        for v in self.varijante:
            v.ako.konstruktor = tipovi.tip_u_konstruktor(
                tip_izraza, v.ako.konstruktor, scope, unutar)
            if not tipovi.equiv_types(tip_izraza, v.typecheck(scope, unutar, meta), scope, unutar):
                # TODO subclass TypeError
                raise SemantičkaGreška(
                    f'matchana vrijednost se ne podudara s varijantom u tipu')
            pojave_konstruktora[v.ako.konstruktor.ime] += 1
        for pojava, puta in pojave_konstruktora.items():
            if puta == 0:
                raise SemantičkaGreška(f'konstruktor {pojava} se ne pojavljuje u match naredbi')



class Varijanta(AST):
    ako: 'Pattern'
    onda: 'naredba'

    def izvrši(self, vrijednost, scope, unutar):
        # dodaj varijable u scope
        local = scopes.Scope(scope)
        matchano = self.ako.match(vrijednost)
        for (var, vrijednost) in zip(self.ako.varijable, matchano):
            local[var] = vrijednost
        self.onda.izvrši(local, unutar)

    def typecheck(self, scope, unutar, meta):
        """Ova metoda signalizira Matchu tip 'ako' polja u varijanti,
           iako bi bilo logičnije da se što više elemenata shvati kao
           izraz a ne naredba, pa bi onda tip varijante zapravo bio tip
           'onda' polja, a Match.typecheck bi bio zadužen za poklapanje
           svih 'ako' polja sa 'izraz'om Matcha."""
        lokalni = scopes.Scope(scope)
        for (varijabla, parametar) in zip(self.ako.varijable, self.ako.konstruktor.parametri):
            lokalni[varijabla] = parametar
        self.onda.typecheck(lokalni, unutar, meta)
        return self.ako.typecheck(lokalni, unutar, meta)


class Pattern(AST):
    konstruktor: 'Konstruktor'
    varijable: 'ime*'

    def match(self, vrijednost):
        return vrijednost.argumenti

    def does_match(self, vrijednost, mem, unutar):
        return self.konstruktor.ime == vrijednost.konstruktor.ime

    def typecheck(self, scope, unutar, meta):
        return tipovi.konstruktor_u_tip(self.konstruktor, [None] * len(self.konstruktor.parametri), scope, unutar)


class Definiranje(AST):
    ime: 'IME'  # TODO provjeri sve ove deklaracije
    tip: 'T'
    izraz: 'izraz'

    def typecheck(self, scope, unutar, meta):
        tip = self.izraz.typecheck(scope, unutar, meta)
        if not tipovi.equiv_types(tip, self.tip, scope, unutar):
            raise SemantičkaGreška(
                f'{self.ime}:{self.tip} se ne podudara s {tip}')
        scope[self.ime] = tip

    def izvrši(self, mem, unutar):
        if self.ime in mem:
            raise SemantičkaGreška(f'redefiniranje {self.ime}')
        mem[self.ime] = self.izraz.vrijednost(mem, unutar)


class Pridruživanje(AST):
    ime: 'IME'
    izraz: 'izraz'

    def typecheck(self, scope, unutar, meta):
        if self.ime not in scope:
            raise SemantičkaGreška(
                f'korištenje {self.ime} prije definiranja (let {self.ime}: TIP = IZRAZ;)')

        moj_tip = scope[self.ime]
        pridruživanje_tip = self.izraz.typecheck(scope, unutar, meta)

        if not tipovi.equiv_types(moj_tip, pridruživanje_tip, scope, unutar):
            raise SemantičkaGreška(
                f'{self.ime} je tipa {moj_tip} a izraz {pridruživanje_tip}')

    def izvrši(self, mem, unutar):  # TODO provjera tipa
        if self.ime not in mem:
            raise SemantičkaGreška(
                f'korištenje {self.ime} prije definiranja (let {self.ime}: TIP = IZRAZ;)')
        mem[self.ime] = self.izraz.vrijednost(mem, unutar)


class Data(AST):
    ime: 'IME'
    parametri: 'IME*'
    konstruktori: 'konstruktor*'

    def typecheck(self, scope, unutar, meta):
        scope[self.ime] = self
        lokalni = scopes.Scope(scope)
        for p in self.parametri:
            lokalni[p] = p
        for konstruktor in self.konstruktori:
            tip = konstruktor.typecheck(lokalni, unutar, meta)
            scope[konstruktor.ime] = tip

    def izvrši(self, mem, unutar):
        """<Data> definicije se ne izvršavaju"""


class SloženaVrijednost(AST):
    # Ovo je AST samo da bi se naslijedio lijepi print
    konstruktor: 'Konstruktor'
    argumenti: 'izraz'

    def __str__(self):
        ime = self.konstruktor.ime
        argumenti = ", ".join(map(printanje_str, self.argumenti))
        return f"{ime}({argumenti})" if len(argumenti) > 0 else f"{ime}"

    def vrijednost(self):
        return self
    
    def vrijednosti(self):
        return self.argumenti

    def __eq__(self, other):
        if not isinstance(other, SloženaVrijednost):
            return False
        if self.konstruktor != other.konstruktor:
            return False
        # složena vrijednost uvijek nastaje kao poziv, argumenti su izvrijednjeni
        # ovo će rekurzivno pozvati arg.__eq__ na svim argumentima, pa prolazi za nestane složene vrijednosti
        return self.argumenti == other.argumenti

class Konstruktor(AST):
    od: 'VELIKOIME'
    ime: 'VELIKOIME'
    parametri: 'tip*'

    def typecheck(self, scope, unutar, meta):
        parametri = [p.typecheck(scope, unutar, meta) for p in self.parametri]
        složeni_tip = tipovi.konstruktor_u_tip(
            self, self.parametri, scope, unutar)
        return tipovi.TipKonstruktora(složeni_tip, parametri)

    def pozovi(konstruktor, mem, unutar, argumenti):
        return SloženaVrijednost(konstruktor, argumenti)


class Funkcija(AST):
    ime: 'IME'
    tip: 'tip'
    parametri: 'Tipizirano*'
    tijelo: 'naredba*'
    # TODO
    memo_flag: ''
    memoizirano = {}

    def typecheck(funkcija, scope, unutar, meta):
        lokalni = scopes.Scope(scope)
        for p in funkcija.parametri:
            lokalni[p.ime] = p.tip
        funkcija.tijelo.typecheck(lokalni, funkcija, meta)
        parametri = [tipizirano.tip for tipizirano in funkcija.parametri]
        tip = tipovi.TipFunkcije(funkcija.tip, parametri)
        scope[funkcija.ime] = tip
        return tip
    
    def pozovi(funkcija, mem, unutar, argumenti):
        if(funkcija.memo_flag):
            try:
                return funkcija.memoizirano[str(argumenti)]
            except KeyError:
                lokalni = Memorija(zip([p.ime for p in funkcija.parametri], argumenti))
                try:
                    funkcija.tijelo.izvrši(mem=lokalni, unutar=funkcija)
                except Povratak as exc:
                    funkcija.memoizirano[str(argumenti)] = exc.preneseno
                    return exc.preneseno
                else:
                    raise GreškaIzvođenja(f'{funkcija.ime} nije ništa vratila')
        else:
            lokalni = Memorija(zip([p.ime for p in funkcija.parametri], argumenti))
            try:
                funkcija.tijelo.izvrši(mem=lokalni, unutar=funkcija)
            except Povratak as exc:
                return exc.preneseno
            else:
                raise GreškaIzvođenja(f'{funkcija.ime} nije ništa vratila')

    def izvrši(self, mem, unutar):
        """<Funkcija> definicije se ne izvršavaju"""


class Poziv(AST):
    funkcija: 'Funkcija?'
    argumenti: 'izraz*'

    def typecheck(poziv, scope, unutar, meta):
        pozvana = poziv.funkcija
        if pozvana is nenavedeno:
            pozvana = unutar  # rekurzivni poziv
        argumenti = [a.typecheck(scope, unutar, meta) for a in poziv.argumenti]

        if isinstance(pozvana, Funkcija):
            # for (p, a) in zip(parametri, argumenti):
            #     if not tipovi.equiv_types(p, a, scope, unutar):
            #         raise SemantičkaGreška(
            #             f'očekivan tip {p}, a dan {a}')
            # IPython.embed()
            return tipovi.funkcija_u_tip(pozvana, argumenti, scope, unutar)
        else:  # TODO ujedini funkcije i konstruktore
            assert(isinstance(pozvana, Konstruktor))
            assert(len(argumenti) == len(pozvana.parametri))
            return tipovi.konstruktor_u_tip(pozvana, argumenti, scope, unutar)

    def vrijednost(poziv, mem, unutar):
        pozvana = poziv.funkcija
        if pozvana is nenavedeno:
            pozvana = unutar  # rekurzivni poziv
        argumenti = [a.vrijednost(mem, unutar) for a in poziv.argumenti]
        return pozvana.pozovi(mem, unutar, argumenti)

    def izvrši(poziv, mem, unutar):
        return poziv.vrijednost(mem, unutar)

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

    def typecheck(self, scope, unutar, meta):
        if self.izraz ^ T.UNIT:
            tip_izraza = Token(T.UNITT)
        else:
            tip_izraza = self.izraz.typecheck(scope, unutar, meta)
        if not tipovi.equiv_types(tip_izraza, unutar.tip, scope, unutar):
            raise SemantičkaGreška(
                f'funkcija {unutar.ime.sadržaj} treba vratiti {unutar.tip.sadržaj} (dano: {tip_izraza.sadržaj})')
        return tip_izraza

    def izvrši(self, mem, unutar):
        if self.izraz is nenavedeno:
            raise Povratak()
        else:
            vrijednost = self.izraz.vrijednost(mem, unutar)
            raise Povratak(vrijednost)


class Printanje(AST):
    sadržaj: 'izraz|STRING#|NEWLINE'

    def typecheck(self, scope, unutar, meta):
        return

    def izvrši(self, mem, unutar):
        if self.sadržaj ^ T.NEWLINE:
            print()
        else:
            print(token_str(self.sadržaj.vrijednost(mem, unutar)), end='')


class Unos(AST):
    ime: 'IME'

    def typecheck(self, scope, unutar, meta):
        if not tipovi.equiv_types(scope[self.ime], Token(T.INT), scope, unutar):
            raise SemantičkaGreška(f'unos mora biti u varijablu tipa {T.INT}')
        scope[self.ime] = Token(T.INT)

    def izvrši(self, mem, unutar):
        mem[self.ime] = int(input())


class Grananje(AST):
    provjera: 'izraz'
    ako: 'naredba+'
    inače: '(naredba+)?'

    def typecheck(self, scope, unutar, meta):
        tip = self.provjera.typecheck(scope, unutar, meta)
        if not tipovi.equiv_types(tip, Token(T.BOOL), scope, unutar):
            raise SemantičkaGreška(f'provjera mora biti tipa {T.BOOL}')
        self.ako.typecheck(scope, unutar, meta)
        if self.inače != nenavedeno:
            self.inače.typecheck(scope, unutar, meta)

    def izvrši(self, mem, unutar):
        vrijednost = self.provjera.vrijednost(mem, unutar)
        if vrijednost:
            return self.ako.izvrši(mem, unutar)
        elif self.inače:
            return self.inače.izvrši(mem, unutar)


class Negacija(AST):
    ispod: 'izraz'

    def typecheck(self, scope, unutar, meta):
        tip = self.ispod.typecheck(scope, unutar, meta)
        if not tipovi.equiv_types(tip, Token(T.BOOL), scope, unutar):
            raise SemantičkaGreška(f'varijabla mora biti tipa {T.BOOL}')

    def vrijednost(negacija): 
        return not negacija.ispod.vrijednost()

    def optim(negacija):
        ispod_opt = negacija.ispod.optim()
        if ispod_opt ^ Negacija: 
            return ispod_opt.ispod 
        else: 
            return Negacija(ispod_opt)


class Infix(AST):
    operator: 'PLUS|MINUS|...'
    lijevi: 'faktor|član|Infix'  # TODO provjeri ima li ova deklaracija smisla
    desni: 'faktor|član|Infix'

    def typecheck(self, scope, unutar, meta):
        op = self.operator
        if self.lijevi == nenavedeno:
            lijevi_tip = Token(T.INT)
        else:
            lijevi_tip = self.lijevi.typecheck(scope, unutar, meta)
        desni_tip = self.desni.typecheck(scope, unutar, meta)

        if op ^ {T.PLUS, T.MINUS, T.PUTA, T.DIV, T.MANJE, T.JMANJE, T.VECE, T.JVECE}:
            if not (tipovi.equiv_types(lijevi_tip, Token(T.INT), scope, unutar) and tipovi.equiv_types(desni_tip, Token(T.INT), scope, unutar)):
                raise SemantičkaGreška(
                    f'oba operanda moraju biti tipa {T.INT}')
        elif op ^ {T.JEDNAKO, T.NEJEDNAKO}:
            if not tipovi.equiv_types(lijevi_tip, desni_tip, scope, unutar):
                raise SemantičkaGreška(
                    f'oba operanda moraju biti istog tipa {lijevi_tip}')
        elif op ^ {T.LOGI, T.LOGILI}:
            if not (tipovi.equiv_types(lijevi_tip, Token(T.BOOL), scope, unutar) and tipovi.equiv_types(desni_tip, Token(T.BOOL), scope, unutar)):
                raise SemantičkaGreška(
                    f'oba operanda moraju biti tipa {T.BOOL}')
        else:
            raise SemantičkaGreška(f'nepoznat operator {op}')

        if op ^ {T.PLUS, T.MINUS, T.PUTA, T.DIV}:
            return Token(T.INT)
        else:
            return Token(T.BOOL)

    def vrijednost(self, mem, unutar):
        op = self.operator
        if self.lijevi == nenavedeno:
            lijevi = 0
        else:
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
        elif op ^ T.ILI:
            return lijevi or desni
        elif op ^ T.I:
            return lijevi and desni
        elif op ^ T.NEGACIJA:
            return not desni
        else:
            raise SemantičkaGreška(f'nepoznat operator {op}')


class Tipizirano(AST):
    ime: 'IME'
    tip: 'tip'
