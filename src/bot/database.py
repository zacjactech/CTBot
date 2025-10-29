"""
Database module for storing order history and logs
"""
import logging
from datetime import datetime
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

logger = logging.getLogger(__name__)

Base = declarative_base()

class OrderHistory(Base):
    """Order history table"""
    __tablename__ = 'order_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String, nullable=False, index=True)
    symbol = Column(String, nullable=False, index=True)
    side = Column(String, nullable=False)
    order_type = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=True)
    stop_price = Column(Float, nullable=True)
    time_in_force = Column(String, nullable=True)
    status = Column(String, nullable=False)
    executed_qty = Column(Float, default=0.0)
    avg_price = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    response_data = Column(Text, nullable=True)  # JSON response from API
    
    def __repr__(self):
        return f"<OrderHistory(order_id={self.order_id}, symbol={self.symbol}, status={self.status})>"

class ActivityLog(Base):
    """Activity log table for tracking all actions"""
    __tablename__ = 'activity_log'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    action = Column(String, nullable=False)  # place_order, cancel_order, check_status, etc.
    symbol = Column(String, nullable=True)
    order_id = Column(String, nullable=True)
    status = Column(String, nullable=False)  # success, error
    message = Column(Text, nullable=True)
    error_details = Column(Text, nullable=True)
    user_interface = Column(String, nullable=True)  # cli, web, terminal
    
    def __repr__(self):
        return f"<ActivityLog(action={self.action}, status={self.status}, timestamp={self.timestamp})>"

class Database:
    """Database manager"""
    
    def __init__(self, db_path: str = "trading_bot.db"):
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        logger.info(f"Database initialized at {db_path}")
    
    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()
    
    def save_order(self, order_data: dict, response_data: dict = None) -> OrderHistory:
        """Save order to database"""
        session = self.get_session()
        try:
            order = OrderHistory(
                order_id=str(response_data.get('orderId', 'pending')) if response_data else 'pending',
                symbol=order_data.get('symbol'),
                side=order_data.get('side'),
                order_type=order_data.get('type'),
                quantity=order_data.get('quantity'),
                price=order_data.get('price'),
                stop_price=order_data.get('stopPrice'),
                time_in_force=order_data.get('timeInForce'),
                status=response_data.get('status', 'PENDING') if response_data else 'PENDING',
                executed_qty=float(response_data.get('executedQty', 0)) if response_data else 0,
                avg_price=float(response_data.get('avgPrice', 0)) if response_data and response_data.get('avgPrice') else None,
                response_data=str(response_data) if response_data else None
            )
            session.add(order)
            session.commit()
            session.refresh(order)
            logger.info(f"Order saved to database: {order.order_id}")
            return order
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save order: {e}")
            raise
        finally:
            session.close()
    
    def update_order_status(self, order_id: str, status_data: dict) -> Optional[OrderHistory]:
        """Update order status"""
        session = self.get_session()
        try:
            order = session.query(OrderHistory).filter_by(order_id=str(order_id)).first()
            if order:
                order.status = status_data.get('status', order.status)
                order.executed_qty = float(status_data.get('executedQty', order.executed_qty))
                if status_data.get('avgPrice'):
                    order.avg_price = float(status_data.get('avgPrice'))
                order.updated_at = datetime.utcnow()
                order.response_data = str(status_data)
                session.commit()
                session.refresh(order)
                logger.info(f"Order {order_id} updated in database")
                return order
            return None
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to update order: {e}")
            raise
        finally:
            session.close()
    
    def get_order_history(self, symbol: Optional[str] = None, limit: int = 100) -> List[OrderHistory]:
        """Get order history"""
        session = self.get_session()
        try:
            query = session.query(OrderHistory)
            if symbol:
                query = query.filter_by(symbol=symbol)
            orders = query.order_by(OrderHistory.created_at.desc()).limit(limit).all()
            return orders
        finally:
            session.close()
    
    def get_order_by_id(self, order_id: str) -> Optional[OrderHistory]:
        """Get order by ID"""
        session = self.get_session()
        try:
            order = session.query(OrderHistory).filter_by(order_id=str(order_id)).first()
            return order
        finally:
            session.close()
    
    def log_activity(self, action: str, status: str, symbol: Optional[str] = None, 
                    order_id: Optional[str] = None, message: Optional[str] = None,
                    error_details: Optional[str] = None, user_interface: Optional[str] = None):
        """Log activity"""
        session = self.get_session()
        try:
            log = ActivityLog(
                action=action,
                symbol=symbol,
                order_id=str(order_id) if order_id else None,
                status=status,
                message=message,
                error_details=error_details,
                user_interface=user_interface
            )
            session.add(log)
            session.commit()
            logger.debug(f"Activity logged: {action} - {status}")
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to log activity: {e}")
        finally:
            session.close()
    
    def get_activity_logs(self, limit: int = 100) -> List[ActivityLog]:
        """Get activity logs"""
        session = self.get_session()
        try:
            logs = session.query(ActivityLog).order_by(ActivityLog.timestamp.desc()).limit(limit).all()
            return logs
        finally:
            session.close()
    
    def get_statistics(self) -> dict:
        """Get trading statistics"""
        session = self.get_session()
        try:
            total_orders = session.query(OrderHistory).count()
            filled_orders = session.query(OrderHistory).filter_by(status='FILLED').count()
            cancelled_orders = session.query(OrderHistory).filter_by(status='CANCELED').count()
            pending_orders = session.query(OrderHistory).filter(
                OrderHistory.status.in_(['NEW', 'PARTIALLY_FILLED'])
            ).count()
            
            return {
                'total_orders': total_orders,
                'filled_orders': filled_orders,
                'cancelled_orders': cancelled_orders,
                'pending_orders': pending_orders,
                'success_rate': (filled_orders / total_orders * 100) if total_orders > 0 else 0
            }
        finally:
            session.close()

# Global database instance
_db_instance = None

def get_database() -> Database:
    """Get or create database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance
