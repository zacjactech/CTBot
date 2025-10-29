import argparse
import logging
from rich.console import Console
from rich.table import Table
from src.bot.client import BinanceClient
from src.bot.config import settings
from src.bot.logger import setup_logging
from src.bot.models import OrderInput, OrderSide, OrderType, TimeInForce
from src.bot.services.orders import OrderService
from src.bot.services.symbols import SymbolService

console = Console()

def main():
    parser = argparse.ArgumentParser(description="Binance Futures Trading Bot")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Order command
    order_parser = subparsers.add_parser("order", help="Place a new order")
    order_parser.add_argument("--symbol", required=True, help="Trading symbol (e.g., BTCUSDT)")
    order_parser.add_argument("--side", required=True, choices=[s.value for s in OrderSide], help="Order side")
    order_parser.add_argument("--type", required=True, choices=[t.value for t in OrderType], help="Order type")
    order_parser.add_argument("--quantity", required=True, type=float, help="Order quantity")
    order_parser.add_argument("--price", type=float, help="Order price (required for LIMIT)")
    order_parser.add_argument("--timeInForce", choices=[t.value for t in TimeInForce], help="Time in force (for LIMIT)")
    order_parser.add_argument("--stopPrice", type=float, help="Stop price (for STOP/TAKE_PROFIT orders)")

    # Status command
    status_parser = subparsers.add_parser("status", help="Query order status")
    status_parser.add_argument("--symbol", required=True, help="Trading symbol")
    status_parser.add_argument("--orderId", required=True, type=int, help="Order ID")

    # Cancel command
    cancel_parser = subparsers.add_parser("cancel", help="Cancel an open order")
    cancel_parser.add_argument("--symbol", required=True, help="Trading symbol")
    cancel_parser.add_argument("--orderId", required=True, type=int, help="Order ID")

    # Symbols command
    symbols_parser = subparsers.add_parser("symbols", help="Show exchange filters for a symbol")
    symbols_parser.add_argument("--symbol", required=True, help="Trading symbol")

    # Ping command
    subparsers.add_parser("ping", help="Check connectivity to Binance API")

    args = parser.parse_args()

    setup_logging(verbose=args.verbose)
    logger = logging.getLogger(__name__)

    try:
        client = BinanceClient(settings.api_key, settings.api_secret)
        symbol_service = SymbolService(client)
        order_service = OrderService(client, symbol_service)

        if args.command == "ping":
            client.futures_ping()
            console.print("[green]Pong! Connectivity is OK.[/green]")

        elif args.command == "symbols":
            filters = symbol_service.get_symbol_filters(args.symbol)
            console.print(filters)

        elif args.command == "order":
            order_input = OrderInput(
                symbol=args.symbol,
                side=args.side,
                type=args.type,
                quantity=args.quantity,
                price=args.price,
                timeInForce=args.timeInForce,
                stopPrice=args.stopPrice,
            )
            result = order_service.place_order(order_input, user_interface='cli')
            console.print(result)

        elif args.command == "status":
            status = order_service.get_status(args.symbol, args.orderId, user_interface='cli')
            console.print(status)

        elif args.command == "cancel":
            result = order_service.cancel_order(args.symbol, args.orderId, user_interface='cli')
            console.print(result)

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        console.print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    main()
