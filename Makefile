.PHONY: lint

lint:
	uv run --locked ruff check .
