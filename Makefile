# Alexandria Transit AI Agent - Makefile

.PHONY: help install install-dev test test-otp run-web run-cli clean format lint type-check setup

# Default target
help:
	@echo "Alexandria Transit AI Agent - Available Commands:"
	@echo ""
	@echo "  setup       - Set up development environment"
	@echo "  install     - Install production dependencies"
	@echo "  install-dev - Install development dependencies"
	@echo "  test        - Run all tests"
	@echo "  test-otp    - Test OTP connection"
	@echo "  run-web     - Start web interface"
	@echo "  run-cli     - Start command line interface"
	@echo "  format      - Format code with black"
	@echo "  lint        - Run flake8 linting"
	@echo "  type-check  - Run mypy type checking"
	@echo "  clean       - Clean up temporary files"
	@echo "  help        - Show this help message"

# Set up development environment
setup:
	@echo "Setting up development environment..."
	python -m venv venv
	@echo "Virtual environment created. Activate it with:"
	@echo "  source venv/bin/activate  # On macOS/Linux"
	@echo "  venv\\Scripts\\activate     # On Windows"
	@echo ""
	@echo "Then run: make install-dev"

# Install production dependencies
install:
	@echo "Installing production dependencies..."
	pip install -r requirements.txt

# Install development dependencies
install-dev:
	@echo "Installing development dependencies..."
	pip install -r requirements.txt
	pip install -e .[dev]

# Run all tests
test:
	@echo "Running tests..."
	python test_final.py

# Test OTP connection
test-otp:
	@echo "Testing OTP connection..."
	python test_otp.py

# Start web interface
run-web:
	@echo "Starting web interface..."
	@echo "Open your browser and go to: http://localhost:5000"
	python web_interface.py

# Start command line interface
run-cli:
	@echo "Starting command line interface..."
	python agent.py

# Format code with black
format:
	@echo "Formatting code with black..."
	black .

# Run flake8 linting
lint:
	@echo "Running flake8 linting..."
	flake8 .

# Run mypy type checking
type-check:
	@echo "Running mypy type checking..."
	mypy .

# Clean up temporary files
clean:
	@echo "Cleaning up temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	@echo "Cleanup complete!"

# Development workflow
dev: format lint type-check test
	@echo "Development checks completed!"

# Full test suite
test-all: test test-otp
	@echo "All tests completed!"

# Quick start
quick-start: install
	@echo "Quick start setup complete!"
	@echo "Next steps:"
	@echo "1. Copy env_example.txt to .env"
	@echo "2. Add your Gemini API key to .env"
	@echo "3. Run: make run-web"
