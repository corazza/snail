import os
import glob

from vepar import *

import IPython # TODO remove

def test_on_single(test, filename):
    with open(filename, 'r') as f:
        print(f"========= {filename} =========")
        test(f.read())
        print()
        print()


def test_on_directory(test, path='../primjeri'):
    for filename in glob.glob(os.path.join(path, '*.snail')):
        if filename.startswith('_'):
            continue
        filename = os.path.join(os.getcwd(), filename)
        test_on_single(test, filename)


def test_on(test):
    import sys
    if len(sys.argv) > 1:
        test_on_single(test, '../primjeri/' + sys.argv[1] + '.snail')
    else:
        test_on_directory(test)


class Povratak(NelokalnaKontrolaToka):
    pass

def token_repr(x):
    if isinstance(x, Token):
        return x.sadržaj
    elif x == None:
        return "_"
    else:
        return repr(x)
