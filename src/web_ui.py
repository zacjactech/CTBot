"""
Simple Web UI for Binance Futures Trading Bot
"""
import logging
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from src.bot.client import BinanceClient
from src.bot.config import settings
from src.bot.logger import setup_logging
from src.bot.models import OrderInput, OrderSide, OrderType, TimeInForce
from src.bot.services.orders import OrderService
from src.bot.services.symbols import SymbolService

# Setup
setup_logging(verbose=False)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Services will be initialized on first request
_client = None
_symbol_service = None
_order_service = None

def get_services():
    """Lazy initialization of services"""
    global _client, _symbol_service, _order_service
    
    if _client is None:
        logger.info("Initializing Binance client...")
        _client = BinanceClient(settings.api_key, settings.api_secret)
        _symbol_service = SymbolService(_client)
        _order_service = OrderService(_client, _symbol_service)
        logger.info("Services initialized successfully")
    
    return _client, _symbol_service, _order_service

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/ping', methods=['GET'])
def ping():
    """Test API connectivity"""
    try:
        client, _, _ = get_services()
        client.futures_ping()
        return jsonify({'success': True, 'message': 'Connected to Binance Futures API'})
    except Exception as e:
        logger.error(f"Ping failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/symbols', methods=['GET'])
def get_symbols():
    """Get list of available symbols"""
    try:
        _, symbol_service, _ = get_services()
        exchange_info = symbol_service._exchange_info
        if not exchange_info:
            exchange_info = symbol_service.fetch_exchange_info()
        
        symbols = [s['symbol'] for s in exchange_info.get('symbols', []) if s.get('status') == 'TRADING']
        return jsonify({'success': True, 'symbols': symbols[:50]})  # Return first 50
    except Exception as e:
        logger.error(f"Failed to get symbols: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/symbol/<symbol>', methods=['GET'])
def get_symbol_info(symbol):
    """Get detailed symbol information"""
    try:
        _, symbol_service, _ = get_services()
        filters = symbol_service.get_symbol_filters(symbol)
        
        # Extract key information
        info = {
            'symbol': filters.get('symbol'),
            'status': filters.get('status'),
            'pricePrecision': filters.get('pricePrecision'),
            'quantityPrecision': filters.get('quantityPrecision'),
        }
        
        # Extract filters
        for f in filters.get('filters', []):
            if f['filterType'] == 'PRICE_FILTER':
                info['minPrice'] = f.get('minPrice')
                info['maxPrice'] = f.get('maxPrice')
                info['tickSize'] = f.get('tickSize')
            elif f['filterType'] == 'LOT_SIZE':
                info['minQty'] = f.get('minQty')
                info['maxQty'] = f.get('maxQty')
                info['stepSize'] = f.get('stepSize')
            elif f['filterType'] == 'MIN_NOTIONAL':
                info['minNotional'] = f.get('notional')
        
        return jsonify({'success': True, 'info': info})
    except Exception as e:
        logger.error(f"Failed to get symbol info: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/order', methods=['POST'])
def place_order():
    """Place a new order"""
    try:
        _, _, order_service = get_services()
        data = request.json
        
        # Build order input
        order_data = {
            'symbol': data.get('symbol'),
            'side': data.get('side'),
            'type': data.get('type'),
            'quantity': float(data.get('quantity')),
        }
        
        # Add optional parameters
        if data.get('price'):
            order_data['price'] = float(data.get('price'))
        if data.get('stopPrice'):
            order_data['stopPrice'] = float(data.get('stopPrice'))
        if data.get('timeInForce'):
            order_data['timeInForce'] = data.get('timeInForce')
        
        order = OrderInput(**order_data)
        result = order_service.place_order(order, user_interface='web')
        
        return jsonify({'success': True, 'order': result})
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to place order: {error_msg}")
        
        # Make error messages more user-friendly
        if "Margin is insufficient" in error_msg or "-2019" in error_msg:
            error_msg = "Insufficient margin. Please add more testnet funds to your account."
        elif "notional must be no smaller" in error_msg or "-4164" in error_msg:
            error_msg = "Order value too small. Minimum order value is $100. Increase quantity or price."
        elif "would immediately trigger" in error_msg or "-2021" in error_msg:
            error_msg = "Stop price would trigger immediately. Adjust stop price based on current market price."
        elif "Precision is over the maximum" in error_msg or "-1111" in error_msg:
            error_msg = "Price or quantity has too many decimal places. Check symbol info for correct precision."
        
        return jsonify({'success': False, 'error': error_msg}), 400

@app.route('/api/order/<symbol>/<int:order_id>', methods=['GET'])
def get_order_status(symbol, order_id):
    """Get order status"""
    try:
        _, _, order_service = get_services()
        result = order_service.get_status(symbol, order_id, user_interface='web')
        return jsonify({'success': True, 'order': result})
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to get order status: {error_msg}")
        
        # Make error messages more user-friendly
        if "Unknown order" in error_msg or "-2011" in error_msg:
            error_msg = "Order not found. Please check the Order ID and symbol."
        
        return jsonify({'success': False, 'error': error_msg}), 400

@app.route('/api/order/<symbol>/<int:order_id>', methods=['DELETE'])
def cancel_order(symbol, order_id):
    """Cancel an order"""
    try:
        _, _, order_service = get_services()
        logger.info(f"Attempting to cancel order {order_id} for {symbol}")
        result = order_service.cancel_order(symbol, order_id, user_interface='web')
        logger.info(f"Order cancelled successfully: {result}")
        return jsonify({'success': True, 'order': result})
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to cancel order {order_id} for {symbol}: {error_msg}")
        
        # Make error messages more user-friendly
        if "Unknown order" in error_msg or "-2011" in error_msg:
            error_msg = "Order not found. It may have already been filled, cancelled, or the Order ID is incorrect."
        elif "Invalid symbol" in error_msg:
            error_msg = "Invalid trading symbol."
        
        return jsonify({'success': False, 'error': error_msg}), 400

@app.route('/api/price/<symbol>', methods=['GET'])
def get_current_price(symbol):
    """Get current market price for a symbol"""
    try:
        client, _, _ = get_services()
        ticker = client.client.futures_symbol_ticker(symbol=symbol)
        return jsonify({
            'success': True, 
            'symbol': symbol,
            'price': float(ticker['price'])
        })
    except Exception as e:
        logger.error(f"Failed to get price: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/history', methods=['GET'])
def get_order_history():
    """Get order history from database"""
    try:
        from src.bot.database import get_database
        db = get_database()
        
        symbol = request.args.get('symbol')
        limit = int(request.args.get('limit', 50))
        
        orders = db.get_order_history(symbol=symbol, limit=limit)
        
        history = []
        for order in orders:
            history.append({
                'id': order.id,
                'orderId': order.order_id,
                'symbol': order.symbol,
                'side': order.side,
                'type': order.order_type,
                'quantity': order.quantity,
                'price': order.price,
                'stopPrice': order.stop_price,
                'status': order.status,
                'executedQty': order.executed_qty,
                'avgPrice': order.avg_price,
                'createdAt': order.created_at.isoformat() if order.created_at else None,
                'updatedAt': order.updated_at.isoformat() if order.updated_at else None
            })
        
        return jsonify({'success': True, 'history': history})
    except Exception as e:
        logger.error(f"Failed to get history: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get trading statistics"""
    try:
        from src.bot.database import get_database
        db = get_database()
        
        stats = db.get_statistics()
        
        return jsonify({'success': True, 'statistics': stats})
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/logs', methods=['GET'])
def get_activity_logs():
    """Get activity logs"""
    try:
        from src.bot.database import get_database
        db = get_database()
        
        limit = int(request.args.get('limit', 50))
        logs = db.get_activity_logs(limit=limit)
        
        activity = []
        for log in logs:
            activity.append({
                'id': log.id,
                'timestamp': log.timestamp.isoformat() if log.timestamp else None,
                'action': log.action,
                'symbol': log.symbol,
                'orderId': log.order_id,
                'status': log.status,
                'message': log.message,
                'errorDetails': log.error_details,
                'userInterface': log.user_interface
            })
        
        return jsonify({'success': True, 'logs': activity})
    except Exception as e:
        logger.error(f"Failed to get logs: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def main():
    """Run the web server"""
    print("\n" + "="*60)
    print("🌐 Binance Futures Trading Bot - Web UI")
    print("="*60)
    print(f"\n✓ Server starting on http://localhost:5000")
    print(f"✓ Connected to: {settings.base_url}")
    print(f"\n📝 Open your browser and navigate to: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()
