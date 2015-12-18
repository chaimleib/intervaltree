SHELL=bash

SCRIPTS_DIR:=$(PWD)/scripts

# any files ending in .py?, and any folders named __pycache__
TEMPS=$(shell                                                   \
	find intervaltree/ test/                                    \
		\( -type f -name '*.py?' ! -path '*/__pycache__/*' \)   \
		-o \( -type d -name '__pycache__' \)                    \
)

PYTHONS:=2.6.9 2.7.11 3.2.6 3.3.6 3.4.3 3.5.1
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

test: pytest rst
	
quicktest: rst
	PYPI=$(PYPI) python setup.py test

coverage:
	coverage run --source=intervaltree setup.py develop test
	coverage report
	coverage html

pytest: deps-dev
	PYTHONS="$(PYTHONS)" PYTHON_MINORS="$(PYTHON_MINORS)" "$(SCRIPTS_DIR)/testall.sh"

clean: clean-build clean-eggs clean-temps

distclean: clean clean-deps

clean-build:
	rm -rf dist build

clean-eggs:
	rm -rf *.egg* .eggs/

clean-deps:
	rm -rf pyandoc docutils bin
	rm -f pandoc

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

# Convert README to rst and check the result
rst: pydocutils pyandoc
	PYPI=$(PYPI) python setup.py check --restructuredtext
	@echo "README is ready for PyPI"

# Register at PyPI
register: rst
	PYPI=$(PYPI) python setup.py register -r $(PYPI)

# Setup for live upload
release:
	$(eval PYPI=pypi)

# Build source distribution
sdist-upload:
	PYPI=$(PYPI) python setup.py sdist upload -r $(PYPI)

deps-ci: pyandoc

deps-dev: pyandoc pyenv-install-versions

pyandoc: pandoc-bin
	[[ -d pyandoc/pandoc ]] || git clone --depth=50 git://github.com/chaimleib/pyandoc.git
	[[ "`readlink pandoc`" == "pyandoc/pandoc" ]] || ln -s pyandoc/pandoc pandoc

pandoc-bin: pm-update
	pandoc -h &>/dev/null || brew install pandoc &>/dev/null || sudo apt-get install pandoc
	
pydocutils:
	$(eval PYPKG=docutils)
	python -c 'import $(PYPKG)' &>/dev/null ||       \
		pip install --upgrade $(PYPKG) ||            \
		pip install --upgrade --install-options="--install-purelib='$(PWD)'" docutils
	
pm-update:
	pandoc -h &>/dev/null || brew update &>/dev/null || sudo apt-get update
	
# Uploads to test server, unless the release target was run too
upload: test clean sdist-upload

pyenv-is-installed:
	pyenv --version || echo "ERROR: pyenv not installed" && false

pyenv-install-versions: pyenv-is-installed
	for pyver in $(PYTHONS); do echo N | pyenv install $$pyver || true; done
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
	clean-deps \
	clean-temps \
	install-testpypi \
	install-pypi \
	install-develop \
	pyenv-install-versions \
	pyenv-is-installed \
	uninstall \
	rst \
	register \
	release \
	sdist-upload \
	deps-ci \
	deps-dev \
	pyandoc \
	pandoc-bin \
	pydocutils \
	pm-update \
	upload \
	env

