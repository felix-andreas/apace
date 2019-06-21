#!/usr/bin/env bash
set -e # exit when any command fails
BUILD_DIR=../shared_objects/
mkdir -p $BUILD_DIR


for file in "$@"; do
    if [[ $file != *.c ]]; then
        echo $file is not a c source file!
        continue
    fi

    if [[ $file == *parallel.c ]]; then
       options='-fopenmp'
    fi

    gcc $options -Ofast -shared -Wl,-soname,cfunc -fPIC $file -o $(basename $file .c).so
    echo $file compiled with $options!

done
