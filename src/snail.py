from vepar import *
import sys
import snailparser

import util

filename = sys.argv[1]


with open(filename, 'r') as f:
    src = f.read()
    program = snailparser.P(src)

    print('=== typechecking ===')
    rows = program.typecheck()
    for ime, tip in rows:
        tip = util.token_str(tip)
        print(f'{ime.sadržaj}:  {tip}')
    print()

    print('=== pokretanje ===')
    program.izvrši()
