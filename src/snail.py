from vepar import *
import sys
import snailparser

filename = sys.argv[1]


with open(filename, 'r') as f:
    src = f.read()
    program = snailparser.P(src)

    print('=== typechecking ===')
    program.typecheck()
    print()

    print('=== pokretanje ===')
    program.izvrši()
