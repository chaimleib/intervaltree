Hacking intervaltree
====================

This is a developer's guide to modifying and maintaining `intervaltree`.

## Dependencies

Before running most `make` commands,
you will need to [install pyenv] and run `make install-devtools`.
This section describes those steps in detail.

### Pyenv

To install pyenv, follow your preferred instructions at
https://github.com/pyenv/pyenv/blob/master/README.md#installation
including

1. running the installer,
2. the modifications to your shell's rc file, and
3. restarting your shell.

### Set up the virtual environments (venv directory)

This section creates the virtual environments necessary for testing `intervaltree`
in all the supported versions of Python, locally.

#### Optional: Compiling Python with third-party libraries

If certain libraries and headers are present,
pyenv will compile the Python interpreters with the associated support.
Note that as we go back in Python version history,
support for the latest libraries declines.
Incompatible libraries will be ignored, rather than break compilation.

If readline is provided, this provides autocomplete and advanced history support
when the interpreters are run interactively.
On systems using `dnf`, readline-devel also includes ncurses-devel.

```bash
apt-get install libreadline-dev libncurses5-dev
# OR
dnf install readline-devel
```

More information about suggested packages is listed at
https://github.com/pyenv/pyenv/wiki#suggested-build-environment

#### Install Python versions and dev tools

To install the Python versions and dev tools:

```bash
make install-devtools
```

This does the following:

1. Uses pyenv to download (and if no binary is hosted, compile)
all the Python interpreters which we test under.
2. Creates Python virtual environments under the venv directory.
3. Installs the needed packages in each venv for testing and deployment.

## Testing

To run the tests in the `test` directory, run

```bash
make test
```

or simply

```bash
make
```

The two commands above run all the available tests on all versions of Python supported.

Running all tests requires that all the supported versions of Python installed.
These can be viewed with `make env`.

### Single version of Python

Run

```bash
make quicktest
```

## Cleaning

To clean up the project directory, run

```bash
make distclean
```

That should remove all the locally-installed dependencies and clear out all the temporary files.
You will need to restore the virtual envs with `make install-devtools`.

To keep the virtual envs, but clean everything else, run

```bash
make clean
```

## Maintainers: Working with PyPI

To publish a new version to Test PyPI, run

```bash
make upload
```

This will run `make test`,
build the source and wheel distributions,
and push them to the PyPI test server.

You can test your deploy in a fresh virtual env:

```bash
python -m venv venv/testpypi
source venv/testpypi/bin/activate
make install-testpypi
python -c 'from intervaltree import IntervalTree; IntervalTree()'
```

If this looks like it went well, run

```bash
make prod upload
```

to push the distribution to the production PyPI server.

You can delete your virtual env when you are done with it:

```bash
rm -rf venv/testpypi
```

## Project structure

### `intervaltree`

The `intervaltree` directory has three main files:

* `intervaltree.py`
* `interval.py`
* `node.py`

`intervaltree.py` and `interval.py` contain the public API to `IntervalTree` and `Interval`. `node.py` contains the internal logic of the tree. For the theory of how this type of tree works, read the following:

* Wikipedia's [Interval tree][Wiki intervaltree] article
* Eternally Confuzzled's tutorial on [AVL balancing][Confuzzled AVL tree]
* Tyler Kahn's simpler, immutable [interval tree implementation][Kahn intervaltree] in Python

### `test`

All files ending with `_test.py` are detected and run whenever you run `make` or `make quicktest`. In those files, only functions beginning with `test_` are executed.

#### `test/data`
Some tests depend on having certain lists of `Interval`s. These are stored in the modules of `test/data`. Most of these modules only contain a `data` attribute, which is a list of tuples that is converted to a list of `Interval`s by `test/intervals.py`. You can access them by importing the dict of lists of `Interval`s `test.intervals.ivs`.

Other tests (like `test/issue25_test.py`) depend on having pre-constructed `IntervalTree`s. These are constructed by `test/intervaltrees.py` and can be accessed by importing `test.intervaltrees.trees`. This is a dict of callables that return `IntervalTree`s.

### Documentation files

* `HACKING.md` is this file.
* `README.md` contains public API documentation and credits.
* `CHANGELOG.md`
* `LICENSE.txt`

### Other code files

* `Makefile` contains convenience routines for managing and testing the project.
* `pyproject.toml` configures how `intervaltree` gets built and deployed.

[brew]: http://brew.sh/
[install pyenv]: https://github.com/pyenv/pyenv/blob/master/README.md#installation
[python.org/downloads]: http://www.python.org/downloads
[Confuzzled AVL tree]: http://www.eternallyconfuzzled.com/tuts/datastructures/jsw_tut_avl.aspx
[Wiki intervaltree]: http://en.wikipedia.org/wiki/Interval_tree
[Kahn intervaltree]: http://zurb.com/forrst/posts/Interval_Tree_implementation_in_python-e0K
