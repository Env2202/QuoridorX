# QuoridorX - Development Makefile
# Usage:
#   make help
#   make bootstrap
#   make run

PYTHON ?= python
VENV_DIR ?= .venv
REQ_FILE ?= requirements.txt

ifeq ($(OS),Windows_NT)
	VENV_BIN := $(VENV_DIR)/Scripts
	VENV_PYTHON := $(VENV_BIN)/python.exe
	ACTIVATE_PATH := $(VENV_BIN)/activate
	PLATFORM_NAME := windows
else
	VENV_BIN := $(VENV_DIR)/bin
	VENV_PYTHON := $(VENV_BIN)/python
	ACTIVATE_PATH := $(VENV_BIN)/activate
	PLATFORM_NAME := linux
endif

.PHONY: help info venv install install-dev bootstrap upgrade-pip run test test-unit test-pytest lint check format clean deep-clean activate-linux activate-windows check-venv

help:
	@echo "QuoridorX development commands"
	@echo ""
	@echo "Setup:"
	@echo "  make bootstrap        Create venv, upgrade pip, install deps"
	@echo "  make venv             Create virtual environment at $(VENV_DIR)"
	@echo "  make install          Install dependencies from $(REQ_FILE)"
	@echo "  make install-dev      Install dependencies + optional dev requirements"
	@echo ""
	@echo "Run and quality:"
	@echo "  make run              Run game app (src/app.py) in venv"
	@echo "  make test             Run tests (pytest if available, fallback to unittest)"
	@echo "  make lint             Run optional linters if installed (ruff, flake8)"
	@echo "  make check            Run lint + test (recommended before PR)"
	@echo "  make format           Run optional formatter if installed (black)"
	@echo ""
	@echo "Environment helpers:"
	@echo "  make activate-linux   Print Linux/macOS venv activation command"
	@echo "  make activate-windows Print Windows venv activation command"
	@echo "  make info             Show current config"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean            Remove Python cache files"
	@echo "  make deep-clean       Remove cache files and venv"

info:
	@echo "Platform: $(PLATFORM_NAME)"
	@echo "Python:   $(PYTHON)"
	@echo "Venv dir: $(VENV_DIR)"
	@echo "Venv py:  $(VENV_PYTHON)"
	@echo "Req file: $(REQ_FILE)"

venv:
	@echo "Creating virtual environment in $(VENV_DIR)"
	@$(PYTHON) -m venv "$(VENV_DIR)"
	@echo "Done."

upgrade-pip: check-venv
	@echo "Upgrading pip/setuptools/wheel inside $(VENV_DIR)"
	@"$(VENV_PYTHON)" -m pip install --upgrade pip setuptools wheel

install: check-venv
	@echo "Installing dependencies from $(REQ_FILE)"
	@"$(VENV_PYTHON)" -m pip install -r "$(REQ_FILE)"

install-dev: install
	@echo "Checking optional development requirements files..."
	@if [ -f requirements-dev.txt ]; then \
		echo "Installing requirements-dev.txt"; \
		"$(VENV_PYTHON)" -m pip install -r requirements-dev.txt; \
	elif [ -f requirements_dev.txt ]; then \
		echo "Installing requirements_dev.txt"; \
		"$(VENV_PYTHON)" -m pip install -r requirements_dev.txt; \
	else \
		echo "No dev requirements file found. Skipping."; \
	fi

bootstrap: venv upgrade-pip install
	@echo "Bootstrap complete."
	@echo "To activate (Linux/macOS): source $(ACTIVATE_PATH)"
	@echo "To activate (Windows PowerShell): .\\$(VENV_DIR)\\Scripts\\Activate.ps1"
	@echo "To activate (Windows CMD): $(VENV_DIR)\\Scripts\\activate.bat"

check-venv:
	@if [ ! -f "$(VENV_PYTHON)" ]; then \
		echo "Virtual environment not found. Run: make venv"; \
		exit 1; \
	fi

run: check-venv
	@"$(VENV_PYTHON)" src/app.py

test: check-venv
	@echo "Running tests..."
	@if "$(VENV_PYTHON)" -m pytest --version >/dev/null 2>&1; then \
		"$(VENV_PYTHON)" -m pytest; \
	elif [ -d tests ]; then \
		"$(VENV_PYTHON)" -m unittest discover -s tests -p "test*.py"; \
	else \
		echo "No tests directory and pytest not installed. Nothing to run."; \
	fi

test-pytest: check-venv
	@"$(VENV_PYTHON)" -m pytest

test-unit: check-venv
	@"$(VENV_PYTHON)" -m unittest discover -s tests -p "test*.py"

lint: check-venv
	@echo "Running lint checks (if tools are installed)..."
	@if "$(VENV_PYTHON)" -m ruff --version >/dev/null 2>&1; then \
		"$(VENV_PYTHON)" -m ruff check src; \
	else \
		echo "ruff not installed, skipping."; \
	fi
	@if "$(VENV_PYTHON)" -m flake8 --version >/dev/null 2>&1; then \
		"$(VENV_PYTHON)" -m flake8 src; \
	else \
		echo "flake8 not installed, skipping."; \
	fi

check: lint test
	@echo "Quality checks complete."

format: check-venv
	@if "$(VENV_PYTHON)" -m black --version >/dev/null 2>&1; then \
		"$(VENV_PYTHON)" -m black src; \
	else \
		echo "black not installed, skipping."; \
	fi

activate-linux:
	@echo "Linux/macOS activation command:"
	@echo "source $(VENV_DIR)/bin/activate"

activate-windows:
	@echo "Windows PowerShell activation command:"
	@echo ".\\$(VENV_DIR)\\Scripts\\Activate.ps1"
	@echo ""
	@echo "Windows CMD activation command:"
	@echo "$(VENV_DIR)\\Scripts\\activate.bat"

clean:
	@echo "Removing Python cache files..."
	@find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete

deep-clean: clean
	@echo "Removing virtual environment..."
	@rm -rf "$(VENV_DIR)"
