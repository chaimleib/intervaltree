#!/bin/bash
# Tests using `python setup.py test` using different versions of python.

this_dir="$(dirname "$0")"
base_dir="$(dirname "$this_dir")"

for ver in $PYTHONS; do
    echo "$ver"
    export PYENV_VERSION="$ver"
    python --version
    python "$base_dir/setup.py" test || exit 1
done
    
