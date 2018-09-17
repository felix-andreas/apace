import timeit
from elements.utils import AttrDict, flatten
import numpy as np
import numba
import opt_einsum
from elements.clib import twiss_product, twiss_product_parallel, twissparameter
from elements.utils import Structure, profile

__all__ = ['einsum', 'cCode_new', 'cCode', 'cCode_parallel', 'dot_app']


def einsum(a, b):
    # BE =opt_einsum.contract('nij,jk->nik', matrix_array, B0, backend='numpy')
    BE2 = np.einsum('nik,kj->nij', a, b, optimize='optimal')
    BE = np.einsum('nik,njk->nij', BE2, a, optimize='optimal')
    twiss = Structure()
    twiss.betax = BE[:, 0, 0]  # betax
    twiss.betay = BE[:, 2, 2]  # betay
    twiss.alphax = -BE[:, 0, 1]  # alphax
    twiss.alphay = -BE[:, 2, 3]  # alphay
    twiss.gammax = BE[:, 1, 1]  # gammax
    twiss.gammay = BE[:, 3, 3]  # gammay
    # twiss.etax = DE[:,0]
    # twiss.detaxds = DE[:,1]  # Dx und Dx
    return twiss.betax


def cCode_new(matrixarray, B0):
    B0vec = np.array([B0[0, 0], B0[2, 2], -B0[0, 1], -B0[2, 3], B0[1, 1], B0[3, 3]])
    twissarray = np.empty((8, matrix_array.shape[0]))
    twiss = Structure()
    twiss.betax  = twissarray[0]# betax
    twiss.betay  = twissarray[1]# betay
    twiss.alphax = twissarray[2] # alphax
    twiss.alphay = twissarray[3] # alphay
    twiss.gammax = twissarray[4]# gammax
    twiss.gammay = twissarray[5]# gammay
    twissparameter(matrixarray, B0vec, twissarray)
    return twiss.betax


def cCode(a, b):
    BE = np.empty((n, size, size))
    twiss_product(a, b, BE)
    twiss = Structure()
    twiss.betax = BE[:, 0, 0]  # betax
    twiss.betay = BE[:, 2, 2]  # betay
    twiss.alphax = -BE[:, 0, 1]  # alphax
    twiss.alphay = -BE[:, 2, 3]  # alphay
    twiss.gammax = BE[:, 1, 1]  # gammax
    twiss.gammay = BE[:, 3, 3]  # gammay
    # twiss.etax = DE[:,0]
    # twiss.detaxds = DE[:,1]  # Dx und Dx
    return twiss.betax


def cCode_parallel(a, b):
    BE = np.empty((n, size, size))
    twiss_product_parallel(a, b, BE)
    twiss = Structure()
    twiss.betax = BE[:, 0, 0]  # betax
    twiss.betay = BE[:, 2, 2]  # betay
    twiss.alphax = -BE[:, 0, 1]  # alphax
    twiss.alphay = -BE[:, 2, 3]  # alphay
    twiss.gammax = BE[:, 1, 1]  # gammax
    twiss.gammay = BE[:, 3, 3]  # gammay
    # twiss.etax = DE[:,0]
    # twiss.detaxds = DE[:,1]  # Dx und Dx
    return twiss.betax


def dot_app(a, b):
    a.shape = n * size, size
    BE2 = np.dot(a, b)
    a.shape = n, size, size
    BE2.shape = n, size, size
    # print(c.flags)
    BE = np.einsum('nik,njk->nij', BE2, a, optimize='optimal')
    twiss = Structure()
    twiss.betax = BE[:, 0, 0]  # betax
    twiss.betay = BE[:, 2, 2]  # betay
    twiss.alphax = -BE[:, 0, 1]  # alphax
    twiss.alphay = -BE[:, 2, 3]  # alphay
    twiss.gammax = BE[:, 1, 1]  # gammax
    twiss.gammay = BE[:, 3, 3]  # gammay
    # twiss.etax = DE[:,0]
    # twiss.detaxds = DE[:,1]  # Dx und Dx
    return twiss.betax


@numba.jit(nopython=True, parallel=True)
def nb_forloop(a, b):
    c = np.empty(a.shape)
    for i in numba.prange(a.shape[0]):
        c[i] = np.dot(np.dot(a[i], b), a[i])
    return c


# Test of twiss product:
# An array of matrices (A) times array of matrices (B)
#     C[0] = A[0] * B[0] * AT[0}
#     C[1] = A[1] * B[1] * AT[1}
#     C[2] = A[2] * B[2] * AT[2}
#     ...
if __name__ == '__main__':
    # setup
    size = 5
    n = 10000
    # build matrix array
    matrix_array = np.zeros((n, size, size))
    matrix_array[:, 0:2, 0:2] = np.random.rand(n, 2, 2)
    matrix_array[:, 2:4, 2:4] = np.random.rand(n, 2, 2)
    matrix_array[:, 0:2, 4] = np.random.rand(n, 2)
    matrix_array[:, -1, -1] = 1
    # build twiss array siehe method 2 of klaus wille chapter 3.10
    B0 = np.zeros((size, size))
    B0[0:2, 0:2] = np.random.rand(2, 2)
    B0[1, 0] = B0[0, 1]
    B0[2:4, 2:4] = np.random.rand(2, 2)
    B0[3, 2] = B0[2, 3]
    B0vec = np.array([B0[0, 0], B0[2, 2], -B0[0, 1], -B0[2, 3], B0[1, 1], B0[3, 3]])
    # print(matrix_array[0])
    # print(B0)
    # print(B0vec)

    # get functions
    _locals = locals()
    functions = [_locals[x] for x in __all__]

    # Processing Speed
    number = 100
    print("\nProcessing speed:")
    for func in __all__:
        print('{:29}              {:.9f}s'.format(func, timeit.timeit(func + "(matrix_array,B0)", setup="from __main__ import matrix_array, B0, " + func, number=number)))

    # check allclose
    print('\nCheck numpy allclose:')
    for func in functions:
        print('is equal = {}'.format(np.allclose(func(matrix_array, B0), functions[0](matrix_array, B0))))

    # check random index
    index = (np.random.randint(0, n - 1))
    index = 0
    print('\nTest element with index {}:'.format(index))
    for func in functions:
        print(func(matrix_array, B0)[index])
