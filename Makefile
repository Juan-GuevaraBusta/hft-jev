.PHONY: help setup lint format typecheck test test-unit

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| sort \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## Create venv and install dependencies (requires uv)
	uv sync

lint: ## Lint: ruff check + ruff format --check
	uv run ruff check .
	uv run ruff format --check .

format: ## Auto-format with ruff
	uv run ruff check --fix .
	uv run ruff format .

typecheck: ## Type-check with mypy (strict mode)
	uv run mypy

test: ## Run unit tests with coverage
	uv run pytest --cov -m unit

test-unit: ## Run unit tests only
	uv run pytest -m unit