#!/bin/bash
# Tests using `python setup.py test` using different versions of python.

this_dir="$(dirname "$0")"
export base_dir="$(dirname "$this_dir")"

function testWithPython() {
    ver="$1"
    export PYENV_VERSION="$ver"
    python --version
    python "$base_dir/setup.py" test || exit 1
}
export -f testWithPython
parallel testWithPython ::: $PYTHONS
    
