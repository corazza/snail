import os
import glob

from vepar import *


class Povratak(NelokalnaKontrolaToka):
    pass


def token_str(x):
    if isinstance(x, Token):
        return x.sadržaj
    elif x == None:
        return "_"
    else:
        return str(x)

def printanje_str(x):
    if isinstance(x, Token):
        raise SemantičkaGreška("vrijednost ne bi trebala biti Token")
    elif x == None:
        raise SemantičkaGreška("vrijednost ne bi trebala biti None")
    elif isinstance(x, str):
        return '"' + x + '"'
    else:
        return str(x)
