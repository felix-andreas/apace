#!/usr/bin/env bash
name=twissparameter_parallel

if $(gcc -Ofast -fopenmp -shared -Wl,-soname,cfunc -fPIC $name.c -o ../../shared_objects/$name.so); then
    echo $name compiled!

    apy="$HOME/anaconda3/bin/python"
    export PYTHONPATH="${PYTHONPATH}:$HOME/git/elements"
    $apy ../../../../tests/processing_speed/twiss_product.py
fi