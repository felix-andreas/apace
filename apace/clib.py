# noinspection PyUnresolvedReferences,PyProtectedMember
from ._clib._twiss_product import ffi, lib


# from python_utils.profile import profile_by_line
# @profile_by_line(exit=1)
def twiss_product(matrix_array, b0_vec, twiss_array, parallel=False):
    """
    Twiss product of matrices of A times matrices of B as follows:
        ...
    Parameters
        ----------
        matrix_array : np.ndarray
            Input array with n matrices.
            Shape = (n - 1, size, size)
        b0_vec : np.ndarray
            Vector with inital values of Twiss parameters.
            Shape = (8,)
        twiss_array : np.ndarray
            The array into which the result is stored.
            Shape : (8, n)
    """
    n = twiss_array.shape[1]
    args = (
        n,
        ffi.cast("double (*)[6][6]", ffi.from_buffer(matrix_array)),
        ffi.cast("double *", ffi.from_buffer(b0_vec)),
        ffi.cast("double (*)[]", ffi.from_buffer(twiss_array)),
    )

    func = lib.twiss_product_parallel if parallel else lib.twiss_product_serial
    func(*args)


# from python_utils.profile import profile_by_line
# @profile_by_line(exit=1)
def accumulated_array(input_array, output_array):
    """
    The input matrices A[0], A[2], ... of the input array (A)
    are accumulated into the output array (B) as follows:

        B[0] = A[0] (First entry remains unchanged)
        B[1] = A[1] * A[0]
        B[2] = A[1] * A[0] * B[0]
        ...

    Parameters
        ----------
        input_array : np.ndarray
            Input array with n matrices
            Shape = (n, size, size)
        output_array : np.ndarray
            The array into which the result is stored.
            Shape : (n, size, size)
    """
    n = input_array.shape[0]
    args = (
        n,
        6,
        ffi.cast("double (*)[6][6]", ffi.from_buffer(input_array)),
        ffi.cast("double (*)[6][6]", ffi.from_buffer(output_array)),
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
