#!/bin/bash
# Tests using `python setup.py test` using different versions of python.

this_dir="$(dirname "$0")"
base_dir="$(dirname "$this_dir")"

for python in python{2.6,2.7,3.2,3.3,3.4}; do
    $python "$base_dir/setup.py" test || exit 1
done
    
