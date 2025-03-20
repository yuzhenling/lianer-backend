from sqlalchemy import Column, Integer, DateTime, Double, Boolean
from sqlalchemy.sql import func
from app.db.base import Base


class VipOrders(Base):
    __tablename__ = "vip_orders"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, index=True)
    vip_id = Column(Integer, index=True)
    price = Column(Double, index=True)
    discount = Column(Double, index=True)

    is_paid = Column(Boolean, default=False, nullable=True)
    paid_date = Column(DateTime, nullable=True)
    paid_amount = Column(Double, nullable=True)

    is_return = Column(Boolean, default=False, nullable=True)
    return_date = Column(DateTime, nullable=True)
    return_amount = Column(Double, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())