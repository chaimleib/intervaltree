SHELL=bash

SCRIPTS_DIR=$(PWD)/scripts

TEMPS=$(shell find intervaltree/ -type f -name '*.py?')
TEMPS+=$(shell find intervaltree/ -type d -name '__pycache__')
TEMPS+=$(shell find test/ -type f -name '*.py?')
TEMPS+=$(shell find test/ -type d -name '__pycache__')

PYTHONS=$(shell echo {2.6,2.7,3.2,3.3,3.4})
PYTHON_MAJORS=$(shell 							\
	echo "$(PYTHONS)" | 						\
	tr ' ' '\n' | cut -d. -f1 | 				\
	uniq 										\
)

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
	rm -rf *.egg* .eggs/

clean-temps:
	@[[ "   " == "$(TEMPS)" ]] ||      	\
		(echo 'Removing:' && rm -rfv $(TEMPS))

# Setup for live upload
release:
	PYPI=pypi

# Build source distribution
sdist-upload:
	python setup.py sdist upload -r $(PYPI)

bdist_wheel-upload:
	for ver in $(PYTHON_MAJORS); do								\
		if ! python$$ver -c 'import wheel' &>/dev/null; then 	\
			echo;												\
			echo "Error: Python $$ver is missing wheel. Run:";	\
			echo "  make deps-dev";								\
			echo "to install it.";								\
			break;												\
		fi > /dev/stderr;										\
		echo '>>'$$ver;											\
		python$$ver setup.py bdist_wheel upload -r $(PYPI);		\
	done

deps-dev:
	for ver in $(PYTHON_MAJORS); do					\
		echo '>>'$$ver;							\
		pip$(ver) install wheel ||				\
			sudo $(ver) install --upgrade wheel;			\
	done

# Uploads to test server, unless the release target was run too
upload: test clean sdist-upload bdist_wheel-upload


# for debugging the Makefile
env:
	@echo TEMPS="\"$(TEMPS)\""
	@echo PYTHONS="\"$(PYTHONS)\""
	@echo PYTHON_MAJORS="\"$(PYTHON_MAJORS)\""
	@echo PYPI="\"$(PYPI)\""

.PHONY: clean clean-eggs clean-all test

