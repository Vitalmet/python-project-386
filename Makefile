.PHONY: install dev test lint lint-fix seed openapi

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
