import numpy as np
from timeit import timeit
from elements.clib import twiss_product, twiss_product_old
from elements.utils import Structure
from elements.utils.profiler import profile

__all__ = ['einsum', 'cCode_new', "cCode_new_parallel", 'cCode', 'cCode_parallel', 'dot_app']
# __all__ = ["cCode_new_parallel", 'cCode_new']# ,'cCode', 'cCode_parallel']
# __all__ = ['cCode_new']# ,'cCode', 'cCode_parallel']
# __all__ = ["cCode_new_parallel", 'cCode_new' ,'cCode', 'cCode_parallel']


def einsum():
    # BE =opt_einsum.contract('nij,jk->nik', matrix_array, B0, backend='numpy')
    BE2 = np.einsum('nik,kj->nij', matrix_array, B0, optimize='optimal')
    BE = np.einsum('nik,njk->nij', BE2, matrix_array, optimize='optimal')
    twiss = Structure()
    twiss.betax = BE[:, 0, 0]  # beta_x
    twiss.betay = BE[:, 2, 2]  # beta_y
    twiss.alphax = -BE[:, 0, 1]  # alpha_x
    twiss.alphay = -BE[:, 2, 3]  # alpha_y
    twiss.gammax = BE[:, 1, 1]  # gamma_x
    twiss.gammay = BE[:, 3, 3]  # gamma_y
    # twiss.eta_x = DE[:,0]
    # twiss.detaxds = DE[:,1]  # Dx und Dx
    return twiss.betax


def cCode_new():
    B0vec = np.array([B0[0, 0], B0[2, 2], -B0[0, 1], -B0[2, 3], B0[1, 1], B0[3, 3]])
    twissarray = np.empty((8, matrix_array.shape[0]))
    twiss = Structure()
    twiss.betax = twissarray[0]  # beta_x
    twiss.betay = twissarray[1]  # beta_y
    twiss.alphax = twissarray[2]  # alpha_x
    twiss.alphay = twissarray[3]  # alpha_y
    twiss.gammax = twissarray[4]  # gamma_x
    twiss.gammay = twissarray[5]  # gamma_y
    twiss_product(matrix_array, B0vec, twissarray, 'twiss_product_reduced')
    return twiss.betax


def cCode_new_parallel():
    B0vec = np.array([B0[0, 0], B0[2, 2], -B0[0, 1], -B0[2, 3], B0[1, 1], B0[3, 3]])
    twissarray = np.empty((8, matrix_array.shape[0]))
    twiss = Structure()
    twiss.betax = twissarray[0]  # beta_x
    twiss.betay = twissarray[1]  # beta_y
    twiss.alphax = twissarray[2]  # alpha_x
    twiss.alphay = twissarray[3]  # alpha_y
    twiss.gammax = twissarray[4]  # gamma_x
    twiss.gammay = twissarray[5]  # gamma_y
    twiss_product(matrix_array, B0vec, twissarray, 'twiss_product_reduced_parallel')
    return twiss.betax


def cCode():
    BE = np.empty((n, size, size))
    twiss_product_old(matrix_array, B0, BE, 'twiss_product_full')
    twiss = Structure()
    twiss.betax = BE[:, 0, 0]  # beta_x
    twiss.betay = BE[:, 2, 2]  # beta_y
    twiss.alphax = -BE[:, 0, 1]  # alpha_x
    twiss.alphay = -BE[:, 2, 3]  # alpha_y
    twiss.gammax = BE[:, 1, 1]  # gamma_x
    twiss.gammay = BE[:, 3, 3]  # gamma_y
    # twiss.eta_x = DE[:,0]
    # twiss.detaxds = DE[:,1]  # Dx und Dx
    return twiss.betax


def cCode_parallel():
    BE = np.empty((n, size, size))
    twiss_product_old(matrix_array, B0, BE, 'twiss_product_full_parallel')
    twiss = Structure()
    twiss.betax = BE[:, 0, 0]  # beta_x
    twiss.betay = BE[:, 2, 2]  # beta_y
    twiss.alphax = -BE[:, 0, 1]  # alpha_x
    twiss.alphay = -BE[:, 2, 3]  # alpha_y
    twiss.gammax = BE[:, 1, 1]  # gamma_x
    twiss.gammay = BE[:, 3, 3]  # gamma_y
    # twiss.eta_x = DE[:,0]
    # twiss.detaxds = DE[:,1]  # Dx und Dx
    return twiss.betax


def dot_app():
    matrix_array.shape = n * size, size
    BE2 = np.dot(matrix_array, B0)
    matrix_array.shape = n, size, size
    BE2.shape = n, size, size
    # print(c.flags)
    BE = np.einsum('nik,njk->nij', BE2, matrix_array, optimize='optimal')
    twiss = Structure()
    twiss.betax = BE[:, 0, 0]  # beta_x
    twiss.betay = BE[:, 2, 2]  # beta_y
    twiss.alphax = -BE[:, 0, 1]  # alpha_x
    twiss.alphay = -BE[:, 2, 3]  # alpha_y
    twiss.gammax = BE[:, 1, 1]  # gamma_x
    twiss.gammay = BE[:, 3, 3]  # gamma_y
    # twiss.eta_x = DE[:,0]
    # twiss.detaxds = DE[:,1]  # Dx und Dx
    return twiss.betax


# Test of twiss product:
# An array of matrices (A) times array of matrices (B)
#     C[0] = A[0] * B[0] * AT[0}
#     C[1] = A[1] * B[1] * AT[1}
#     C[2] = A[2] * B[2] * AT[2}
#     ...

if __name__ == '__main__':
    # setup
    size = 5
    n = 40000

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

    # Profiling
    # print("\nProfiling:")
    # for func in functions:
    #     profile_func_ = profile(func, num=1000)()
    #     func_ = profile_func_
    # exit()

    # Processing Speed
    number = 100
    print("\nProcessing speed:")
    for func in functions:
        timeit_seconds = timeit(func.__name__ + "()", setup=f"from __main__ import {func.__name__}", number=number)
        print(f'{func.__name__:25}{ timeit_seconds / number :.9f}s')

    exit()
    # check allclose
    print('\nCheck numpy allclose:')
    for func in functions:
        print(f'is equal = {np.allclose(func(), functions[0]())}')

    # check random index
    index = (np.random.randint(0, n - 1))
    index *= 0
    print(f'\nTest element with index {index}')
    for func in functions:
        print(func()[index])
