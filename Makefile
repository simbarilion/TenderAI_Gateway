.PHONY: lint format ci run seed

lint:
	poetry run ruff check .

format:
	poetry run ruff format .
	poetry run ruff check . --fix

ci:
	poetry run ruff check .
	poetry run ruff format --check .

run:
	poetry run uvicorn app.main:app --reload

seed:
	poetry run seed
