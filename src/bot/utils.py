import decimal

def format_price(price, tick_size):
    """Format price to match tick size."""
    tick_size = decimal.Decimal(str(tick_size))
    return decimal.Decimal(str(price)).quantize(tick_size)

def format_quantity(quantity, step_size):
    """Format quantity to match step size."""
    step_size = decimal.Decimal(str(step_size))
    return decimal.Decimal(str(quantity)).quantize(step_size)
