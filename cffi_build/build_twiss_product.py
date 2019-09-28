import os
from cffi import FFI

SOURCES = ('twiss_product_serial.c', 'twiss_product_parallel.c', 'accumulate_array.c')
SRC_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../src')

ffi_builder = FFI()
ffi_builder.set_source(
    'elements.clib.twiss_product._twiss_product',
    ''.join(f'#include "{source}"\n' for source in SOURCES),
    include_dirs=[SRC_ROOT],
    extra_compile_args=['-fopenmp', '-D use_openmp', '-Ofast', '-march=native', '-ffast-math'],
    extra_link_args=['-fopenmp'],
)

ffi_builder.cdef(
    '''
    void twiss_product_serial(int n, double (*matrix_array)[5][5], double *B0, double (*twiss_array)[]);
    void twiss_product_parallel(int n, double (*matrix_array)[5][5], double *B0, double (*twiss_array)[]);
    void accumulate_array(int n, int size, double (*ina)[5][5], double (*outa)[5][5]);
    '''
)

ffi_builder.compile(verbose=True)
