.DEFAULT_GOAL := help

COMPOSE      := docker compose
SERVICE_DEV  := dev
SERVICE_CI   := ci

# ── help ──────────────────────────────────────────────────────────────────────

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── build ─────────────────────────────────────────────────────────────────────

.PHONY: build
build: ## Build the dev image
	$(COMPOSE) build $(SERVICE_DEV)

.PHONY: build-ci
build-ci: ## Build the CI image
	$(COMPOSE) build $(SERVICE_CI)

.PHONY: build-all
build-all: ## Build all images
	$(COMPOSE) build

# ── test ──────────────────────────────────────────────────────────────────────

.PHONY: test
test: ## Run tests inside the CI container
	$(COMPOSE) run --rm $(SERVICE_CI)

.PHONY: test-local
test-local: ## Run tests locally on the host
	python -m pytest tests/ -v --cov=libs/parsing --cov-report=term-missing

.PHONY: test-xml
test-xml: ## Run tests locally and emit coverage.xml
	python -m pytest tests/ -v --cov=libs/parsing --cov-report=xml

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
	$(COMPOSE) run --rm $(SERVICE_DEV) bash

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
	$(COMPOSE) down --remove-orphans
	docker image prune -f