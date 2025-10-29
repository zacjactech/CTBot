@echo off
REM Batch script for running common commands
REM Usage: run.bat <command>

if "%1"=="" goto help

if "%1"=="install" goto install
if "%1"=="web" goto web
if "%1"=="interactive" goto interactive
if "%1"=="test" goto test
if "%1"=="ping" goto ping
if "%1"=="order-market" goto order-market
if "%1"=="order-limit" goto order-limit
if "%1"=="order-stop" goto order-stop
if "%1"=="db-history" goto db-history
if "%1"=="db-logs" goto db-logs
if "%1"=="db-stats" goto db-stats
if "%1"=="lint" goto lint
if "%1"=="fmt" goto fmt
if "%1"=="help" goto help

echo Unknown command: %1
echo Run 'run.bat help' to see available commands
goto end

:install
echo Installing dependencies...
poetry install
goto end

:web
echo Starting web UI...
poetry run python -m src.web_ui
goto end

:interactive
echo Starting interactive terminal UI...
poetry run python -m src.interactive_cli
goto end

:test
echo Running tests...
poetry run pytest -v
goto end

:ping
echo Testing connection...
poetry run python -m src.cli ping
goto end

:order-market
echo Placing sample market order...
poetry run python -m src.cli order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
goto end

:order-limit
echo Placing sample limit order...
poetry run python -m src.cli order --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.1 --price 2000 --timeInForce GTC
goto end

:order-stop
echo Placing sample stop order...
poetry run python -m src.cli order --symbol BTCUSDT --side BUY --type STOP --quantity 0.001 --price 95000 --stopPrice 94000 --timeInForce GTC
goto end

:db-history
echo Viewing order history...
poetry run python -m src.db_viewer history
goto end

:db-logs
echo Viewing activity logs...
poetry run python -m src.db_viewer logs
goto end

:db-stats
echo Viewing trading statistics...
poetry run python -m src.db_viewer stats
goto end

:lint
echo Linting code...
poetry run ruff check .
goto end

:fmt
echo Formatting code...
poetry run ruff format .
goto end

:help
echo.
echo Available Commands:
echo ==================
echo.
echo Setup:
echo   install          Install dependencies
echo   test             Run tests
echo.
echo Interfaces:
echo   web              Launch web UI (http://localhost:5000)
echo   interactive      Launch interactive terminal UI
echo   ping             Test API connection
echo.
echo Orders:
echo   order-market     Place sample market order
echo   order-limit      Place sample limit order
echo   order-stop       Place sample stop order
echo.
echo Database:
echo   db-history       View order history
echo   db-logs          View activity logs
echo   db-stats         View trading statistics
echo.
echo Development:
echo   lint             Lint code
echo   fmt              Format code
echo.
echo Usage: run.bat ^<command^>
echo Example: run.bat web
echo.
goto end

:end
