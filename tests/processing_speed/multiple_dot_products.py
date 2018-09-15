import timeit
from elements.utils import AttrDict, flatten
import numpy as np
import numba
import opt_einsum
from elements.clib import multiple_dot_products

# Test of multiple dot products:
# An array of matrices (A) times array of matrices (B)
#     C[0] = A[0] * B[0]
#     C[1] = A[1] * B[1]
#     C[2] = A[2] * B[2]
#     ...


size = 4
n = 10000

a = np.random.rand(n, size, size)
a_list = [a[i, :, :] for i in range(n)]
num = 10  # size of nested list
a_nested_list = [a_list[i:i + num] for i in range(n)[::10]]
tester = 0
b = np.random.rand(size, size)


class Structure:
    pass


twissdata = Structure()

def GPUimplementationwithopt_einsum():
    pass

def einsum():
    # BE =opt_einsum.contract('nij,jk->nik', a, b, backend='numpy')
    BE = np.einsum('nik,kj->nij', a, b, optimize='optimal')
    # twissdata = AttrDict()
    twissdata.betax = BE[0, 0]  # betax
    twissdata.betay = BE[2, 2]  # betay
    twissdata.alphax = -BE[0, 1]  # alphax
    twissdata.alphay = -BE[2, 3]  # alphay
    twissdata.gammax = BE[1, 1]  # gammax
    twissdata.gammay = BE[3, 3]  # gammay
    return BE


def cCode():
    BE = np.empty((n, size, size))
    multiple_dot_products(a, b, BE)
    twissdata.betax = BE[0, 0]  # betax
    twissdata.betay = BE[2, 2]  # betay
    twissdata.alphax = -BE[0, 1]  # alphax
    twissdata.alphay = -BE[2, 3]  # alphay
    twissdata.gammax = BE[1, 1]  # gammax
    twissdata.gammay = BE[3, 3]  # gammay
    return BE

def dot_app():
    a.shape = n * size, size
    BE = np.dot(a, b)
    a.shape = n, size, size
    BE.shape = n, size, size
    # print(c.flags)
    twissdata = AttrDict()
    twissdata.betax = BE[0, 0]  # betax
    twissdata.betay = BE[2, 2]  # betay
    twissdata.alphax = -BE[0, 1]  # alphax
    twissdata.alphay = -BE[2, 3]  # alphay
    twissdata.gammax = BE[1, 1]  # gammax
    twissdata.gammay = BE[3, 3]  # gammay
    return BE


@numba.jit(nopython=True, parallel=True)
def forloop():
    c = np.empty(a.shape)
    for i in numba.prange(a.shape[0]):
        c[i] = np.dot(a[i], b)
    return c


def dot_simple():
    BE = np.dot(a_list, b)
    # twissdata = Structure()
    twissdata.betax = BE[0, 0]  # betax
    twissdata.betay = BE[2, 2]  # betay
    twissdata.alphax = -BE[0, 1]  # alphax
    twissdata.alphay = -BE[2, 3]  # alphay
    twissdata.gammax = BE[1, 1]  # gammax
    twissdata.gammay = BE[3, 3]  # gammay
    return BE


def forloop_list():
    matrix_array = np.empty(a.shape)
    twissdata = AttrDict()
    twissdata.betax = np.empty(len(a_list))
    twissdata.betay = np.empty(len(a_list))
    twissdata.alphax = np.empty(len(a_list))
    twissdata.alphay = np.empty(len(a_list))
    twissdata.gammax = np.empty(len(a_list))
    twissdata.gammay = np.empty(len(a_list))
    for i, x in enumerate(a_list):
        matrix_array[i, :, :] = BE = np.dot(x, b)
        twissdata.betax[i] = BE[0, 0]  # betax
        twissdata.betay[i] = BE[2, 2]  # betay
        twissdata.alphax[i] = -BE[0, 1]  # alphax
        twissdata.alphay[i] = -BE[2, 3]  # alphay
        twissdata.gammax[i] = BE[1, 1]  # gammax
        twissdata.gammay[i] = BE[3, 3]  # gammay
    return matrix_array


def forloop_list_nested():
    c = np.empty(a.shape)
    index = 0
    for x in a_nested_list:
        for y in (x):
            c[index, :, :] = np.dot(y, b)
            index += 1
    return c


def einsum_list2array():
    a_array = np.array([y for x in a_nested_list for y in x])
    BE = np.einsum('nij,jk->nik', a_array, b)
    twissdata = AttrDict()
    twissdata.betax = BE[0, 0]  # betax
    twissdata.betay = BE[2, 2]  # betay
    twissdata.alphax = -BE[0, 1]  # alphax
    twissdata.alphay = -BE[2, 3]  # alphay
    twissdata.gammax = BE[1, 1]  # gammax
    twissdata.gammay = BE[3, 3]  # gammay
    return BE


print('\nCheck numpy allclose:')
print('is equal = {}'.format(np.allclose(forloop(), einsum())))
print('is equal = {}'.format(np.allclose(dot_simple(), einsum())))
print('is equal = {}'.format(np.allclose(dot_app(), einsum())))
print('is equal = {}'.format(np.allclose(cCode(), einsum())))
print('is equal = {}'.format(np.allclose(forloop_list(), einsum())))
print('is equal = {}'.format(np.allclose(forloop_list_nested(), einsum())))
print('is equal = {}'.format(np.allclose(einsum_list2array(), einsum())))

number = 1000
print("\nProcessing speed:")
print('einsum              {:.9f}s'.format(timeit.timeit("einsum()", setup="from __main__ import einsum", number=number)))
print('cCode               {:.9f}s'.format(timeit.timeit("cCode()", setup="from __main__ import cCode", number=number)))
print('dot_app             {:.9f}s'.format(timeit.timeit("dot_app()", setup="from __main__ import dot_app", number=number)))
print('forloop             {:.9f}s'.format(timeit.timeit("forloop()", setup="from __main__ import forloop", number=number)))
# print('dot_simple          {:.9f}s'.format(timeit.timeit("dot_simple()", setup="from __main__ import dot_simple", number=number)))
# print('forloop_list        {:.9f}s'.format(timeit.timeit("forloop_list()", setup="from __main__ import forloop_list", number=number)))
# print('forloop_list_nested {:.9f}s'.format(timeit.timeit("forloop_list_nested()", setup="from __main__ import forloop_list_nested", number=number)))
# print('einsum_list2array   {:.9f}s'.format(timeit.timeit("einsum_list2array ()", setup="from __main__ import einsum_list2array ", number=number)))


index = (np.random.randint(0, n - 1), np.random.randint(0, size - 1), np.random.randint(0, size - 1))
index = (0,0,0)
print('\nTest element with index {}:'.format(index))
print("{:.15f}, {:.15f}".format(forloop()[index], cCode()[index]))
print("{:.15f}, {:.15f}".format(einsum()[index], dot_app()[index]))
