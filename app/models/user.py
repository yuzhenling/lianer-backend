from sqlalchemy import Boolean, Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from app.db.base import Base
import enum


class VipLevel(enum.Enum):
    FREE = "free"
    HALF_YEAR = "half_year"
    ONE_YEAR = "one_year"
    TWO_YEAR = "two_year"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, index=True, nullable=True)
    phone = Column(String, unique=True, index=True, nullable=True)
    wechat_openid = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # VIP信息
    vip_level = Column(Enum(VipLevel), default=VipLevel.FREE)
    vip_expire_date = Column(DateTime, nullable=True)
    
    # 用户统计
    total_practice_time = Column(Integer, default=0)  # 总练习时长（分钟）
    pitch_test_count = Column(Integer, default=0)     # 音高测试次数
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())