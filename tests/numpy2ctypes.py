import ctypes
import numpy as np

testlib = ctypes.CDLL('./cfunc.so')

size = 5
n = 10
num = size * size * n

outa = np.ones((n + 1, size, size),np.float) *10
outa[0] = np.identity(size)
ina = np.empty((n, size,size),np.float)
ina[:] = np.identity(size)
ina[:,0,0] = 2

testlib.accumulate_array.restype = None
testlib.accumulate_array(ctypes.c_int(n), ctypes.c_int(size), np.ctypeslib.as_ctypes(ina), np.ctypeslib.as_ctypes(outa))
print("intial array\n", ina)
print("final array\n ", outa)
