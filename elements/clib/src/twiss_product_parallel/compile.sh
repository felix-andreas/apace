#!/usr/bin/env bash
name=twiss_product_parallel
gcc -Ofast -fopenmp -shared -Wl,-soname,cfunc -o ../../shared_objects/$name.so -fPIC $name.c
echo $name compiled!