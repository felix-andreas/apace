import os
import ctypes
import numpy as np

__all__ = ['accumulate_array', 'multiple_dot_products']

lib1 = ctypes.CDLL(os.path.dirname(__file__) + '/shared_objects/accumulate_array.so')
lib1.accumulate_array.restype = None


def accumulate_array(input_array, output_array):
    """
    The input matrices A[0], A[2], ... of the input array (A) are accumlated into the ouput array (B) as follows:

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
    if input_array.shape == output_array.shape:
        n = output_array.shape[0]
        size = output_array.shape[1]
        lib1.accumulate_array(ctypes.c_int(n), ctypes.c_int(size), np.ctypeslib.as_ctypes(input_array), np.ctypeslib.as_ctypes(output_array))
    else:
        raise ValueError("Wrong shapes! input_array {} and output_array {}".format(input_array.shape, output_array.shape))


lib2 = ctypes.CDLL(os.path.dirname(__file__) + '/shared_objects/multiple_dot_products.so')
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
    if A.shape[1:3] == B.shape:
        n = A.shape[0]
        size = A.shape[1]
        lib1.multiple_dot_products(ctypes.c_int(n), ctypes.c_int(size), np.ctypeslib.as_ctypes(A), np.ctypeslib.as_ctypes(B), np.ctypeslib.as_ctypes(out))
    else:
        raise ValueError("Wrong shapes! A {} and B {}".format(A.shape, B.shape))
