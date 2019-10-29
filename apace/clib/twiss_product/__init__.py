from ._twiss_product import ffi, lib


# from python_utils.profile import profile_by_line
# @profile_by_line(exit=1)
def twiss_product(matrix_array, b0_vec, twiss_array, parallel=False):
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
    n = matrix_array.shape[0]
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
def accumulated_array(transfer_matrices, acc_array):
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
    n = transfer_matrices.shape[0]
    args = (
        n,
        6,
        ffi.cast("double (*)[6][6]", ffi.from_buffer(transfer_matrices)),
        ffi.cast("double (*)[6][6]", ffi.from_buffer(acc_array)),
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
