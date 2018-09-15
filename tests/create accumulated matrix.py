import numpy as np
import timeit
from functools import reduce
from itertools import accumulate
import numba
from elements.clib import accumulate_array

size = 6
n = 10000
a = np.random.rand(n, size, size) / 3
a_list = [a[i, :, :] for i in range(n)]
num = 10
A = [a_list[i:i + num] for i in range(n)[::10]]


def ft_reduce():
    A_flattend = [y for x in A for y in x]
    A_flattend.insert(0, np.identity(size))
    return np.array(reduce(lambda x, y: np.dot(y, x), A_flattend))  # foldr


def cCode():
    array = np.empty((n + 1, size, size))
    array[0] = np.identity(size)
    accumulate_array(a, array)
    return array


def it_accumulate():
    A_flattend = [y for x in A for y in x]
    A_flattend.insert(0, np.identity(size))
    # accumulate(A_flattend, np.dot)
    return np.array(list(accumulate(A_flattend, lambda x, y: np.dot(y, x))))  # foldr


@numba.jit(nopython=True)
def forloop_numba():
    array = np.empty((n + 1, size, size))
    array[0] = np.identity(size)
    for i in range(n):
        array[i + 1] = np.dot(a[i], array[i])
    return array


# @numba.jit
def forloop():
    array = np.empty((n + 1, size, size))
    array[0] = np.identity(size)
    i = 1
    for i2 in range(int(n / num)):
        for i3 in range(num):
            array[i] = np.dot(A[i2][i3], array[i - 1])
            i = i + 1
    return array


print('is equal = {}'.format(np.allclose(ft_reduce(), it_accumulate()[-1])))
print('is equal = {}'.format(np.allclose(it_accumulate(), cCode())))
print('is equal = {}'.format(np.allclose(it_accumulate(), forloop())))
print('is equal = {}'.format(np.allclose(it_accumulate(), forloop_numba())))

number = 100
print('ft_reduce       {:.9f}s'.format(timeit.timeit("ft_reduce()", setup="from __main__ import ft_reduce", number=number)))
print('cCode           {:.9f}s'.format(timeit.timeit("cCode()", setup="from __main__ import cCode", number=number)))
print('it_accumulate   {:.9f}s'.format(timeit.timeit("it_accumulate()", setup="from __main__ import it_accumulate", number=number)))
print('forloop_numba   {:.9f}s'.format(timeit.timeit("forloop_numba()", setup="from __main__ import forloop_numba", number=number)))
print('forloop         {:.9f}s'.format(timeit.timeit("forloop()", setup="from __main__ import forloop", number=number)))
