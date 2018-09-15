#!/usr/bin/env bash
name=multiple_dot_products
gcc -Ofast -shared -Wl,-soname,cfunc -o ../../shared_objects/$name.so -fPIC $name.c
echo $name compiled!