SHELL=bash

SCRIPTS_DIR:=$(PWD)/scripts

# any files ending in .py?, and any folders named __pycache__
TEMPS=$(shell                                                   \
	find intervaltree/ test/                                    \
		\( -type f -name '*.py?' ! -path '*/__pycache__/*' \)   \
		-o \( -type d -name '__pycache__' \)                    \
)

PYTHONS:=2.6 2.7 3.2 3.3 3.4
PYTHON_MAJORS:=$(shell          \
	echo "$(PYTHONS)" |         \
	tr ' ' '\n' | cut -d. -f1 | \
	uniq                        \
)

# PyPI server name, as specified in ~/.pypirc
# See http://peterdowns.com/posts/first-time-with-pypi.html
PYPI=pypitest

# default target
all: test

test: pytest rst
	
quicktest: rst
	python setup.py test

pytest: deps-dev
	"$(SCRIPTS_DIR)/testall.sh"

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

# Convert README to rst and check the result
rst: pydocutils pyandoc
	python setup.py check --restructuredtext --strict
	@echo "README is ready for PyPI"

# Register at PyPI
register: rst
	python setup.py register -r $(PYPI)

# Setup for live upload
release:
	$(eval PYPI=pypi)

# Build source distribution
sdist-upload:
	python setup.py sdist upload -r $(PYPI)

deps-dev: pyandoc

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


# for debugging the Makefile
env:
	@echo
	@echo TEMPS="\"$(TEMPS)\""
	@echo PYTHONS="\"$(PYTHONS)\""
	@echo PYTHON_MAJORS="\"$(PYTHON_MAJORS)\""
	@echo PYPI="\"$(PYPI)\""


.PHONY: clean clean-build clean-eggs clean-all test release sdist-upload deps-dev upload env pm-update pydocutils pytest quicktest

