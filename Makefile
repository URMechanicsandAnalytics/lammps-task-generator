.PHONY: all clean reset

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
	@chmod u+x ./bin/RUN.sh
	@chmod u+x ./bin/RESET.sh
	@chmod u+x ./submit
	@chmod u+x ./compress
	@. /etc/profile.d/modules.sh; \
	module load python3/3.10.5b; \
	python3 -m venv $(VENV)
	@source $(VENV)/bin/activate
	@$(PIP) install -r ./src/requirements.txt
	@./bin/RUN.sh

clean: 
	@echo Deleting the virtual environment...
	@rm -rf src/__pycache__
	@rm -rf $(VENV)

reset:
	@echo Resetting the directory...
	@chmod u-x compress
	@chmod u-x submit
	@rm -rf src/__pycache__
	@rm -rf $(VENV)
	@./bin/RESET.sh
