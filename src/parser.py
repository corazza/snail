## BKG za našu Snail implementaciju
#
# start -> naredbe
# naredbe -> naredbe naredba | naredba
#
# naredba   -> pridruživanje
#            | print
#            | if
#
# pridruživanje -> IME# JEDNAKO izraz TOČKAZ
#
# print -> PRINT izraz TOČKAZ
#        | PRINT STRING# TOČKAZ
#        | PRINT NEWLINE TOČKAZ
#
# if    -> IF izraz THEN naredbe ENDIF
#        | IF izraz THEN naredbe ELSE naredbe ENDIF
#
# izraz -> OTV izraz ZATV
#        | izraz PLUS izraz
#        | izraz MINUS izraz
#        | izraz PUTA izraz
#        | izraz DIV izraz
#        | izraz MANJE izraz
#        | izraz VECE izraz
#        | izraz JMANJE izraz
#        | izraz JVECE izraz
#        | izraz JEDNAKO izraz
#        | izraz NEJEDNAKO izraz
#        | MINUS izraz
#        | BROJ#
#        | IME#

from vepar import *

from lekser import *
from ast import *

class P(Parser):
    def start(p) -> 'Program':
        naredbe = [p.naredba()]
        while not p > KRAJ:
            naredbe.append(p.naredba())
        return Program(naredbe)

#     def naredba(p) -> 'petlja|ispis|grananje|BREAK':
#         if p > T.FOR:
#             return p.petlja()
#         elif p > T.COUT:
#             return p.ispis()
#         elif p > T.IF:
#             return p.grananje()
#         elif br := p >> T.BREAK:
#             p >> T.TOČKAZ
#             return br

#     def petlja(p) -> 'Petlja':
#         kriva_varijabla = SemantičkaGreška(
#             'Sva tri dijela for-petlje moraju imati istu varijablu.')
#         p >> T.FOR, p >> T.OOTV
#         i = p >> T.IME
#         p >> T.JEDNAKO
#         početak = p >> T.BROJ
#         p >> T.TOČKAZ

#         if (p >> T.IME) != i:
#             raise kriva_varijabla
#         p >> T.MANJE
#         granica = p >> T.BROJ
#         p >> T.TOČKAZ

#         if (p >> T.IME) != i:
#             raise kriva_varijabla
#         if p >= T.PLUSP:
#             inkrement = nenavedeno
#         elif p >> T.PLUSJ:
#             inkrement = p >> T.BROJ
#         p >> T.OZATV

#         if p >= T.VOTV:
#             blok = []
#             while not p >= T.VZATV:
#                 blok.append(p.naredba())
#         else:
#             blok = [p.naredba()]
#         return Petlja(i, početak, granica, inkrement, blok)

#     def ispis(p) -> 'Ispis':
#         p >> T.COUT
#         varijable, novired = [], nenavedeno
#         while p >= T.MMANJE:
#             if varijabla := p >= T.IME:
#                 varijable.append(varijabla)
#             else:
#                 novired = p >> T.ENDL
#                 break
#         p >> T.TOČKAZ
#         return Ispis(varijable, novired)

#     def grananje(p) -> 'Grananje':
#         p >> T.IF, p >> T.OOTV
#         lijevo = p >> T.IME
#         p >> T.JJEDNAKO
#         desno = p >> T.BROJ
#         p >> T.OZATV
#         return Grananje(lijevo, desno, p.naredba())
