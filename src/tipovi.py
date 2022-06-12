from lekser import *
from vepar import *
from scope import *

elementarni = {T.INT, T.BOOL, T.STRINGT, T.UNITT}


class FunkcijaTipa(AST):
    ime: 'VELIKOIME'
    argumenti: 'tip*'

    def typecheck(self, scope, unutar):
        for p in self.argumenti:
            p.typecheck(scope, unutar)
        return self


def tip_u_konstruktor(tip, konstruktor, scope, unutar):
    assert(scope[tip.ime] == scope[konstruktor.od])
    new_scope = Scope(None)

    dtip = scope[tip.ime]
    ime = konstruktor.ime

    originalni_konstruktor = next(
        filter(lambda x, ime=ime: x.ime == ime, dtip.konstruktori))

    import IPython
    IPython.embed()


def konstruktor_u_tip(konstruktor, argumenti, scope, unutar):
    import IPython
    IPython.embed()


def equiv_types(a, b, scope, unutar):
    """Checks types a and b for equality within a scope"""
    if a ^ elementarni or b ^ elementarni:
        return a == b

    if a ^ T.VARTIPA and b ^ T.VARTIPA:
        return a.sadržaj == b.sadržaj

    if isinstance(a, SloženiTip) and isinstance(b, SloženiTip):
        if a.argumenti == None or b.argumenti == None:
            return a.ime == b.ime

        return all([equiv_types(aarg, barg, scope, unutar)
                    for (aarg, barg) in zip(a.argumenti, b.argumenti)])

    import IPython
    IPython.embed()
    raise SemantičkaGreška(f'{a} i {b} nisu tipovi')
