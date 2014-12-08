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


# first target is default
test: deps-dev
	"$(SCRIPTS_DIR)/testall.sh"

clean: clean-build clean-eggs clean-temps

distclean: clean clean-deps

clean-build:
	rm -rf dist build

clean-eggs:
	rm -rf *.egg* .eggs/

clean-deps:
	rm -rf pyandoc
	rm -f pandoc

clean-temps:
	rm -rf $(TEMPS)

# Setup for live upload
release:
	$(eval PYPI=pypi)

# Build source distribution
sdist-upload:
	python setup.py sdist upload -r $(PYPI)

bdist_wheel-upload:
	for ver in $(PYTHON_MAJORS); do                              \
		if ! python$$ver -c 'import wheel' &>/dev/null; then     \
			echo;                                                \
			echo "Error: Python $$ver is missing wheel. Run:";   \
			echo "  make deps-dev";                              \
			echo "to install it.";                               \
			break;                                               \
		fi > /dev/stderr;                                        \
		echo '>>'$$ver;                                          \
		python$$ver setup.py bdist_wheel upload -r $(PYPI);      \
	done

deps-dev: pyandoc

pyandoc: pandoc-bin
	[[ -d pyandoc/pandoc ]] || git clone --depth=50 git://github.com/chaimleib/pyandoc.git
	[[ "`readlink pandoc`" == "pyandoc/pandoc" ]] || ln -s pyandoc/pandoc pandoc
	# $(eval PYPKG=pyandoc)
	# for ver in $(PYTHONS); do                          \
	#     echo '>>'$$ver;                                \
	#     pip$(ver) install --upgrade $(PYPKG) ||        \
	#         sudo $(ver) install --upgrade $(PYPKG);    \
	# done

pandoc-bin: pm-update
	brew install pandoc || sudo apt-get install pandoc
	
pywheel:
	$(eval PYPKG=wheel)
	for ver in $(PYTHONS); do                          \
		echo '>>'$$ver;                                \
		pip$(ver) install --upgrade $(PYPKG) ||        \
			sudo $(ver) install --upgrade $(PYPKG);    \
	done

pm-update:
	brew update || sudo apt-get update
	
# Uploads to test server, unless the release target was run too
upload: test clean sdist-upload bdist_wheel-upload


# for debugging the Makefile
env:
	@echo
	@echo TEMPS="\"$(TEMPS)\""
	@echo PYTHONS="\"$(PYTHONS)\""
	@echo PYTHON_MAJORS="\"$(PYTHON_MAJORS)\""
	@echo PYPI="\"$(PYPI)\""


.PHONY: clean clean-build clean-eggs clean-all test release sdist-upload bdist_wheel-upload deps-dev pywheel upload env pm-update

