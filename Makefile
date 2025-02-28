.PHONY: install test lint format clean setup pre-commit run-ui debug-cleanup docs docs-check

# Project settings
PROJECT_NAME = research_agent
PYTHON = pipenv run python
PYTEST = pipenv run pytest
PYTEST_FLAGS = -v
SOURCE_DIR = src
TESTS_DIR = tests
DOCS_DIR = docs

# Install dependencies
install:
	pipenv install -e .

# Install dependencies for development
install-dev:
	pipenv install -e ".[dev]"

# Run tests
test:
	$(PYTEST) $(PYTEST_FLAGS) $(TESTS_DIR)

# Run a specific test file
test-file:
	$(PYTEST) $(PYTEST_FLAGS) $(TESTS_DIR)/$(file)

# Run linters
lint:
	pipenv run isort $(SOURCE_DIR) $(TESTS_DIR)
	pipenv run black $(SOURCE_DIR) $(TESTS_DIR)
	pipenv run flake8 $(SOURCE_DIR) $(TESTS_DIR)
	pipenv run mypy $(SOURCE_DIR)
	pipenv run bandit -r $(SOURCE_DIR)

# Run formatters
format:
	pipenv run isort $(SOURCE_DIR) $(TESTS_DIR)
	pipenv run black $(SOURCE_DIR) $(TESTS_DIR)

# Run security checks
security:
	pipenv run bandit -r $(SOURCE_DIR)

# Clean up Python cache files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete

# Clean up debugging artifacts
debug-cleanup:
	$(PYTHON) scripts/clean_debug.py src

# Clean up debugging artifacts and fix automatically
debug-cleanup-fix:
	$(PYTHON) scripts/clean_debug.py src --fix

# Set up pre-commit hooks
pre-commit:
	pipenv run pip install pre-commit
	pipenv run pre-commit install

# Run the Streamlit UI
run-ui:
	$(PYTHON) -m src.main ui

# Documentation targets
docs:
	@echo "Checking for documentation updates..."
	@test -d $(DOCS_DIR) || mkdir -p $(DOCS_DIR)
	@test -d $(DOCS_DIR)/images || mkdir -p $(DOCS_DIR)/images

# Check for documentation issues
docs-check:
	@echo "Checking documentation files..."
	@find $(DOCS_DIR) -name "*.md" -exec grep -l "TODO" {} \; | xargs -r echo "TODO items found in:"
	@find $(DOCS_DIR) -name "*.md" -exec grep -l "(Coming Soon)" {} \; | xargs -r echo "Coming Soon items found in:"
	@find $(DOCS_DIR) -name "*.md" -exec grep -l "FIXME" {} \; | xargs -r echo "FIXME items found in:"

# Run all quality checks
quality: format lint security test debug-cleanup docs-check

# Setup development environment
setup: install-dev pre-commit
	@echo "Development environment setup complete. Use 'make quality' to run all checks." 