import timeit
from elements.utils import AttrDict, flatten
import numpy as np
import numba
size = 6
n = 10000

a = np.random.rand(n, size, size)
a_list = [a[i, :, :] for i in range(n)]
num = 10 # size of nested list
a_nested_list = [a_list[i:i + num] for i in range(n)[::10]]
tester = 0
b = np.random.rand(size, size)

@numba.jit(nopython=True, parallel=True)
def forloop():
    c = np.empty(a.shape)
    for i in numba.prange(a.shape[0]):
        c[i] = np.dot(a[i], b)
    return c

def dot_simple():
    BE = np.dot(a_list,b)
    twissdata = AttrDict()
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


def einsum():
    BE = np.einsum('nij,jk->nik', a, b, optimize='optimal')
    twissdata = AttrDict()
    twissdata.betax = BE[0, 0]  # betax
    twissdata.betay = BE[2, 2]  # betay
    twissdata.alphax = -BE[0, 1]  # alphax
    twissdata.alphay = -BE[2, 3]  # alphay
    twissdata.gammax = BE[1, 1]  # gammax
    twissdata.gammay = BE[3, 3]  # gammay
    return BE

def einsum_list2array():
    # a_array = np.empty(a.shape)
    # index = 0
    # for x in a_nested_list:
    #     for y in (x):
    #         a_array[index, :, :] = y
    #         index += 1
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


print('is equal = {}'.format(np.allclose(forloop(), einsum())))
print('is equal = {}'.format(np.allclose(dot_simple(), einsum())))
print('is equal = {}'.format(np.allclose(dot_app(), einsum())))
print('is equal = {}'.format(np.allclose(forloop_list(), einsum())))
print('is equal = {}'.format(np.allclose(forloop_list_nested(), einsum())))
print('is equal = {}'.format(np.allclose(einsum_list2array(), einsum())))

number = 100
print('forloop             {:.9f}s'.format(timeit.timeit("forloop()", setup="from __main__ import forloop", number=number)))
print('dot_simple          {:.9f}s'.format(timeit.timeit("dot_simple()", setup="from __main__ import dot_simple", number=number)))
print('dot_app             {:.9f}s'.format(timeit.timeit("dot_app()", setup="from __main__ import dot_app", number=number)))
print('forloop_list        {:.9f}s'.format(timeit.timeit("forloop_list()", setup="from __main__ import forloop_list", number=number)))
print('forloop_list_nested {:.9f}s'.format(timeit.timeit("forloop_list_nested()", setup="from __main__ import forloop_list_nested", number=number)))
print('einsum              {:.9f}s'.format(timeit.timeit("einsum()", setup="from __main__ import einsum", number=number)))
print('einsum_list2array   {:.9f}s'.format(timeit.timeit("einsum_list2array ()", setup="from __main__ import einsum_list2array ", number=number)))

#
# def forloop_append():
#     c = np.empty((0,size,size))
#     for i in range(a.shape[0]):
#         c = np.append(c,np.dot(a[i, :, :], b))
#     return c
