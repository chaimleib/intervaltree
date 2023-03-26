#!/bin/bash
# Tests using `python setup.py test` using different versions of python.

this_dir="$(dirname "$0")"
export base_dir="$(dirname "$this_dir")"

set -x
code=0
for ver in $(pyenv versions --bare | sort -V); do
  pyenv global "$ver"
  python --version
  python "$base_dir/setup.py" test || code=1
done
set +x
exit "$code"
