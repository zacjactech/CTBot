import logging
from functools import wraps
from binance import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from src.bot.config import settings

logger = logging.getLogger(__name__)

def log_io(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} returned {result}")
            return result
        except (BinanceAPIException, BinanceRequestException) as e:
            logger.error(f"API Error in {func.__name__}: {e}")
            raise
    return wrapper

@log_io
def create_client(api_key: str, api_secret: str) -> Client:
    client = Client(api_key, api_secret)
    
    # Try with /fapi suffix first as it's required for most endpoints
    base_url = settings.base_url
    if not base_url.endswith('/fapi'):
        base_url = f"{base_url}/fapi"
    
    client.FUTURES_URL = base_url
    
    # Verify connectivity
    try:
        client.futures_ping()
        logger.info(f"Connected to Binance Futures at {base_url}")
    except BinanceAPIException as e:
        if e.code == -1021:  # Timestamp error, but means endpoint is correct
            logger.warning("Timestamp error, but endpoint is reachable")
        else:
            logger.error(f"Failed to connect: {e}")
            raise

    return client

class BinanceClient:
    def __init__(self, api_key: str, api_secret: str):
        self.client = create_client(api_key, api_secret)

    @log_io
    def futures_exchange_info(self):
        result = self.client.futures_exchange_info()
        logger.debug(f"Exchange info result type: {type(result)}")
        if isinstance(result, dict):
            logger.debug(f"Exchange info keys: {list(result.keys())}")
        return result

    @log_io
    def futures_create_order(self, **params):
        return self.client.futures_create_order(**params)

    @log_io
    def futures_get_order(self, **params):
        return self.client.futures_get_order(**params)

    @log_io
    def futures_cancel_order(self, **params):
        return self.client.futures_cancel_order(**params)

    @log_io
    def futures_ping(self):
        return self.client.futures_ping()
