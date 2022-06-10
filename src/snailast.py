# Apstraktna sintaksna stabla
# Program: naredbe: [naredba]
# naredba:

from vepar import *


class Program(AST):
    naredbe: 'naredba*'

    def izvrši(program):
        rt.mem = Memorija()
        for naredba in program.naredbe:
            naredba.izvrši()


class Pridruživanje(AST):
    ime: 'IME'
    izraz: 'izraz'


class Printanje(AST):
    sadržaj: 'izraz|STRING#|NEWLINE'


class Grananje(AST):
    provjera: 'izraz'
    ako: 'naredba+'
    inače: '(naredba+)?'


class Infix(AST):
    operator: 'PLUS|MINUS|...'
    lijevi: 'faktor'
    desni: 'faktor'


class Vraćanje(AST):
    izraz: 'izraz?'

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


class Poziv(AST):
    funkcija: 'Funkcija?'
    argumenti: 'izraz*'

    def vrijednost(poziv, mem, unutar):
        pozvana = poziv.funkcija
        if pozvana is nenavedeno:
            pozvana = unutar  # rekurzivni poziv
        argumenti = [a.vrijednost(mem, unutar) for a in poziv.argumenti]
        return pozvana.pozovi(argumenti)

    def za_prikaz(poziv):  # samo za ispis, da se ne ispiše čitava funkcija
        r = {'argumenti': poziv.argumenti}
        if poziv.funkcija is nenavedeno:
            r['*rekurzivni'] = True
        else:
            r['*ime'] = poziv.funkcija.ime
        return r
