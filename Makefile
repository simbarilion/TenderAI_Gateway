.PHONY: lint format run seed

lint:
	poetry run ruff check .

format:
	poetry run ruff format .
	poetry run ruff check . --fix

run:
	poetry run uvicorn app.main:app --reload

seed:
	poetry run seed
