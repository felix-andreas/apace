#!/usr/bin/env bash
name=twiss_product_parallel
gcc -Ofast -fopenmp -shared -Wl,-soname,cfunc -fPIC $name.c -o ../../shared_objects/$name.so
echo $name compiled!