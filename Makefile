SHELL=bash

SCRIPTS_DIR=$(PWD)/scripts

TEMPS=$(shell find intervaltree/ -type f -name '*.py?')
TEMPS+=$(shell find intervaltree/ -type d -name '__pycache__')
TEMPS+=$(shell find test/ -type f -name '*.py?')
TEMPS+=$(shell find test/ -type d -name '__pycache__')

clean:
	@[[ "   " == "$(TEMPS)" ]] &&      	\
		echo No temps to delete	||			\
		(echo 'Removing:' && rm -rfv $(TEMPS))

clean-eggs:
	rm -rf *.egg*

clean-all: clean-eggs clean

test:
	"$(SCRIPTS_DIR)/testall.sh"

.PHONY: clean clean-eggs clean-all test

