import pytest
from unittest.mock import MagicMock
from src.bot.models import OrderInput, OrderSide, OrderType
from src.bot.services.orders import OrderService

@pytest.fixture
def mock_order_service():
    client = MagicMock()
    symbol_service = MagicMock()
    symbol_service.get_symbol_filters.return_value = {
        "filters": [
            {"filterType": "PRICE_FILTER", "tickSize": "0.01"},
            {"filterType": "LOT_SIZE", "stepSize": "0.001", "minQty": "0.001"},
        ]
    }
    return OrderService(client, symbol_service)

def test_place_limit_order(mock_order_service):
    order = OrderInput(
        symbol="BTCUSDT",
        side=OrderSide.BUY,
        type=OrderType.LIMIT,
        quantity=1.2345,
        price=123.456,
        timeInForce="GTC"
    )
    mock_order_service.place_order(order)
    mock_order_service.client.futures_create_order.assert_called_once_with(
        symbol='BTCUSDT',
        side='BUY',
        type='LIMIT',
        quantity=1.234,
        price=123.46,
        timeInForce='GTC',
        reduceOnly=False
    )

def test_place_market_order(mock_order_service):
    order = OrderInput(
        symbol="BTCUSDT",
        side=OrderSide.SELL,
        type=OrderType.MARKET,
        quantity=0.123
    )
    mock_order_service.place_order(order)
    mock_order_service.client.futures_create_order.assert_called_once_with(
        symbol='BTCUSDT',
        side='SELL',
        type='MARKET',
        quantity=0.123,
        reduceOnly=False
    )

def test_place_stop_order(mock_order_service):
    order = OrderInput(
        symbol="ETHUSDT",
        side=OrderSide.BUY,
        type=OrderType.STOP,
        quantity=0.5,
        price=2000.00,
        stopPrice=1950.00,
        timeInForce="GTC"
    )
    mock_order_service.place_order(order)
    mock_order_service.client.futures_create_order.assert_called_once_with(
        symbol='ETHUSDT',
        side='BUY',
        type='STOP',
        quantity=0.5,
        price=2000.0,
        stopPrice=1950.0,
        timeInForce='GTC',
        reduceOnly=False
    )
