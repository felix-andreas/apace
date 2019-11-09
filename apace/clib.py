# noinspection PyUnresolvedReferences,PyProtectedMember
from ._clib._twiss_product import ffi, lib
import numpy as np


# from pyprofilers import profile_by_line
# @profile_by_line(exit=1)
def twiss_product(transfer_matrices, twiss_0, twiss_array, from_idx, parallel=False):
    """Calculates the Twiss product of the transfer matrices and the initial
    Twiss parameters twiss_0 into the twiss_array:

    :param np.ndarray transfer_matrices: Array of accumulated transfer_matrices.
    :param np.ndarray twiss_0: Initial twiss parameter.
    :param np.ndarray twiss_array: Array where the result of the calculation is stored.
    :param int from_idx: The index from which the matrices are accumulated.
    :param bool parallel: Flag to utilize multiple cpu cores.
           Parallel overhead can make slower for small lattices.
    """
    n = twiss_array.shape[1]
    args = (
        n,
        from_idx,
        ffi.cast('double (*)[6][6]', ffi.from_buffer(transfer_matrices)),
        ffi.cast('double *', ffi.from_buffer(twiss_0)),
        ffi.cast('double (*)[]', ffi.from_buffer(twiss_array)),
    )

    func = lib.twiss_product_parallel if parallel else lib.twiss_product_serial
    func(*args)


# from pyprofilers import profile_by_line
# @profile_by_line(exit=1)
def accumulate_array(input_array, output_array, from_idx):
    """ Accumulated an array of matrices to a given index.

    The input matrices A[0], A[2], ... of the input array (A)
    are accumulated into the output array (B) as follows:

        B[0] = A[0] (First entry remains unchanged)
        B[1] = A[1] * A[0]
        B[2] = A[1] * A[0] * B[0]
        ...

    :param np.ndarray input_array: Input array with n matrices. Shape = (n, size, size)
    :param np.ndarray output_array: The array into which the result is stored. Shape : (n, size, size)
    :param int from_idx: The index from which the matrices are accumulated.
    """
    n = input_array.shape[0]
    if from_idx >= n:
        raise IndexError(
            f'The parameter from_idx ({from_idx}) '
            f'cannot be larger than the number of kicks ({n})!'
        )

    args = (
        n,
        from_idx,
        ffi.cast('double (*)[6][6]', ffi.from_buffer(input_array)),
        ffi.cast('double (*)[6][6]', ffi.from_buffer(output_array)),
    )

    lib.accumulate_array(*args)


# from pyprofilers import profile_by_line
# @profile_by_line(exit=1)
def accumulate_array_partial(input_array, output_array, indices):
    """ Returns the accumulated transfer matrices between given start and end values.

    The final array has the shape (n, size, size) and contains the accumulated transfer matrices between
    the given indices:

    B[0] = A[end_0] * A[end_0 - 1] * ... * A[start_0]
    B[1] = A[end_1] * A[end_1 - 1] * ... * A[start_1]
    ...

    where start_i = indices[i, 0] and end_i = indices[i, 1]

    :param np.ndarray input_array: Input array with n matrices. Shape = (n_kicks, size, size)
    :param np.ndarray output_array: The array into which the result is stored. Shape : (n, size, size)
    :param array-like indices: The indices from which and to the matrices are accumulated.
                               Has shape (n, 2), where indices[:, 0] are the start and indices[:, 1] are
                               the end values.
    """
    n_kicks = input_array.shape[0]
    n_indices = indices.shape[0]
    if indices.shape[1] != 2:
        raise ValueError('The argument indices has the wrong shape! (Expected (n, 2))')

    if not isinstance(indices, np.ndarray):
        indices = np.array(indices)

    args = (
        n_indices,
        ffi.cast('double (*)[2]', ffi.from_buffer(indices)),
        n_kicks,
        ffi.cast('double (*)[6][6]', ffi.from_buffer(input_array)),
        ffi.cast('double (*)[6][6]', ffi.from_buffer(output_array)),
    )

    lib.accumulate_array(*args)


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
    raise NotImplementedError
