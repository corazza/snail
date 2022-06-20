from lekser import *
from vepar import *

import IPython  # TODO remove

import scopes
import snailast


elementarni = {T.INT, T.BOOL, T.STRINGT, T.UNITT}


class TipFunkcije(AST):
    tip: 'tip'  # return type
    parametri: 'tip*'

    def __str__(self):
        parametri = ", ".join(map(token_str, self.parametri))
        tip = token_str(self.tip)
        return f"({parametri}) -> {tip}"

# TODO unificiraj sa funkcijama


class TipKonstruktora(AST):
    tip: 'tip'  # return type
    parametri: 'tip*'

    def __str__(self):
        parametri = ", ".join(map(token_str, self.parametri))
        tip = token_str(self.tip)
        return f"({parametri}) -> {tip}" if len(parametri) > 0 else f"{tip}"


class SloženiTip(AST):
    """Ovo je pojednostavljeni Data(AST)."""
    ime: 'VELIKOIME'
    argumenti: 'tip*'

    def typecheck(self, scope, unutar, meta):
        for p in self.argumenti:
            p.typecheck(scope, unutar, meta)
        return self

    def __str__(self):
        ime = self.ime.sadržaj
        argumenti = ", ".join(map(token_str, self.argumenti))
        return f"{ime}<{argumenti}>"


def apply_vartipa_mapping(mapiranje, tip):
    if isinstance(tip, Token):
        if tip ^ T.VARTIPA:
            return mapiranje[tip] if tip in mapiranje else None
        else:
            return tip
    elif isinstance(tip, SloženiTip):
        argumenti = [apply_vartipa_mapping(
            mapiranje, a) for a in tip.argumenti]
        return SloženiTip(tip.ime, argumenti)
    elif tip ^ elementarni:
        return tip
    else:
        raise RuntimeError(f'neprepoznat tip {tip} za mapiranje ({mapiranje})')


def izračunaj_vartipa_mapiranje(parametar, argument):
    if isinstance(parametar, Token) and parametar ^ T.VARTIPA:
        if isinstance(argument, SloženiTip) or (isinstance(argument, Token) and (argument ^ T.VARTIPA or argument ^ elementarni)) or argument == None:
            return {parametar: argument}
    elif isinstance(parametar, Token) and parametar ^ elementarni and (isinstance(argument, Token) and argument ^ elementarni or argument == None):
        return {}  # TODO FIX URGENT kad se dolazi ovdje?
    elif isinstance(parametar, SloženiTip):
        if isinstance(argument, SloženiTip) and parametar.ime == argument.ime and len(parametar.argumenti) == len(argument.argumenti):
            return izračunaj_vartipa_mapiranje(parametar.argumenti, argument.argumenti)
        elif argument == None:
            return izračunaj_vartipa_mapiranje(parametar.argumenti, [argument] * len(parametar.argumenti))
    elif isinstance(parametar, list) and isinstance(argument, list) and len(parametar) == len(argument):
        mapiranja = [izračunaj_vartipa_mapiranje(
            p, a) for (p, a) in zip(parametar, argument)]
        složeno_mapiranje = {}
        for mapiranje in mapiranja:
            for (p, a) in mapiranje.items():
                # treba paziti na konzistentnost mapiranja
                if p not in složeno_mapiranje or složeno_mapiranje[p] == a or složeno_mapiranje[p] == None:
                    složeno_mapiranje[p] = a
                elif p == a:
                    assert(p ^ T.VARTIPA and a ^ T.VARTIPA)
                elif a != None:
                    # raise SemantičkaGreška(
                    #     f'{složeno_mapiranje} već ima ključ {p} koji se ne mapira na {None}, a vrijednost tipa {a} nije {složeno_mapiranje[p]}')
                    raise SemantičkaGreška(
                        f'{a} nije {složeno_mapiranje[p]}')
                # else => a == None, i ne radimo ništa
        return složeno_mapiranje

    raise RuntimeError(
        f'ne mogu izračunati mapiranje za {parametar} i {argument}')


def tip_u_konstruktor(funkcija_tipa, konstruktor, scope, unutar):
    assert(scope[funkcija_tipa.ime] == scope[konstruktor.od])
    dtip = scope[funkcija_tipa.ime]
    ime = konstruktor.ime
    originalni_konstruktor = next(
        filter(lambda x, ime=ime: x.ime == ime, dtip.konstruktori))
    mapiranje = {p: a for (p, a) in zip(
        dtip.parametri, funkcija_tipa.argumenti)}
    parametri = [apply_vartipa_mapping(mapiranje, tip)
                 for tip in originalni_konstruktor.parametri]
    return snailast.Konstruktor(konstruktor.od, konstruktor.ime, parametri)


def konstruktor_u_tip(konstruktor, argumenti, scope, unutar):
    """Vrati funkciju tipa za konstruktor kad se primijene dani argumenti."""
    tip = scope[konstruktor.od]
    funkcija_tipa = SloženiTip(tip.ime, tip.parametri)
    mapiranje = izračunaj_vartipa_mapiranje(konstruktor.parametri, argumenti)
    return apply_vartipa_mapping(mapiranje, funkcija_tipa)


def funkcija_u_tip(pozvana, argumenti, scope, unutar):
    parametri = list(map(lambda p: p.tip, pozvana.parametri))
    mapiranje = izračunaj_vartipa_mapiranje(parametri, argumenti)
    return apply_vartipa_mapping(mapiranje, pozvana.tip)


def equiv_types(a, b, scope, unutar):
    """Checks types a and b for equality within a scope"""
    if a == None:
        return b ^ T.VARTIPA or b ^ elementarni
    elif b == None:
        return a ^ T.VARTIPA or a ^ elementarni
    elif a ^ elementarni or b ^ elementarni:
        assert(a not in scope and b not in scope)  # debugiranje
        return a == b or a ^ T.VARTIPA or b ^ T.VARTIPA
    elif a ^ T.VARTIPA and b ^ T.VARTIPA:
        return a.sadržaj == b.sadržaj
    elif isinstance(a, SloženiTip) and isinstance(b, SloženiTip):
        return all([equiv_types(aarg, barg, scope, unutar)
                    for (aarg, barg) in zip(a.argumenti, b.argumenti)])
    raise SemantičkaGreška(f'greška u provjeravanju ekvivalencije {a} i {b}')
