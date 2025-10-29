from typing import Any, Dict
from src.bot.utils import format_price, format_quantity

def validate_and_normalize_order_params(
    params: Dict[str, Any], filters: Dict[str, Any]
) -> Dict[str, Any]:
    """Validate and normalize order parameters against exchange filters."""
    # Price validation (for LIMIT orders)
    if 'price' in params and params['price'] is not None:
        price_filter = next((f for f in filters['filters'] if f['filterType'] == 'PRICE_FILTER'), None)
        if price_filter:
            tick_size = price_filter['tickSize']
            params['price'] = float(format_price(params['price'], tick_size))

    # Quantity validation
    lot_size_filter = next((f for f in filters['filters'] if f['filterType'] == 'LOT_SIZE'), None)
    if lot_size_filter:
        step_size = lot_size_filter['stepSize']
        min_qty = float(lot_size_filter['minQty'])
        if params['quantity'] < min_qty:
            raise ValueError(f"Quantity {params['quantity']} is less than minQty {min_qty}")
        params['quantity'] = float(format_quantity(params['quantity'], step_size))

    return params
