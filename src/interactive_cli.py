import logging
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich import box
from src.bot.client import BinanceClient
from src.bot.config import settings
from src.bot.logger import setup_logging
from src.bot.models import OrderInput, OrderSide, OrderType, TimeInForce
from src.bot.services.orders import OrderService
from src.bot.services.symbols import SymbolService

console = Console()

def display_banner():
    banner = """
╔══════════════════════════════════════════════════════════╗
║     Binance Futures Trading Bot - Interactive Mode      ║
║                    Testnet Environment                   ║
╚══════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")

def display_menu():
    table = Table(show_header=False, box=box.ROUNDED, border_style="cyan")
    table.add_column("Option", style="bold yellow", width=10)
    table.add_column("Description", style="white")
    
    table.add_row("1", "Place Market Order")
    table.add_row("2", "Place Limit Order")
    table.add_row("3", "Place Stop Order (with Limit)")
    table.add_row("4", "Check Order Status")
    table.add_row("5", "Cancel Order")
    table.add_row("6", "View Symbol Info")
    table.add_row("7", "Test Connection")
    table.add_row("0", "Exit")
    
    console.print("\n")
    console.print(table)
    console.print("\n")

def place_market_order(order_service: OrderService):
    console.print("\n[bold cyan]═══ Place Market Order ═══[/bold cyan]\n")
    
    symbol = Prompt.ask("Symbol", default="BTCUSDT")
    side = Prompt.ask("Side", choices=["BUY", "SELL"])
    quantity = float(Prompt.ask("Quantity"))
    
    try:
        order = OrderInput(
            symbol=symbol,
            side=side,
            type=OrderType.MARKET,
            quantity=quantity
        )
        
        if Confirm.ask(f"\nConfirm {side} {quantity} {symbol} at MARKET price?"):
            result = order_service.place_order(order, user_interface='terminal')
            console.print("\n[green]✓ Order placed successfully![/green]")
            display_order_result(result)
        else:
            console.print("[yellow]Order cancelled[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")

def place_limit_order(order_service: OrderService):
    console.print("\n[bold cyan]═══ Place Limit Order ═══[/bold cyan]\n")
    
    symbol = Prompt.ask("Symbol", default="BTCUSDT")
    side = Prompt.ask("Side", choices=["BUY", "SELL"])
    quantity = float(Prompt.ask("Quantity"))
    price = float(Prompt.ask("Price"))
    time_in_force = Prompt.ask("Time in Force", choices=["GTC", "IOC", "FOK"], default="GTC")
    
    try:
        order = OrderInput(
            symbol=symbol,
            side=side,
            type=OrderType.LIMIT,
            quantity=quantity,
            price=price,
            timeInForce=time_in_force
        )
        
        if Confirm.ask(f"\nConfirm {side} {quantity} {symbol} at {price} ({time_in_force})?"):
            result = order_service.place_order(order, user_interface='terminal')
            console.print("\n[green]✓ Order placed successfully![/green]")
            display_order_result(result)
        else:
            console.print("[yellow]Order cancelled[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")

def place_stop_limit_order(order_service: OrderService):
    console.print("\n[bold cyan]═══ Place Stop Order (with Limit) ═══[/bold cyan]\n")
    console.print("[dim]STOP order: Triggers at stop price, then places limit order at limit price[/dim]\n")
    
    symbol = Prompt.ask("Symbol", default="BTCUSDT")
    side = Prompt.ask("Side", choices=["BUY", "SELL"])
    quantity = float(Prompt.ask("Quantity"))
    stop_price = float(Prompt.ask("Stop Price (trigger)"))
    limit_price = float(Prompt.ask("Limit Price (execution)"))
    time_in_force = Prompt.ask("Time in Force", choices=["GTC", "IOC", "FOK"], default="GTC")
    
    try:
        order = OrderInput(
            symbol=symbol,
            side=side,
            type=OrderType.STOP,
            quantity=quantity,
            price=limit_price,
            stopPrice=stop_price,
            timeInForce=time_in_force
        )
        
        console.print(f"\n[yellow]Order Summary:[/yellow]")
        console.print(f"  When price reaches [cyan]{stop_price}[/cyan]")
        console.print(f"  Place {side} order for [cyan]{quantity}[/cyan] {symbol}")
        console.print(f"  At limit price [cyan]{limit_price}[/cyan] ({time_in_force})")
        
        if Confirm.ask("\nConfirm this stop order?"):
            result = order_service.place_order(order, user_interface='terminal')
            console.print("\n[green]✓ Order placed successfully![/green]")
            display_order_result(result)
        else:
            console.print("[yellow]Order cancelled[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")

def check_order_status(order_service: OrderService):
    console.print("\n[bold cyan]═══ Check Order Status ═══[/bold cyan]\n")
    
    symbol = Prompt.ask("Symbol", default="BTCUSDT")
    order_id = int(Prompt.ask("Order ID"))
    
    try:
        result = order_service.get_status(symbol, order_id, user_interface='terminal')
        console.print("\n[green]✓ Order found![/green]")
        display_order_result(result)
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")

def cancel_order(order_service: OrderService):
    console.print("\n[bold cyan]═══ Cancel Order ═══[/bold cyan]\n")
    
    symbol = Prompt.ask("Symbol", default="BTCUSDT")
    order_id = int(Prompt.ask("Order ID"))
    
    try:
        if Confirm.ask(f"\nConfirm cancel order {order_id} for {symbol}?"):
            result = order_service.cancel_order(symbol, order_id, user_interface='terminal')
            console.print("\n[green]✓ Order cancelled successfully![/green]")
            display_order_result(result)
        else:
            console.print("[yellow]Cancellation aborted[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")

def view_symbol_info(symbol_service: SymbolService):
    console.print("\n[bold cyan]═══ View Symbol Info ═══[/bold cyan]\n")
    
    symbol = Prompt.ask("Symbol", default="BTCUSDT")
    
    try:
        filters = symbol_service.get_symbol_filters(symbol)
        
        # Create info table
        table = Table(title=f"{symbol} Information", box=box.ROUNDED, border_style="cyan")
        table.add_column("Property", style="yellow")
        table.add_column("Value", style="white")
        
        table.add_row("Status", filters.get('status', 'N/A'))
        table.add_row("Contract Type", filters.get('contractType', 'N/A'))
        table.add_row("Price Precision", str(filters.get('pricePrecision', 'N/A')))
        table.add_row("Quantity Precision", str(filters.get('quantityPrecision', 'N/A')))
        
        # Extract filter info
        for f in filters.get('filters', []):
            if f['filterType'] == 'PRICE_FILTER':
                table.add_row("Min Price", f.get('minPrice', 'N/A'))
                table.add_row("Max Price", f.get('maxPrice', 'N/A'))
                table.add_row("Tick Size", f.get('tickSize', 'N/A'))
            elif f['filterType'] == 'LOT_SIZE':
                table.add_row("Min Quantity", f.get('minQty', 'N/A'))
                table.add_row("Max Quantity", f.get('maxQty', 'N/A'))
                table.add_row("Step Size", f.get('stepSize', 'N/A'))
            elif f['filterType'] == 'MIN_NOTIONAL':
                table.add_row("Min Notional", f.get('notional', 'N/A'))
        
        console.print("\n")
        console.print(table)
        console.print("\n")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")

def test_connection(client: BinanceClient):
    console.print("\n[bold cyan]═══ Test Connection ═══[/bold cyan]\n")
    
    try:
        client.futures_ping()
        console.print("[green]✓ Connection successful! API is reachable.[/green]\n")
    except Exception as e:
        console.print(f"[red]✗ Connection failed: {e}[/red]\n")

def display_order_result(result: dict):
    table = Table(box=box.ROUNDED, border_style="green")
    table.add_column("Field", style="yellow")
    table.add_column("Value", style="white")
    
    important_fields = [
        'orderId', 'symbol', 'status', 'type', 'side', 
        'price', 'stopPrice', 'origQty', 'executedQty', 
        'cumQuote', 'timeInForce', 'updateTime'
    ]
    
    for field in important_fields:
        if field in result:
            table.add_row(field, str(result[field]))
    
    console.print("\n")
    console.print(table)
    console.print("\n")

def main():
    setup_logging(verbose=False)
    
    try:
        client = BinanceClient(settings.api_key, settings.api_secret)
        symbol_service = SymbolService(client)
        order_service = OrderService(client, symbol_service)
        
        display_banner()
        
        while True:
            display_menu()
            choice = Prompt.ask("Select an option", choices=["0", "1", "2", "3", "4", "5", "6", "7"])
            
            if choice == "0":
                console.print("\n[cyan]Goodbye! Happy trading! 👋[/cyan]\n")
                break
            elif choice == "1":
                place_market_order(order_service)
            elif choice == "2":
                place_limit_order(order_service)
            elif choice == "3":
                place_stop_limit_order(order_service)
            elif choice == "4":
                check_order_status(order_service)
            elif choice == "5":
                cancel_order(order_service)
            elif choice == "6":
                view_symbol_info(symbol_service)
            elif choice == "7":
                test_connection(client)
            
            if choice != "0":
                Prompt.ask("\nPress Enter to continue")
                console.clear()
                display_banner()
    
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Interrupted by user[/yellow]\n")
    except Exception as e:
        console.print(f"\n[red]Fatal error: {e}[/red]\n")

if __name__ == "__main__":
    main()
