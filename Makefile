# Makefile for Salon Pulse
# Convenience commands for common development tasks

.PHONY: help install install-dev test lint format clean run seed

# Default target
help:
	@echo "Salon Pulse - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install       Install production dependencies"
	@echo "  make install-dev   Install all dependencies (dev + test)"
	@echo ""
	@echo "Development:"
	@echo "  make run           Start Flask development server"
	@echo "  make seed          Generate test data"
	@echo ""
	@echo "Code Quality:"
	@echo "  make format        Format code with Black and isort"
	@echo "  make lint          Run all linters (flake8, pylint, bandit)"
	@echo "  make test          Run pytest with coverage"
	@echo "  make test-watch    Run tests in watch mode"
	@echo ""
	@echo "CI/CD:"
	@echo "  make ci            Run full CI pipeline locally"
	@echo "  make pre-commit    Install pre-commit hooks"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean         Remove generated files and caches"

# Install production dependencies
install:
	pip install --upgrade pip
	pip install -r requirements.txt

# Install all dependencies (dev + test)
install-dev: install
	pip install -r requirements-dev.txt
	pip install -r requirements-test.txt
	pip install pre-commit
	@echo "✅ All dependencies installed"

# Run the Flask application
run:
	python run.py

# Generate test data
seed:
	python scripts/seed_data.py

# Format code with Black and isort
format:
	@echo "🎨 Formatting code..."
	black backend/ scripts/ run.py tests/
	isort backend/ scripts/ run.py tests/
	@echo "✅ Code formatted"

# Run linters
lint:
	@echo "🔍 Running linters..."
	@echo "\n📋 Flake8..."
	flake8 backend/ scripts/ run.py --count --statistics || true
	@echo "\n🔬 Pylint..."
	pylint backend/ scripts/ run.py --exit-zero || true
	@echo "\n🔒 Bandit (security)..."
	bandit -r backend/ scripts/ run.py || true
	@echo "✅ Linting complete"

# Run tests with coverage
test:
	@echo "🧪 Running tests..."
	pytest tests/ -v --cov=backend --cov-report=term-missing --cov-report=html
	@echo "✅ Tests complete. Coverage report: htmlcov/index.html"

# Run tests in watch mode (requires pytest-watch)
test-watch:
	ptw tests/ -- --cov=backend

# Run full CI pipeline locally
ci: format lint test
	@echo "✅ Full CI pipeline complete!"

# Install pre-commit hooks
pre-commit:
	pre-commit install
	@echo "✅ Pre-commit hooks installed"

# Clean generated files
clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf build/
	rm -rf dist/
	rm -f bandit-report.json safety-report.json
	@echo "✅ Cleanup complete"

# Initialize database
init-db:
	python -m backend.models
	@echo "✅ Database initialized"

# Run analytics reports
reports:
	@echo "📊 Running analytics reports..."
	python scripts/analyze.py
	python scripts/customer_report.py

# Full setup from scratch
setup: install-dev pre-commit init-db seed
	@echo "✅ Full setup complete! Run 'make run' to start the app."
