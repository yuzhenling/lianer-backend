from dataclasses import dataclass
from typing import Optional

from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.db.database import Base
from app.models.vip import VipLevel


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=False, index=True, nullable=True)
    phone = Column(String(20), unique=False, index=True, nullable=True)
    wechat_openid = Column(String(512), unique=True, index=True, nullable=True)
    unionid = Column(String(512), unique=True, index=False, nullable=True)
    hashed_password = Column(String(512), nullable=True)
    is_active = Column(Boolean, default=True)

    is_vip = Column(Boolean, default=False)
    vip_start_date = Column(DateTime, nullable=True)
    vip_expire_date = Column(DateTime, nullable=True)
    
    # 用户统计
    total_practice_time = Column(Integer, default=0, nullable=True)  # 总练习时长（分钟）
    pitch_test_count = Column(Integer, default=0, nullable=True )     # 音高测试次数
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    is_super_admin = Column(Boolean, default=False)

@dataclass
class CombineUser:
    id: int
    wechat_openid: str
    is_active: bool
    is_super_admin: bool
    email: Optional[str] = None
    phone: Optional[str] = None
    unionid: Optional[str] = None

    is_vip: Optional[bool] = None
    vip_start_date: Optional[DateTime] = None
    vip_expire_date: Optional[DateTime] = None

    vip_id: Optional[int] = None
    vip_level: Optional[VipLevel] = None
    order_id: Optional[int] = None


class UserInfo(Base):
    __tablename__ = "user_info"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    nickname = Column(String(50))
    avatar_url = Column(String(255))
    phone = Column(String(20))
    gender = Column(String(10))
    country = Column(String(50))
    province = Column(String(50))
    city = Column(String(50))
    language = Column(String(20))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())








