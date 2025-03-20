from sqlalchemy import Boolean, Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from app.db.base import Base
import enum


class VipLevel(enum.Enum):
    FREE = "free"
    HALF_YEAR = "half_year"
    ONE_YEAR = "one_year"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=False, index=True, nullable=True)
    phone = Column(String, unique=False, index=True, nullable=True)
    wechat_openid = Column(String, unique=True, index=True, nullable=True)
    unionid = Column(String, unique=True, index=False, nullable=True)
    hashed_password = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

    is_vip = Column(Boolean, default=False)
    vip_start_date = Column(DateTime, nullable=True)
    vip_expire_date = Column(DateTime, nullable=True)
    
    # 用户统计
    total_practice_time = Column(Integer, default=0, nullable=True)  # 总练习时长（分钟）
    pitch_test_count = Column(Integer, default=0, nullable=True )     # 音高测试次数
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Vip(Base):
    __tablename__ = "vip"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    vip_level = Column(Enum(VipLevel), default=VipLevel.FREE)
    vip_describe = Column(String, nullable=True)






