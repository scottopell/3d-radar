# Self-Documented Makefile
# https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html

.DEFAULT_GOAL := help

.PHONY: help
help: ## Displays this help page
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: ## Install dependencies
	@python -m pip install -r requirements.txt

.PHONY: format
format: ## Format code
	@python -m black .

.PHONY: test
test: ## Run tests
	@cd src && python -m unittest