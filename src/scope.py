from vepar import *


class Scope:
    def __init__(self, parent=None):
        self.mem = Memorija()
        self.parent = parent

    # def __delitem__(self, lokacija):
    #     del self.mem[lokacija]

    def __getitem__(self, lokacija):
        if lokacija in self.mem or self.parent == None:
            return self.mem[lokacija]
        else:
            return self.parent[lokacija]

    def __setitem__(self, lokacija, vrijednost):
        self.mem[lokacija] = vrijednost

    def __contains__(self, lokacija):
        if self.parent == None:
            return lokacija in self.mem
        else:
            return lokacija in self.mem or lokacija in self.parent
