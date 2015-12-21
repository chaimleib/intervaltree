"""
intervaltree: A mutable, self-balancing interval tree for Python 2 and 3.
Queries may be by point, by range overlap, or by range envelopment.

File utilities

Copyright 2013-2015 Chaim-Leib Halbert

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import os

## Filesystem utilities
def read_file(path):
    """Reads file into string."""
    with open(path, 'r') as f:
        data = f.read()
    return data


def mkdir_p(path):
    """Like `mkdir -p` in unix"""
    if not path.strip():
        return
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def rm_f(path):
    """Like `rm -f` in unix"""
    try:
        os.unlink(path)
    except OSError as e:
        if e.errno == errno.ENOENT:
            pass
        else:
            raise


def update_file(path, data):
    """Writes data to path, creating path if it doesn't exist"""
    # delete file if already exists
    rm_f(path)

    # create parent dirs if needed
    parent_dir = os.path.dirname(path)
    if not os.path.isdir(os.path.dirname(parent_dir)):
        mkdir_p(parent_dir)

    # write file
    with open(path, 'w') as f:
        f.write(data)
