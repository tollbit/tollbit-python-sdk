# Makefile for the Tollbit SDK
# Usage:
#   make test          # run pytest
#   make lint          # style check (Black, no changes)
#   make type          # mypy static type checks
#   make format        # auto-format with Black
#   make all           # lint + type + tests
#   make matrix        # (optional) run nox test matrix if you use it

SHELL := /bin/bash -eo pipefail
.DEFAULT_GOAL := help

# --- variables ---
PACKAGE_NAME := tollbit-python-sdk
DIST_STEM    := $(subst -,_,$(PACKAGE_NAME))
VERSION      := $(shell poetry version -s)
WHEEL        := $(shell ls -t dist/$(DIST_STEM)-$(VERSION)-*.whl 2>/dev/null | head -1)
DRYRUN       ?= true

MAKEFILE_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

# --- paths & commands ---
PY_SRC               := src/tollbit tests
PY_VERS_FILE         := .python-version
TOLLBIT_SPEC_FILES   := .typespec/tsp-output/@typespec/openapi3
GENERATED_MODELS_DIR := src/tollbit/_apis/models/_generated

POETRY   := poetry
PYENV    := pyenv
GIT      := git
PYTEST   := $(POETRY) run pytest
BLACK    := $(POETRY) run black
MYPY     := $(POETRY) run mypy
NOX      := $(POETRY) run nox
PKGINFO  := $(POETRY) run pkginfo

# --- targets ---

.PHONY: help
help: ## Show this help
	@awk 'BEGIN {FS":.*##"; printf "\nTargets:\n"} /^[a-zA-Z_%-]+:.*##/ { printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST); echo

# --- setup ---

.PHONY: install
install: ## Install dependencies into Poetry venv
	xargs -L 1 $(PYENV) install -s < $(PY_VERS_FILE)
	$(POETRY) install --with dev

# -- generate models ---

.PHONY: models
models: clear-models ## Generate Pydantic models from OpenAPI YAMLs under spec/
	@$(POETRY) run python scripts/gen_models.py

.PHONY: clear-models
clear-models: ## Clear generated models
	@rm -rf $(GENERATED_MODELS_DIR)/*

# --- tests and linting ---

.PHONY: test
test: ## Run unit tests (pytest)
	$(PYTEST) -q

.PHONY: lint
lint: ## Check code style with Black (no changes written)
	$(BLACK) --check $(PY_SRC) --exclude '$(GENERATED_MODELS_DIR)'

.PHONY: type
type: ## Static type checks with mypy
	$(MYPY) src/tollbit

.PHONY: format
format: ## Auto-format code with Black
	$(BLACK) $(PY_SRC) --exclude '$(GENERATED_MODELS_DIR)'

.PHONY: clean
clean: ## Remove build artifacts but keep .gitignore files
	@echo "🧹 Cleaning build artifacts..."
	@find dist -mindepth 1 ! -name '.gitignore' -exec rm -rf {} +
	@rm -rf .pytest_cache/ .mypy_cache/ **/*.egg-info
	@echo "✅ Clean complete (kept .gitignore files)"

.PHONY: matrix-tests
matrix-tests: ## Run nox test matrix across Python versions
	$(NOX) -s tests

.PHONY: test-watch
test-watch: ensure-reflex ## Run pytest in watch mode using reflex
	reflex -c .reflex.conf

.PHONY: ensure-reflex
ensure-reflex: ## Ensure reflex is installed in the Poetry venv
	@if ! which reflex > /dev/null 2>&1; then \
	  echo "⚠️ reflex not found in Poetry venv. Run `brew install reflex`"; \
	  exit 1; \
	fi

# --- build steps ---

.PHONY: build
build: ## Build the package (sdist + wheel)
	$(POETRY) build

.PHONY: inspect-meta
inspect-meta: build ## Show wheel metadata for this version using pkginfo
	@if [[ -z "$(WHEEL)" ]]; then \
	  echo "No wheel found for $(DIST_STEM)-$(VERSION)-*.whl. Did build succeed?" >&2; exit 1; \
	fi; \
	echo "=== 📦 Metadata for $(WHEEL) ===:"; \
	$(PKGINFO) "$(WHEEL)"

.PHONY: ensure-changelog
ensure-changelog: ## Ensure CHANGELOG.md has an entry for the current version
	@./scripts/ensure-changelog.sh $(VERSION)

.PHONY: ensure-tag
ensure-tag: ## Ensure git tag exists for the current version
	@./scripts/ensure-git-tag.sh $(VERSION)

.PHONY: publish-test
publish-test: build ## Publish package to Test PyPI
	$(POETRY) publish -r testpypi


.PHONY: publish-live
publish-live: ensure-tag ensure-changelog lint type test clean build ## Publish package to Live PyPI
	@if [ "$(DRYRUN)" = "true" ]; then \
	  echo "🚧 DRY RUN: Skipping actual publish to PyPI. Set DRYRUN=false to publish."; \
	  exit 0; \
	fi; \
	$(POETRY) publish; \
	$(GIT) tag push origin $(VERSION)


# --- defaults ---

.PHONY: all
all: lint type test ## Run lint + type + tests
