import os
import ctypes
import numpy as np

__all__ = ['accumulate_array', 'multiple_dot_products', 'twiss_product', 'twiss_product_old']
SHARED_OBJECTS_PATH = os.path.dirname(__file__) + '/shared_objects/'

lib1 = ctypes.CDLL(SHARED_OBJECTS_PATH + 'accumulate_array.so')
lib1.accumulate_array.restype = None


def accumulate_array(input_array, output_array):
    """
    The input matrices A[0], A[2], ... of the input array (A)
    are accumulated into the output array (B) as follows:

        B[0] = A[0] (Frist entry remains unchanged)
        B[1] = A[1] * A[0]
        B[2] = A[1] * A[0] * B[0]
        ...

    Parameters
        ----------
        input_array : ndarray
            Input array with n matrices
            Shape = (n, size, size)
        output_array : ndarray
            The calculation is done into this array.
            Shape : (n, size, size)
    """
    if input_array.shape != output_array.shape:
        raise ValueError(f'Wrong shapes! input_array {input_array.shape} and output_array {output_array.shape}')
    n = output_array.shape[0]
    size = output_array.shape[1]
    lib1.accumulate_array(ctypes.c_int(n), ctypes.c_int(size),
                          np.ctypeslib.as_ctypes(input_array), np.ctypeslib.as_ctypes(output_array))


lib2 = ctypes.CDLL(SHARED_OBJECTS_PATH + 'multiple_dot_products.so')
lib2.multiple_dot_products.restype = None


def multiple_dot_products(A, B, out):
    """
    Dot product of matrices of A times matrices of B as follows:
        out[0] = A[0] * B[0]
        out[1] = A[1] * B[1]
        out[2] = A[2] * B[2]
        ...

    Parameters
        ----------
        A : ndarray
            Input array with n matrices.
            Shape = (n, size, size)
        B : ndarray
            Single matrix.
            Shape = (size, size)
        out : ndarray
            The calculation is done into this array.
            Shape : (n, size, size)
    """
    if A.shape[1:3] != B.shape:
        raise ValueError(f'Wrong shapes! A {A.shape} and B {B.shape}')
    n = A.shape[0]
    size = A.shape[1]
    lib2.multiple_dot_products(ctypes.c_int(n), ctypes.c_int(size), np.ctypeslib.as_ctypes(A),
                               np.ctypeslib.as_ctypes(B), np.ctypeslib.as_ctypes(out))


twiss_product_modes = ['twiss_product_reduced', 'twiss_product_reduced_parallel']
twiss_product_lib = {}
for mode in twiss_product_modes:
    twiss_product_lib[mode] = ctypes.CDLL(SHARED_OBJECTS_PATH + f'{mode}.so').twiss_product
    twiss_product_lib[mode].restype = None


def twiss_product(matrix_array, B0vec, twiss, mode):
    """
    Twiss product of matrices of A times matrices of B as follows:
        ...
    Parameters
        ----------
        matrixarray : ndarray
            Input array with n matrices.
            Shape = (n, size, size)
        B0vec : ndarray
            Vector with inital values of Twiss parameters.
            Shape = (6)
        twiss : ndarray
            The calculation is done into this array.
            Shape : (n, 6)
    """
    if mode not in twiss_product_modes:
        raise Exception('Unknown twiss_product_modes mode!')
    if matrix_array.shape[0] == twiss.shape[1]:
        n = matrix_array.shape[0]
        size = matrix_array.shape[1]
        twiss_product_lib[mode](ctypes.c_int(n), ctypes.c_int(size), np.ctypeslib.as_ctypes(matrix_array),
                                np.ctypeslib.as_ctypes(B0vec), np.ctypeslib.as_ctypes(twiss))
    else:
        raise ValueError(f'Wrong shapes! matrix_array {matrix_array} and B0vec {B0vec}')


twiss_product_modes_old = ['twiss_product_full', 'twiss_product_full_parallel']
twiss_product_lib_old = {}
for mode in twiss_product_modes_old:
    twiss_product_lib_old[mode] = ctypes.CDLL(SHARED_OBJECTS_PATH + f'{mode}.so').twiss_product
    twiss_product_lib_old[mode].restype = None


def twiss_product_old(A, B, out, mode):
    """
    Twiss product of matrices of A times matrices of B as follows:
        out[0] = A[0] * B[0] * AT[0}
        out[1] = A[1] * B[1] * AT[1}
        out[2] = A[2] * B[2] * AT[2}
        ...
    Parameters
        ----------
        A : ndarray
            Input array with n matrices.
            Shape = (n, size, size)
        B : ndarray
            Single matrix.
            Shape = (size, size)
        out : ndarray
            The calculation is done into this array.
            Shape : (n, size, size)
    """
    if mode not in twiss_product_modes_old:
        raise Exception('Unknown twiss_product_modes mode!')
    if A.shape[1:3] == B.shape:
        n = A.shape[0]
        size = A.shape[1]
        twiss_product_lib_old[mode](ctypes.c_int(n), ctypes.c_int(size), np.ctypeslib.as_ctypes(A),
                                              np.ctypeslib.as_ctypes(B), np.ctypeslib.as_ctypes(out))
    else:
        raise ValueError("Wrong shapes! A {A.shape} and B {B.shape}")
