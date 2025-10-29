from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator

class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderType(str, Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"
    TAKE_PROFIT = "TAKE_PROFIT"
    TAKE_PROFIT_LIMIT = "TAKE_PROFIT_LIMIT"
    STOP_MARKET = "STOP_MARKET"
    TAKE_PROFIT_MARKET = "TAKE_PROFIT_MARKET"

class TimeInForce(str, Enum):
    GTC = "GTC"  # Good 'Til Canceled
    IOC = "IOC"  # Immediate or Cancel
    FOK = "FOK"  # Fill or Kill

class OrderInput(BaseModel):
    symbol: str
    side: OrderSide
    type: OrderType
    quantity: float = Field(..., gt=0)
    price: float | None = None
    timeInForce: TimeInForce | None = None
    stopPrice: float | None = None
    reduceOnly: bool = False

    @model_validator(mode='after')
    def validate_order_params(self):
        # LIMIT orders require price
        if self.type == OrderType.LIMIT and self.price is None:
            raise ValueError("Price is required for LIMIT orders")
        
        # LIMIT orders default to GTC
        if self.type == OrderType.LIMIT and self.timeInForce is None:
            self.timeInForce = TimeInForce.GTC
        
        # STOP and TAKE_PROFIT with limit price require both price and stopPrice
        if self.type in [OrderType.STOP, OrderType.TAKE_PROFIT]:
            if self.stopPrice is None:
                raise ValueError(f"stopPrice is required for {self.type.value} orders")
            # If price is provided, it's a limit order after trigger
            if self.price is not None and self.timeInForce is None:
                self.timeInForce = TimeInForce.GTC
        
        # STOP_LIMIT and TAKE_PROFIT_LIMIT require both price and stopPrice
        if self.type in [OrderType.STOP_LIMIT, OrderType.TAKE_PROFIT_LIMIT]:
            if self.price is None:
                raise ValueError(f"Price is required for {self.type.value} orders")
            if self.stopPrice is None:
                raise ValueError(f"stopPrice is required for {self.type.value} orders")
            if self.timeInForce is None:
                self.timeInForce = TimeInForce.GTC
        
        # STOP_MARKET and TAKE_PROFIT_MARKET require only stopPrice
        if self.type in [OrderType.STOP_MARKET, OrderType.TAKE_PROFIT_MARKET] and self.stopPrice is None:
            raise ValueError("stopPrice is required for STOP_MARKET/TAKE_PROFIT_MARKET orders")
        
        return self
