#!/usr/bin/env bash
name=twissparameter
gcc -Ofast -shared -Wl,-soname,cfunc -o ../../shared_objects/$name.so -fPIC $name.c
echo $name compiled!