.PHONY: install dev test lint format typecheck check clean

PYTHON := python
PIP := $(PYTHON) -m pip

install:
	$(PIP) install -r requirements.txt

dev:
	$(PIP) install -r requirements.txt
	$(PIP) install -e .

test:
	$(PYTHON) -m pytest

test-cov:
	$(PYTHON) -m pytest --cov=src/nexus --cov-report=term-missing

lint:
	ruff check .

format:
	ruff format .

format-check:
	ruff format --check .

typecheck:
	mypy src

check:
	ruff check .
	ruff format --check .
	mypy src
	$(PYTHON) -m pytest

run-api:
	uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000

run-worker:
	$(PYTHON) -m apps.worker.main

clean:
	$(PYTHON) scripts/bootstrap.py --clean