from sqlalchemy import Column, Integer, DateTime, Double, Boolean, BigInteger
from sqlalchemy.sql import func
from app.db.base import Base


class VipOrder(Base):
    __tablename__ = "vip_order"
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    trade_no = Column(BigInteger, index=True, nullable=False)
    user_id = Column(Integer, index=True)
    vip_id = Column(Integer, index=True)

    is_paid = Column(Boolean, default=False, nullable=True)
    paid_date = Column(DateTime, nullable=True)
    paid_amount = Column(BigInteger, nullable=True) #整数 分单位

    is_return = Column(Boolean, default=False, nullable=True)
    return_date = Column(DateTime, nullable=True)
    return_amount = Column(BigInteger, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


