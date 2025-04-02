.PHONY: help lint format check test clean install

help:
	@echo "Available commands:"
	@echo "  make install      - Install development dependencies"
	@echo "  make lint         - Run Ruff linter"
	@echo "  make format       - Run Black formatter"
	@echo "  make check        - Run all checks (Black + Ruff)"
	@echo "  make test         - Run tests"
	@echo "  make clean        - Clean up cache directories"

install:
	poetry install

lint:
	poetry run ruff check .

format:
	poetry run black .

check: format lint

test:
	poetry run pytest

clean:
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .mypy_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} + 