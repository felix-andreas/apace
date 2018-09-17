import timeit

import numpy as np
import elements as el
import numba
# from elements.linbeamdyn.twissfunctions import get_twissdata

Q1 = el.Quad('Q1', l=2, k1=1)
B1 = el.Bend('B1', l=1, angle=np.pi / 4)
Q2 = el.Quad('Q2', l=2, k1=-1)
D1 = el.Drift('D1', l=1)
FODO = el.Line('fodo-cell', [Q1, D1, B1, D1, Q2, D1, B1, D1])
interFODO = el.Line('inter-Fodo', [FODO] * 100)
ring = el.Mainline('fodo-ring', [interFODO] * 100)


def update_lattice(tree):
    for x in tree:
        if isinstance(x, el.Line):
            yield from update_lattice(x.tree)
        else:
            yield x




def fun1():
    liste =  list(update_lattice(ring.tree))
    seto = set(liste)
    return liste

def fun2():
    def update_lattice2(tree):
        for x in tree:
            if isinstance(x, el.Line):
                update_lattice2(x.tree)
            else:
                liste.append(x)
                seto.add(x)
    liste = list()
    seto= set()
    update_lattice2(ring.tree)
    seto = list(seto)
    return liste

print(fun1() == fun2())
num=10
print(timeit.timeit('fun1()', setup='from __main__ import fun1', number=num))
print(timeit.timeit('fun2()', setup='from __main__ import fun2', number=num))