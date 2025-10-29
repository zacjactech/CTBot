# PowerShell script for running common commands
# Usage: .\run.ps1 <command>

param(
    [Parameter(Mandatory=$true)]
    [string]$Command
)

switch ($Command) {
    "install" {
        Write-Host "Installing dependencies..." -ForegroundColor Cyan
        poetry install
    }
    "web" {
        Write-Host "Starting web UI..." -ForegroundColor Cyan
        poetry run python -m src.web_ui
    }
    "interactive" {
        Write-Host "Starting interactive terminal UI..." -ForegroundColor Cyan
        poetry run python -m src.interactive_cli
    }
    "test" {
        Write-Host "Running tests..." -ForegroundColor Cyan
        poetry run pytest -v
    }
    "ping" {
        Write-Host "Testing connection..." -ForegroundColor Cyan
        poetry run python -m src.cli ping
    }
    "order-market" {
        Write-Host "Placing sample market order..." -ForegroundColor Cyan
        poetry run python -m src.cli order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
    }
    "order-limit" {
        Write-Host "Placing sample limit order..." -ForegroundColor Cyan
        poetry run python -m src.cli order --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.1 --price 2000 --timeInForce GTC
    }
    "order-stop" {
        Write-Host "Placing sample stop order..." -ForegroundColor Cyan
        poetry run python -m src.cli order --symbol BTCUSDT --side BUY --type STOP --quantity 0.001 --price 95000 --stopPrice 94000 --timeInForce GTC
    }
    "db-history" {
        Write-Host "Viewing order history..." -ForegroundColor Cyan
        poetry run python -m src.db_viewer history
    }
    "db-logs" {
        Write-Host "Viewing activity logs..." -ForegroundColor Cyan
        poetry run python -m src.db_viewer logs
    }
    "db-stats" {
        Write-Host "Viewing trading statistics..." -ForegroundColor Cyan
        poetry run python -m src.db_viewer stats
    }
    "lint" {
        Write-Host "Linting code..." -ForegroundColor Cyan
        poetry run ruff check .
    }
    "fmt" {
        Write-Host "Formatting code..." -ForegroundColor Cyan
        poetry run ruff format .
    }
    "help" {
        Write-Host @"

Available Commands:
==================

Setup:
  install          Install dependencies
  test             Run tests

Interfaces:
  web              Launch web UI (http://localhost:5000)
  interactive      Launch interactive terminal UI
  ping             Test API connection

Orders:
  order-market     Place sample market order
  order-limit      Place sample limit order
  order-stop       Place sample stop order

Database:
  db-history       View order history
  db-logs          View activity logs
  db-stats         View trading statistics

Development:
  lint             Lint code
  fmt              Format code

Usage: .\run.ps1 <command>
Example: .\run.ps1 web

"@ -ForegroundColor Yellow
    }
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Write-Host "Run '.\run.ps1 help' to see available commands" -ForegroundColor Yellow
    }
}
