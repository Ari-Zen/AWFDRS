.PHONY: help install dev-install clean test lint format docker-up docker-down migrate seed run

help:
	@echo "AWFDRS Development Commands"
	@echo "============================"
	@echo "install          - Install production dependencies"
	@echo "dev-install      - Install development dependencies"
	@echo "clean            - Clean build artifacts and caches"
	@echo "test             - Run tests with coverage"
	@echo "test-integration - Run integration tests only"
	@echo "lint             - Run linters (ruff, mypy)"
	@echo "format           - Format code with black"
	@echo "docker-up        - Start Docker services (postgres, redis)"
	@echo "docker-down      - Stop Docker services"
	@echo "migrate          - Run database migrations"
	@echo "seed             - Seed database with initial data"
	@echo "init-db          - Initialize database (create tables)"
	@echo "run              - Run development server"
	@echo "shell            - Open Python shell with app context"

install:
	pip install -r requirements.txt

dev-install:
	pip install -r requirements.txt -r requirements-dev.txt

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -f .coverage

test:
	pytest -v --cov --cov-report=term-missing --cov-report=html

test-integration:
	pytest -v -m integration

lint:
	ruff check src/ tests/
	mypy src/

format:
	black src/ tests/ scripts/
	ruff check --fix src/ tests/

docker-up:
	docker-compose up -d postgres redis
	@echo "Waiting for services to be ready..."
	@sleep 5

docker-down:
	docker-compose down

migrate:
	alembic upgrade head

migrate-create:
	alembic revision --autogenerate -m "$(message)"

init-db:
	python scripts/init_db.py

seed:
	python scripts/seed_data.py

run:
	uvicorn src.awfdrs.main:app --reload --host 0.0.0.0 --port 8000

shell:
	python -i -c "import asyncio; from src.awfdrs.db.session import AsyncSessionLocal; from src.awfdrs.db.models import *"

setup: docker-up init-db seed
	@echo "Setup complete! Database initialized and seeded."

reset-db: docker-down docker-up init-db seed
	@echo "Database reset complete!"
