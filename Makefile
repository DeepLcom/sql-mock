.DEFAULT_GOAL := help
SHELL := /bin/bash

.PHONY: help
help: ## Show all available commands
	@awk 'BEGIN {FS = ":.*##"; printf "Usage: make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-13s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST);

.PHONY: test
test: ## Run test pipeline
	poetry run pytest tests/

.PHONY: test-integration
test-integration: ## Run integration tests
	poetry run pytest -m "integration" tests/

.PHONY: test-unit
test-unit: ## Run unit tests
	poetry run pytest -m "not integration" tests/