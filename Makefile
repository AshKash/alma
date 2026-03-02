.PHONY: install dev test lint format

install:
	cd backend && uv sync

dev:
	cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	cd backend && uv run pytest -v

lint:
	cd backend && uv run ruff check .

format:
	cd backend && uv run ruff format .
