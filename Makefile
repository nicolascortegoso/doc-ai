.DEFAULT_GOAL := help

COMPOSE_DEV  := docker compose -f docker-compose.yml -f docker-compose.dev.yml
COMPOSE_CI   := docker compose -f docker-compose.yml -f docker-compose.ci.yml

# ── help ──────────────────────────────────────────────────────────────────────

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── build ─────────────────────────────────────────────────────────────────────

.PHONY: build
build: ## Build the dev image
	$(COMPOSE_DEV) build app

.PHONY: build-ci
build-ci: ## Build the CI image
	$(COMPOSE_CI) build app

.PHONY: build-all
build-all: ## Build all images
	$(COMPOSE_DEV) build app
	$(COMPOSE_CI) build app

# ── test ──────────────────────────────────────────────────────────────────────

.PHONY: test
test: ## Run tests inside the CI container
	$(COMPOSE_CI) run --rm app

.PHONY: test-local
test-local: ## Run tests locally on the host
	python -m pytest tests/ -v --cov=libs --cov-report=term-missing

.PHONY: test-xml
test-xml: ## Run tests locally and emit coverage.xml
	python -m pytest tests/ -v --cov=libs --cov-report=xml

# ── lint / format ─────────────────────────────────────────────────────────────

.PHONY: lint
lint: ## Run ruff linter
	ruff check libs/ tests/

.PHONY: lint-fix
lint-fix: ## Run ruff linter and apply auto-fixes
	ruff check --fix libs/ tests/

.PHONY: format
format: ## Run ruff formatter
	ruff format libs/ tests/

.PHONY: format-check
format-check: ## Check formatting without modifying files
	ruff format --check libs/ tests/

# ── dev shell ─────────────────────────────────────────────────────────────────

.PHONY: shell
shell: ## Drop into a shell inside the dev container
	$(COMPOSE_DEV) run --rm app bash

# ── install ───────────────────────────────────────────────────────────────────

.PHONY: install
install: ## Install all dependencies locally (including dev)
	uv pip install -e ".[dev]"

# ── clean ─────────────────────────────────────────────────────────────────────

.PHONY: clean
clean: ## Remove Python cache files and coverage artefacts
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete
	find . -type f -name "coverage.xml" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +

.PHONY: clean-docker
clean-docker: ## Remove stopped containers and dangling images
	$(COMPOSE_DEV) down --remove-orphans
	$(COMPOSE_CI) down --remove-orphans
	docker image prune -f