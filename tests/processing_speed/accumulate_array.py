import numpy as np
import timeit
from functools import reduce
from itertools import accumulate
import numba
from elements.clib import accumulate_array

# Test of matrices accumulation:
# The input matrices A[0], A[2], ... of the input array (A) are accumlated into the ouput array (B) as follows:
#     B[0] = A[0] (Frist entry remains unchanged)
#     B[1] = A[1] * a[0]
#     B[2] = A[1] * A[0] * B[0]

size = 6
n = 10000
n_nested = 10
a_array = np.random.rand(n, size, size) / 2.98  # 3D array of matrices
a_list = [a_array[i, :, :] for i in range(n)]  # list of matrices
a_list_nested = [a_list[i:i + n_nested] for i in range(n)[::10]]  # nested list of matrices


def ft_reduce():
    A_flattend = [y for x in a_list_nested for y in x]
    A_flattend.insert(0, np.identity(size))
    return np.array(reduce(lambda x, y: np.dot(y, x), A_flattend))  # foldr


def cCode():
    array = np.empty((n + 1, size, size))
    array[0] = np.identity(size)
    accumulate_array(a_array, array[1:])
    return array


def it_accumulate():
    A_flattend = [y for x in a_list_nested for y in x]
    A_flattend.insert(0, np.identity(size))
    # accumulate(A_flattend, np.dot)
    return np.array(list(accumulate(A_flattend, lambda x, y: np.dot(y, x))))  # foldr


@numba.jit(nopython=True)
def forloop_numba():
    array = np.empty((n + 1, size, size))
    array[0] = np.identity(size)
    for i in range(n):
        array[i + 1] = np.dot(a_array[i], array[i])
    return array


def forloop():
    array = np.empty((n + 1, size, size))
    array[0] = np.identity(size)
    i = 1
    for i2 in range(int(n / n_nested)):
        for i3 in range(n_nested):
            array[i] = np.dot(a_list_nested[i2][i3], array[i - 1])
            i = i + 1
    return array

print('\nCheck numpy allclose:')
print('is allclose = {}'.format(np.allclose(ft_reduce(), it_accumulate()[-1])))
print('is allclose = {}'.format(np.allclose(it_accumulate(), cCode())))
print('is allclose = {}'.format(np.allclose(it_accumulate(), forloop())))
print('is allclose = {}'.format(np.allclose(it_accumulate(), forloop_numba())))

number = 100
print("\nProcessing speed:")
print('ft_reduce       {:.9f}s'.format(timeit.timeit("ft_reduce()", setup="from __main__ import ft_reduce", number=number)))
print('it_accumulate   {:.9f}s'.format(timeit.timeit("it_accumulate()", setup="from __main__ import it_accumulate", number=number)))
print('cCode           {:.9f}s'.format(timeit.timeit("cCode()", setup="from __main__ import cCode", number=number)))
print('forloop_numba   {:.9f}s'.format(timeit.timeit("forloop_numba()", setup="from __main__ import forloop_numba", number=number)))
print('forloop         {:.9f}s'.format(timeit.timeit("forloop()", setup="from __main__ import forloop", number=number)))


index = (np.random.randint(0, n - 1), np.random.randint(0, size - 1), np.random.randint(0, size - 1))
print('\nTest element with index {}:'.format(index))
print("{:.15f}, {:.15f}".format(it_accumulate()[index], cCode()[index]))
print("{:.15f}, {:.15f}".format(forloop()[index], forloop_numba()[index]))
