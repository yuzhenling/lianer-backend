from sqlalchemy import Column, Integer, DateTime, Double, Boolean, Enum, String
from sqlalchemy.sql import func
import enum

from app.db.database import Base


class VipLevel(enum.Enum):
    FREE = "free"
    NORMAL = "normal"
    HALF_YEAR = "half_year"
    ONE_YEAR = "one_year"


class Vip(Base):
    __tablename__ = "vip"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    level = Column(Enum(VipLevel), default=VipLevel.FREE)
    name = Column(String(20), nullable=False)
    describe = Column(String, nullable=True)

    price = Column(Double, index=True, default=0)
    discount = Column(Double, index=True, default=0)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


