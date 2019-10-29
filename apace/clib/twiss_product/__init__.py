from ._twiss_product import ffi, lib

# from python_utils.profile import profile_by_line
# @profile_by_line(exit=1)
def twiss_product(matrix_array, b0_vec, twiss_array, parallel=False):
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
    n = transfer_matrices.shape[0]
    args = (
        n,
        6,
        ffi.cast("double (*)[6][6]", ffi.from_buffer(transfer_matrices)),
        ffi.cast("double (*)[6][6]", ffi.from_buffer(acc_array)),
    )

    lib.accumulate_array(*args)

