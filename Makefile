.PHONY: install run interactive web test lint fmt order-market order-limit order-stop-limit db-history db-logs db-stats

install:
	poetry install

run:
	poetry run python -m src.main

interactive:
	poetry run python -m src.interactive_cli

web:
	poetry run python -m src.web_ui

test:
	poetry run pytest

lint:
	poetry run ruff check .

fmt:
	poetry run ruff format .

order-market:
	poetry run python -m src.cli order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

order-limit:
	poetry run python -m src.cli order --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.1 --price 2000 --timeInForce GTC

order-stop-limit:
	poetry run python -m src.cli order --symbol BTCUSDT --side BUY --type STOP --quantity 0.001 --price 95000 --stopPrice 94000 --timeInForce GTC

db-history:
	poetry run python -m src.db_viewer history

db-logs:
	poetry run python -m src.db_viewer logs

db-stats:
	poetry run python -m src.db_viewer stats
