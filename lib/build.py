import os
from cffi import FFI

SOURCES = ("twiss_product_serial.c", "twiss_product_parallel.c", "accumulate_array.c")
SRC_ROOT = os.path.dirname(os.path.abspath(__file__))

ffi_builder = FFI()
ffi_builder.set_source(
    "apace._clib",
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
    double (*matrices)[6][6], // shape (n-1, 6, 6)
    double *B0,
    double (*twiss)[] // shape (8, n)
);

void twiss_product_parallel (
    int n,
    int from_idx,
    double (*matrices)[6][6], // shape (n -1, 6, 6)
    double *B0,
    double (*twiss)[] // shape (8, n)
);

void matrix_product_accumulated(
    int n,
    int start_idx,
    double (*matrices)[6][6],
    double (*accumulated)[6][6]
);

void matrix_product_ranges(
    int n_ranges,
    int n_matrices,
    int (*ranges)[2],
    double (*matrices)[6][6],
    double (*accumulated)[6][6]
);
"""

ffi_builder.cdef(header)
ffi_builder.compile(verbose=True)
