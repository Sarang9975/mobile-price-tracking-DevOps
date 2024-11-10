# Makefile for Mobile Price Predictor
.PHONY: help install test run clean deploy

help: ## Show this help message
	@echo "Mobile Price Predictor - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install pytest pytest-cov black flake8

test: ## Run tests
	python -m pytest test_app.py -v

test-cov: ## Run tests with coverage
	python -m pytest test_app.py --cov=. --cov-report=html

run: ## Run the application
	python app.py

run-dev: ## Run the application in development mode
	export FLASK_DEBUG=True && python app.py

deploy: ## Deploy the application
	python deploy.py

clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/

format: ## Format code with black
	black *.py

lint: ## Lint code with flake8
	flake8 *.py

check: format lint test ## Run all checks (format, lint, test)

docker-build: ## Build Docker image
	docker build -t mobile-price-predictor .

docker-run: ## Run Docker container
	docker run -p 80:80 mobile-price-predictor 