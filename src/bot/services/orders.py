import logging
from typing import Any, Dict
from src.bot.client import BinanceClient
from src.bot.models import OrderInput
from src.bot.services.symbols import SymbolService
from src.bot.validators import validate_and_normalize_order_params
from src.bot.database import get_database

logger = logging.getLogger(__name__)

class OrderService:
    def __init__(self, client: BinanceClient, symbol_service: SymbolService):
        self.client = client
        self.symbol_service = symbol_service
        self.db = get_database()

    def place_order(self, order: OrderInput, user_interface: str = 'cli') -> Dict[str, Any]:
        filters = self.symbol_service.get_symbol_filters(order.symbol)

        params = order.model_dump(exclude_none=True, mode='python')
        
        # Convert enum values to strings
        if 'side' in params:
            params['side'] = params['side'].value if hasattr(params['side'], 'value') else params['side']
        if 'type' in params:
            params['type'] = params['type'].value if hasattr(params['type'], 'value') else params['type']
        if 'timeInForce' in params:
            params['timeInForce'] = params['timeInForce'].value if hasattr(params['timeInForce'], 'value') else params['timeInForce']

        validated_params = validate_and_normalize_order_params(params, filters)

        logger.info(f"Placing order with params: {validated_params}")
        
        try:
            result = self.client.futures_create_order(**validated_params)
            
            # Save to database
            self.db.save_order(validated_params, result)
            
            # Log activity
            self.db.log_activity(
                action='place_order',
                status='success',
                symbol=validated_params.get('symbol'),
                order_id=result.get('orderId'),
                message=f"Order placed: {validated_params.get('type')} {validated_params.get('side')}",
                user_interface=user_interface
            )
            
            return result
        except Exception as e:
            # Log error
            self.db.log_activity(
                action='place_order',
                status='error',
                symbol=validated_params.get('symbol'),
                message=f"Failed to place order",
                error_details=str(e),
                user_interface=user_interface
            )
            raise

    def get_status(self, symbol: str, orderId: int, user_interface: str = 'cli') -> Dict[str, Any]:
        logger.info(f"Getting status for orderId: {orderId}")
        
        try:
            result = self.client.futures_get_order(symbol=symbol, orderId=orderId)
            
            # Update database
            self.db.update_order_status(str(orderId), result)
            
            # Log activity
            self.db.log_activity(
                action='check_status',
                status='success',
                symbol=symbol,
                order_id=orderId,
                message=f"Status checked: {result.get('status')}",
                user_interface=user_interface
            )
            
            return result
        except Exception as e:
            # Log error
            self.db.log_activity(
                action='check_status',
                status='error',
                symbol=symbol,
                order_id=orderId,
                message=f"Failed to check status",
                error_details=str(e),
                user_interface=user_interface
            )
            raise

    def cancel_order(self, symbol: str, orderId: int, user_interface: str = 'cli') -> Dict[str, Any]:
        logger.info(f"Cancelling orderId: {orderId}")
        
        try:
            result = self.client.futures_cancel_order(symbol=symbol, orderId=orderId)
            
            # Update database
            self.db.update_order_status(str(orderId), result)
            
            # Log activity
            self.db.log_activity(
                action='cancel_order',
                status='success',
                symbol=symbol,
                order_id=orderId,
                message=f"Order cancelled",
                user_interface=user_interface
            )
            
            return result
        except Exception as e:
            # Log error
            self.db.log_activity(
                action='cancel_order',
                status='error',
                symbol=symbol,
                order_id=orderId,
                message=f"Failed to cancel order",
                error_details=str(e),
                user_interface=user_interface
            )
            raise
