import numpy as np
import timeit
from functools import reduce
from itertools import accumulate
# import numba
from elements.clib import accumulate_array

# Test of matrices accumulation:
# The input matrices A[0], A[2], ... of the input array (A) are accumlated into the ouput array (B) as follows:
#     B[0] = A[0] (Frist entry remains unchanged)
#     B[1] = A[1] * matrix_array[0]
#     B[2] = A[1] * A[0] * B[0]

__all__ = ['forloop',  'cCode', 'ft_reduce', 'it_accumulate']


def ft_reduce():
    A_flattend = [y for x in a_list_nested for y in x]
    A_flattend.insert(0, np.identity(size))
    return [np.array(reduce(lambda x, y: np.dot(y, x), A_flattend))]  # foldr


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


def forloop():
    array = np.empty((n + 1, size, size))
    array[0] = np.identity(size)
    for i in range(n):
        array[i + 1] = np.dot(a_array[i], array[i])
    return array


# @numba.jit(nopython=True)
# def forloop_numba():
#     array = np.empty((n + 1, size, size))
#     array[0] = np.identity(size)
#     for i in range(n):
#         array[i + 1] = np.dot(a_array[i], array[i])
#     return array


if __name__ == '__main__':
    # setup
    size = 6
    n = 10000
    n_nested = 10
    a_array = np.random.rand(n, size, size) / 2.98  # 3D array of matrices
    a_list = [a_array[i, :, :] for i in range(n)]  # list of matrices
    a_list_nested = [a_list[i:i + n_nested] for i in range(n)[::10]]  # nested list of matrices
    # get functions
    _locals = locals()
    functions = [_locals[x] for x in __all__]

    # Processing Speed
    number = 100
    print("\nProcessing speed:")
    for func in __all__:
        print('{:29}              {:.9f}s'.format(func, timeit.timeit(func + "()", setup="from __main__ import " + func, number=number)))

    # check allclose
    print('\nCheck numpy allclose:')
    for func in functions:
        print('is equal = {}'.format(np.allclose(func()[-1], functions[0]()[-1])))

    # check random index
    index = 0, 0
    print('\nTest element with index {}:'.format(index))
    for func in functions:
        print(func()[-1][index])
