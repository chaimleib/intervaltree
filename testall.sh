#!/bin/bash
# Tests using `python setup.py test` using different versions of python.

for python in python{2.6,2.7,3.3,3.4}; do
    $python setup.py test || exit 1
done
    
