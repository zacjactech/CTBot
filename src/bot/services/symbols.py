import json
import logging
from typing import Any, Dict
from src.bot.client import BinanceClient

logger = logging.getLogger(__name__)

CACHE_FILE = "exchange_info.json"

class SymbolService:
    def __init__(self, client: BinanceClient):
        self.client = client
        self._exchange_info = None
        self._load_cache()

    def _load_cache(self):
        try:
            with open(CACHE_FILE, "r") as f:
                self._exchange_info = json.load(f)
                logger.info("Loaded exchange info from cache.")
        except (FileNotFoundError, json.JSONDecodeError):
            logger.info("Cache not found or invalid, will fetch from API.")
            self._exchange_info = None

    def _save_cache(self):
        if self._exchange_info:
            with open(CACHE_FILE, "w") as f:
                json.dump(self._exchange_info, f)
                logger.info("Saved exchange info to cache.")

    def fetch_exchange_info(self) -> Dict[str, Any]:
        logger.info("Fetching exchange info from API...")
        self._exchange_info = self.client.futures_exchange_info()
        logger.debug(f"Exchange info response type: {type(self._exchange_info)}, keys: {list(self._exchange_info.keys()) if isinstance(self._exchange_info, dict) else 'not a dict'}")
        self._save_cache()
        return self._exchange_info

    def get_symbol_filters(self, symbol: str) -> Dict[str, Any]:
        if not self._exchange_info:
            self.fetch_exchange_info()

        if 'symbols' not in self._exchange_info:
            raise ValueError(f"Invalid exchange info structure: {list(self._exchange_info.keys())}")
        
        for s in self._exchange_info['symbols']:
            if s['symbol'] == symbol:
                return s
        raise ValueError(f"Symbol {symbol} not found in exchange info.")
