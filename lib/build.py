import os
from cffi import FFI

SOURCES = ("twiss_product_serial.c", "twiss_product_parallel.c", "accumulate_array.c")
SRC_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../lib")

ffi_builder = FFI()
ffi_builder.set_source(
    "apace._clib._twiss_product",
    "".join(f'#include "{source}"\n' for source in SOURCES),
    include_dirs=[SRC_ROOT],
    extra_compile_args=[
        "-fopenmp",
        "-D use_openmp",
        "-Ofast",
        "-march=native",
        "-ffast-math",
    ],
    extra_link_args=["-fopenmp"],
)

header = """\
void twiss_product_serial (
        int n,
        int from_idx,
        double (*matrix_array)[6][6], // shape (6, 6, n - 1)
        double *B0,
        double (*twiss_array)[] // shape (8, n)
);

void twiss_product_parallel (
        int n,
        int from_idx,
        double (*matrix_array)[6][6], // shape (6, 6, n - 1)
        double *B0,
        double (*twiss_array)[] // shape (8, n)
);

void accumulate_array(
        int n,
        int from_idx,
        double (*input_array)[6][6],
        double (*accumulated_array)[6][6]
);

void accumulate_array_partial(
        int n_indices,
        int (*indices)[2],
        int n_kicks,
        double (*input_array)[6][6],
        double (*accumulated_array)[6][6]
);
"""

ffi_builder.cdef(header)
ffi_builder.compile(verbose=True)
