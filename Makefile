SHELL=bash

SCRIPTS_DIR=$(PWD)/scripts

TEMPS=$(shell find intervaltree/ -type f -name '*.py?')
TEMPS+=$(shell find intervaltree/ -type d -name '__pycache__')
TEMPS+=$(shell find test/ -type f -name '*.py?')
TEMPS+=$(shell find test/ -type d -name '__pycache__')

PYTHONS=$(shell echo {2.6,2.7,3.2,3.3,3.4})

# PyPI server name, as specified in ~/.pypirc
# See http://peterdowns.com/posts/first-time-with-pypi.html
PYPI=pypitest

# first target is default
test:
	"$(SCRIPTS_DIR)/testall.sh"

clean: clean-build clean-eggs clean-temps

clean-build:
	rm -rf dist build

clean-eggs:
	rm -rf *.egg*

clean-temps:
	@[[ "   " == "$(TEMPS)" ]] ||      	\
		(echo 'Removing:' && rm -rfv $(TEMPS))

# Setup for live upload
release:
	PYPI=pypi

# Build source distribution
sdist:
	python setup.py sdist

bdist_wheel:
	for ver in $(PYTHONS); do									\
		if ! python$$ver -c 'import wheel' &>/dev/null; then 	\
			echo;												\
			echo "Error: Python $$ver is missing wheel. Run:";	\
			echo "  make deps-dev";								\
			echo "to install it.";								\
			break;												\
		fi > /dev/stderr;										\
		echo '>>'$$ver;											\
		python$$ver setup.py bdist_wheel || 					\
			echo "Try running \`make deps-dev'";				\
	done

deps-dev:
	for ver in $(PYTHONS); do					\
		echo '>>'$$ver;							\
		pip$(ver) install wheel ||				\
			sudo $(ver) install wheel;			\
	done


.PHONY: clean clean-eggs clean-all test

