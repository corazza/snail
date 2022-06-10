## Apstraktna sintaksna stabla
# Program: naredbe: [naredba]
# naredba: 

from vepar import *

class Program(AST):
    naredbe: 'naredba*'

    def izvrši(program):
        rt.mem = Memorija()
        for naredba in program.naredbe: naredba.izvrši()
