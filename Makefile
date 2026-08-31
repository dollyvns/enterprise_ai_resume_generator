.PHONY: install run test lint docker-build docker-run

install:
	python -m pip install -e ".[dev]"

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest -q

lint:
	ruff check .

docker-build:
	docker build -t enterprise-ai-resume-generator:local .

docker-run:
	docker compose up --build
