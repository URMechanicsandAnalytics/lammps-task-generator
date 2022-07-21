# .PHONY: run clean
.PHONY: all clean

VENV = venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip
SHELL = /bin/bash

# run: $(VENV)/bin/activate
# 	$(PYTHON) test.py

# $(VENV)/bin/activate: requirements.txt
# 	. /etc/profile.d/modules.sh; \
# 	module load python3/3.10.5b; \
# 	python3 -m venv $(VENV)
# 	$(PIP) install -r requirements.txt

.ONESHELL:
all:
	@chmod u+x ./RUN.sh
	@chmod u+x ./RESET.sh
	@. /etc/profile.d/modules.sh; \
	@module load python3/3.10.5b; \
	@python3 -m venv $(VENV)
	@source $(VENV)/bin/activate
	@$(PIP) install -r requirements.txt
	@./RUN.sh

clean: 
	@echo Deleting the virtual environment...
	@rm -rf src/__pycache__
	@rm -rf $(VENV)

reset:
	@echo Resetting the directory...
	@rm -rf src/__pycache__
	@rm -rf $(VENV)
	@./RESET.sh
