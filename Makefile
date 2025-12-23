SHELL=bash

# any files ending in .py?, and any folders named __pycache__
TEMPS=$(shell                                                   \
	find intervaltree test                                    \
		\( -type f -name '*.py?' ! -path '*/__pycache__/*' \)   \
		-o \( -type d -name '__pycache__' \)                    \
)

PYTHON_MINORS:=$(shell echo 2.7 3.{5..14})
PYTHONS:=$(shell echo $(PYTHON_MINORS) | xargs -n1 pyenv latest -k)
MAINPY=$(shell echo $(PYTHONS) | tr ' ' '\n' | tail -n1)
MAINPYMINOR=$(shell echo $(PYTHON_MINORS) | tr ' ' '\n' | tail -n1)

# PyPI server name, as specified in ~/.pypirc
# See http://peterdowns.com/posts/first-time-with-pypi.html
PYPI=pypitest

# default target
all: test

test: pytest flake8

quicktest:
	source venv/mainpy$(MAINPY)/bin/activate
	python -m pytest

coverage:
	pytest --cov=intervaltree
	coverage html | sed -E 's@(Wrote HTML report to) (.*)@\1 file://'"$$PWD"'/\2@'

pytest:
	unset anyerr; \
	for pyver in $(PYTHONS); do \
		echo "pytest in Python $${pyver}"; \
		pyminor=$${pyver%.*}; \
		if ! source venv/py$${pyminor}/bin/activate; then \
			echo "Failed to activate" >&2; \
			anyerr=y; \
			continue; \
		fi; \
		>/dev/null echo "Python 2.7 sends version to stderr instead of stdout"; \
		if [[ "$$(python$${pyminor} --version 2>&1)" != *"Python $${pyver}" ]]; then \
			echo "venv does not have Python $${pyver} installed" >&2; \
			anyerr=y; \
			continue; \
		fi; \
		if ! python$${pyminor} -m pytest; then \
			echo "Pytest failed" >&2; \
			anyerr=y; \
			continue; \
		fi; \
	done; \
	if [ -n "$$anyerr" ]; then exit 1; fi

flake8:
	source venv/mainpy$(MAINPYMINOR)/bin/activate || exit 1
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --extend-exclude=venv,requirements,dist
	# flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

clean: clean-build clean-eggs clean-temps

distclean: clean clean-env

clean-build:
	rm -rf dist build htmlcov

clean-eggs:
	rm -rf *.egg* .eggs/

clean-env:
	rm -rf venv

clean-temps:
	rm -rf $(TEMPS)

install-testpypi:
	pip install \
		--no-cache-dir \
		--index-url https://test.pypi.org/simple/ \
		--extra-index-url https://pypi.org/simple \
		intervaltree

install-pypi:
	pip install intervaltree

install-develop:
	pip install -e .

uninstall:
	pip uninstall intervaltree sortedcontainers

# Setup for live upload
release:
	$(eval PYPI=pypi)

# Build dist distribution
build: clean
	source venv/mainpy$(MAINPYMINOR)/bin/activate || exit 1
	python$(MAINPYMINOR) -m hatch build

upload: test build
	source venv/mainpy$(MAINPYMINOR)/bin/activate || exit 1
	if [[ "$(PYPI)" == pypitest ]]; then \
		python$(MAINPYMINOR) -m twine upload --verbose -r testpypi dist/*; \
	else \
		python$(MAINPYMINOR) -m twine upload --verbose dist/*; \
	fi

install-devtools: pyenv-install-main-env pyenv-install-envs

pyenv-is-installed:
	pyenv --version &>/dev/null || (echo "ERROR: pyenv not installed" && false)

pyenv-install-main-env: pyenv-is-installed
	@# echo N: Do not recompile a python interpreter if it is already present.
	echo N | pyenv install $(MAINPY) || true
	@echo "Setting up venv for main Python version $(MAINPY)"
	export PYENV_VERSION=$(MAINPY)
	unset CFLAGS;
	python$(MAINPYMINOR) -m venv venv/mainpy$(MAINPYMINOR) || exit 1
	source venv/mainpy$(MAINPYMINOR)/bin/activate || exit 1
	pip$(MAINPYMINOR) install -U pip || exit 1
	pip$(MAINPYMINOR) install -r requirements/flake8.txt
	pip$(MAINPYMINOR) install -r requirements/pytest.txt || exit 1
	pip$(MAINPYMINOR) install -U hatch hatchling twine
	@echo "Finished setting up venv for main Python $(MAINPY)"

pyenv-install-envs: pyenv-is-installed
	@# echo N: Do not recompile a python interpreter if it is already present.
	for pyver in $(PYTHONS); do echo N | pyenv install $$pyver || true; done
	@# Setup virtual environments.
	@# venv only works on Python 3.3 and later. It will not work for 2.7.
	@# So, use virtualenv for 2.7.
	for pyver in $(PYTHONS); do \
		echo ""; \
		echo "Setting up venv for Python $${pyver}"; \
		export PYENV_VERSION=$$pyver; \
		pyminor=$${pyver%.*}; \
		unset CFLAGS; \
		if [[ "$$pyver" == 2.* ]]; then \
			export CFLAGS=" -std=c17"; \
			pip$${pyminor} install virtualenv || continue; \
			python$${pyminor} -m virtualenv \
				--python=python$${pyminor} \
				venv/py$${pyminor} || continue; \
			source venv/py$${pyminor}/bin/activate || continue; \
		else \
			python$${pyminor} -m venv venv/py$${pyminor} || continue; \
			source venv/py$${pyminor}/bin/activate || continue; \
		fi; \
		pip$${pyminor} install -U pip || continue; \
		pip$${pyminor} install -r requirements/pytest.txt || continue; \
		echo "Finished setting up venv for Python $${pyver}"; \
	done

pyenv-uninstall-envs:
	rm -rf venv

pyenv-uninstall-versions:
	for pyver in $(PYTHONS); do (echo y | pyenv uninstall $$pyver) || true; done

# for debugging the Makefile
env:
	@echo
	@echo TEMPS="\"$(TEMPS)\""
	@echo PYTHONS="\"$(PYTHONS)\""
	@echo PYTHON_MINORS="\"$(PYTHON_MINORS)\""
	@echo MAINPY="\"$(MAINPY)\""
	@echo MAINPYMINOR="\"$(MAINPYMINOR)\""
	@echo PYENV_VERSION="\"$(PYENV_VERSION)\""
	@echo PYPI="\"$(PYPI)\""


.PHONY: all \
	build \
	clean \
	clean-build \
	clean-eggs \
	clean-temps \
	coverage \
	distclean \
	env \
	flake8 \
	install-develop \
	install-devtools \
	install-pypi \
	install-testpypi \
	pyenv-install-envs \
	pyenv-install-main-env \
	pyenv-is-installed \
	pyenv-uninstall-envs \
	pyenv-uninstall-versions \
	pytest \
	quicktest \
	release \
	test \
	uninstall \
	upload

