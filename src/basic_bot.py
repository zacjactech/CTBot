from binance import Client
from src.bot.config import get_settings
from src.bot.models import OrderSide, OrderType, TimeInForce

class BasicBot:
    def __init__(self, api_key, api_secret, testnet=True):
        self.client = Client(api_key, api_secret)
        if testnet:
            settings = get_settings()
            self.client.FUTURES_URL = settings.base_url

    def place_order(
        self,
        symbol: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: float,
        price: float = None,
        timeInForce: TimeInForce = TimeInForce.GTC,
        stopPrice: float = None,
        reduceOnly: bool = False,
    ):
        params = {
            "symbol": symbol,
            "side": side.value,
            "type": order_type.value,
            "quantity": quantity,
            "reduceOnly": reduceOnly
        }
        if price:
            params["price"] = price
        if timeInForce:
            params["timeInForce"] = timeInForce.value
        if stopPrice:
            params["stopPrice"] = stopPrice

        return self.client.futures_create_order(**params)

    def get_order_status(self, symbol: str, orderId: int = None, origClientOrderId: str = None):
        params = {"symbol": symbol}
        if orderId:
            params["orderId"] = orderId
        if origClientOrderId:
            params["origClientOrderId"] = origClientOrderId
        return self.client.futures_get_order(**params)

    def cancel_order(self, symbol: str, orderId: int = None, origClientOrderId: str = None):
        params = {"symbol": symbol}
        if orderId:
            params["orderId"] = orderId
        if origClientOrderId:
            params["origClientOrderId"] = origClientOrderId
        return self.client.futures_cancel_order(**params)
