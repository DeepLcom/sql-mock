.DEFAULT_GOAL := help
SHELL := /bin/bash

.PHONY: help
help: ## Show all available commands
	@awk 'BEGIN {FS = ":.*##"; printf "Usage: make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-13s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST);

.PHONY: lint
lint: ## Lint code with flake8
	poetry run flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics # stop the build if there are Python syntax errors or undefined names
	poetry run flake8 . --count --exit-zero --max-complexity=10 --max-line-length=119 --statistics --ignore E203,E266,E501,W503 # exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide

.PHONY: test
test: ## Run test pipeline
	poetry run pytest tests/

.PHONY: test-integration
test-integration: ## Run integration tests
	poetry run pytest -m "integration" tests/

.PHONY: test-unit
test-unit: ## Run unit tests
	poetry run pytest -m "not integration" tests/