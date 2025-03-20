from sqlalchemy import Column, Integer, DateTime, Double, Boolean, Enum, String
from sqlalchemy.sql import func
from app.db.base import Base
import enum

class VipLevel(enum.Enum):
    FREE = "free"
    NORMAL = "normal"
    HALF_YEAR = "half_year"
    ONE_YEAR = "one_year"


class Vip(Base):
    __tablename__ = "vip"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    level = Column(Enum(VipLevel), default=VipLevel.FREE)
    describe = Column(String, nullable=True)



class Product(Base):
    __tablename__ = "product"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    vip_id = Column(Integer, index=True)
    price = Column(Double, index=True)
    discount = Column(Double, index=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())