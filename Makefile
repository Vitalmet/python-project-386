.PHONY: install dev test lint lint-fix seed openapi frontend-install frontend-dev frontend-build

install:
	poetry install

dev:
	poetry run flask --app calendar_app --debug run

test:
	poetry run pytest

lint:
	poetry run ruff check .

lint-fix:
	poetry run ruff check . --fix

seed:
	poetry run flask --app calendar_app seed

openapi:
	cd typespec && npx tsp compile .

frontend-install:
	cd frontend && npm install

frontend-dev:
	cd frontend && npm run dev

frontend-build:
	cd frontend && npm run build
