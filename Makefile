SHELL=bash

SCRIPTS_DIR:=$(PWD)/scripts

# any files ending in .py?, and any folders named __pycache__
TEMPS=$(shell                                                   \
	find intervaltree test                                    \
		\( -type f -name '*.py?' ! -path '*/__pycache__/*' \)   \
		-o \( -type d -name '__pycache__' \)                    \
)

PYTHONS:=2.7.14 3.4.3 3.5.4 3.6.3
PYTHON_MAJORS:=$(shell        \
	echo "$(PYTHONS)" |         \
	tr ' ' '\n' | cut -d. -f1 | \
	uniq                        \
)
PYTHON_MINORS:=$(shell          \
	echo "$(PYTHONS)" |           \
	tr ' ' '\n' | cut -d. -f1,2 | \
	uniq                          \
)

# PyPI server name, as specified in ~/.pypirc
# See http://peterdowns.com/posts/first-time-with-pypi.html
PYPI=pypitest

# default target
all: test

test: pytest
	
quicktest:
	PYPI=$(PYPI) python setup.py test

coverage:
	coverage run --source=intervaltree setup.py develop test
	coverage report
	coverage html

pytest: deps-dev
	PYTHONS="$(PYTHONS)" PYTHON_MINORS="$(PYTHON_MINORS)" "$(SCRIPTS_DIR)/testall.sh"

clean: clean-build clean-eggs clean-temps

distclean: clean

clean-build:
	rm -rf dist build

clean-eggs:
	rm -rf *.egg* .eggs/

clean-temps:
	rm -rf $(TEMPS)

install-testpypi:
	pip install --pre -i https://testpypi.python.org/pypi intervaltree

install-pypi:
	pip install intervaltree

install-develop:
	PYPI=$(PYPI) python setup.py develop
	
uninstall:
	pip uninstall intervaltree

# Register at PyPI
register:
	PYPI=$(PYPI) python setup.py register -r $(PYPI)

# Setup for live upload
release:
	$(eval PYPI=pypi)

# Build source distribution
sdist-upload:
	PYPI=$(PYPI) python setup.py sdist upload -r $(PYPI)

deps-dev: pyenv-install-versions

# Uploads to test server, unless the release target was run too
upload: test clean sdist-upload

pyenv-is-installed:
	pyenv --version &>/dev/null || (echo "ERROR: pyenv not installed" && false)

pyenv-install-versions: pyenv-is-installed
	for pyver in $(PYTHONS); do (echo N | pyenv install $$pyver) || true; done
	for pyver in $(PYTHONS); do export PYENV_VERSION=$$pyver; pip install -U pip; pip install -U pytest; done
	pyenv rehash

# for debugging the Makefile
env:
	@echo
	@echo TEMPS="\"$(TEMPS)\""
	@echo PYTHONS="\"$(PYTHONS)\""
	@echo PYTHON_MAJORS="\"$(PYTHON_MAJORS)\""
	@echo PYTHON_MINORS="\"$(PYTHON_MINORS)\""
	@echo PYPI="\"$(PYPI)\""


.PHONY: all \
	test \
	quicktest \
	pytest \
	clean \
	distclean \
	clean-build \
	clean-eggs \
	clean-temps \
	install-testpypi \
	install-pypi \
	install-develop \
	pyenv-install-versions \
	pyenv-is-installed \
	uninstall \
	register \
	release \
	sdist-upload \
	deps-ci \
	deps-dev \
	pm-update \
	upload \
	env

