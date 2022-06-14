import os
import glob

from vepar import *


class Povratak(NelokalnaKontrolaToka):
    pass


def token_repr(x):
    if isinstance(x, Token):
        return x.sadržaj
    elif x == None:
        return "_"
    else:
        return repr(x)
