from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from app.db.database import Base


class PaymentStatus(enum.Enum):
    PENDING = "pending"  # 待支付
    SUCCESS = "success"  # 支付成功
    FAILED = "failed"    # 支付失败
    REFUNDED = "refunded"  # 已退款

class PaymentType(enum.Enum):
    WECHAT_MINI = "wechat_mini"  # 微信小程序支付
    WECHAT_H5 = "wechat_h5"     # 微信H5支付
    ALIPAY = "alipay"           # 支付宝支付

class Payment(Base):
    """支付记录表"""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), index=True, nullable=False)  # 用户ID
    order_id = Column(String(50), unique=True, index=True, nullable=False)  # 订单号
    transaction_id = Column(String(50), unique=True, index=True)  # 微信支付交易号
    amount = Column(Float, nullable=False)  # 支付金额（元）
    payment_type = Column(Enum(PaymentType), nullable=False)  # 支付类型
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)  # 支付状态
    description = Column(String(255))  # 支付描述
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间
    paid_at = Column(DateTime)  # 支付时间
    refunded_at = Column(DateTime)  # 退款时间
    
    # 微信支付相关字段
    prepay_id = Column(String(50))  # 预支付交易会话标识
    code_url = Column(String(255))  # 二维码链接
    openid = Column(String(50))  # 用户openid
    
    # 关联的订单信息
    order = relationship("Order", back_populates="payment", uselist=False)

class Order(Base):
    """订单表"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(50), unique=True, index=True, nullable=False)  # 订单号
    user_id = Column(String(50), index=True, nullable=False)  # 用户ID
    payment_id = Column(Integer, ForeignKey("payments.id"))  # 支付记录ID
    amount = Column(Float, nullable=False)  # 订单金额
    description = Column(String(255))  # 订单描述
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间
    status = Column(String(20), default="pending")  # 订单状态
    
    # 关联的支付记录
    payment = relationship("Payment", back_populates="order") 