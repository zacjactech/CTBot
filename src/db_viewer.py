"""
Database viewer CLI for viewing order history and logs
"""
import argparse
from rich.console import Console
from rich.table import Table
from rich import box
from src.bot.database import get_database

console = Console()

def view_history(symbol=None, limit=20):
    """View order history"""
    db = get_database()
    orders = db.get_order_history(symbol=symbol, limit=limit)
    
    if not orders:
        console.print("[yellow]No orders found in database[/yellow]")
        return
    
    table = Table(title=f"Order History{f' - {symbol}' if symbol else ''}", box=box.ROUNDED)
    table.add_column("ID", style="cyan")
    table.add_column("Order ID", style="yellow")
    table.add_column("Symbol", style="green")
    table.add_column("Side", style="blue")
    table.add_column("Type", style="magenta")
    table.add_column("Qty", style="white")
    table.add_column("Price", style="white")
    table.add_column("Status", style="bold")
    table.add_column("Created", style="dim")
    
    for order in orders:
        status_color = {
            'NEW': 'yellow',
            'FILLED': 'green',
            'CANCELED': 'red',
            'PARTIALLY_FILLED': 'blue'
        }.get(order.status, 'white')
        
        table.add_row(
            str(order.id),
            str(order.order_id),
            order.symbol,
            order.side,
            order.order_type,
            f"{order.quantity:.4f}",
            f"{order.price:.2f}" if order.price else "MARKET",
            f"[{status_color}]{order.status}[/{status_color}]",
            order.created_at.strftime("%Y-%m-%d %H:%M:%S") if order.created_at else "N/A"
        )
    
    console.print(table)

def view_logs(limit=20):
    """View activity logs"""
    db = get_database()
    logs = db.get_activity_logs(limit=limit)
    
    if not logs:
        console.print("[yellow]No logs found in database[/yellow]")
        return
    
    table = Table(title="Activity Logs", box=box.ROUNDED)
    table.add_column("ID", style="cyan")
    table.add_column("Timestamp", style="dim")
    table.add_column("Action", style="yellow")
    table.add_column("Symbol", style="green")
    table.add_column("Order ID", style="blue")
    table.add_column("Status", style="bold")
    table.add_column("Interface", style="magenta")
    table.add_column("Message", style="white")
    
    for log in logs:
        status_color = 'green' if log.status == 'success' else 'red'
        
        table.add_row(
            str(log.id),
            log.timestamp.strftime("%Y-%m-%d %H:%M:%S") if log.timestamp else "N/A",
            log.action,
            log.symbol or "-",
            str(log.order_id) if log.order_id else "-",
            f"[{status_color}]{log.status}[/{status_color}]",
            log.user_interface or "-",
            log.message or "-"
        )
    
    console.print(table)

def view_statistics():
    """View trading statistics"""
    db = get_database()
    stats = db.get_statistics()
    
    table = Table(title="Trading Statistics", box=box.ROUNDED, show_header=False)
    table.add_column("Metric", style="yellow bold")
    table.add_column("Value", style="cyan bold")
    
    table.add_row("Total Orders", str(stats['total_orders']))
    table.add_row("Filled Orders", f"[green]{stats['filled_orders']}[/green]")
    table.add_row("Cancelled Orders", f"[red]{stats['cancelled_orders']}[/red]")
    table.add_row("Pending Orders", f"[yellow]{stats['pending_orders']}[/yellow]")
    table.add_row("Success Rate", f"{stats['success_rate']:.2f}%")
    
    console.print(table)

def main():
    parser = argparse.ArgumentParser(description="Database Viewer for Trading Bot")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # History command
    history_parser = subparsers.add_parser("history", help="View order history")
    history_parser.add_argument("--symbol", help="Filter by symbol")
    history_parser.add_argument("--limit", type=int, default=20, help="Number of records to show")
    
    # Logs command
    logs_parser = subparsers.add_parser("logs", help="View activity logs")
    logs_parser.add_argument("--limit", type=int, default=20, help="Number of records to show")
    
    # Stats command
    subparsers.add_parser("stats", help="View trading statistics")
    
    args = parser.parse_args()
    
    try:
        if args.command == "history":
            view_history(symbol=args.symbol, limit=args.limit)
        elif args.command == "logs":
            view_logs(limit=args.limit)
        elif args.command == "stats":
            view_statistics()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    main()
