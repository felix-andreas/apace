import os
import ctypes
import numpy as np

clib = ctypes.CDLL(os.path.dirname(__file__) + '/accumulate_array/accumulate_array.so')
clib.accumulate_array.restype = None


def accumulate_array(input_array, output_array):
    """
    The input matrices A[0], A[2], ... of the input array (A) are accumlated into the ouput array (B) as follows:

        B[0] = B[0]
        B[1] = A[1] * B[0]
        B[2] = A[1] * A[0] * B[0]
        ...

    Parameters
        ----------
        input_array : ndarray
            Input array with n matrices
            Shape = (n, size, size)
        output_array : ndarray
            The calculation is done into this array.
            Shape : (n + 1, size, size)
    """
    if input_array.shape[0] == output_array.shape[0] - 1 and input_array.shape[1:3] == output_array.shape[1:3]:
        n = input_array.shape[0]
        size = input_array.shape[1]
        clib.accumulate_array(ctypes.c_int(n), ctypes.c_int(size), np.ctypeslib.as_ctypes(input_array), np.ctypeslib.as_ctypes(output_array))
    else:
        raise ValueError("Wrong shapes! input_array {} and output_array {}".format(input_array.shape, output_array.shape))
