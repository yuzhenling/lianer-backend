from datetime import datetime, timedelta
from typing import Optional
import json
import requests
from sqlalchemy.orm import Session

from app.models.order import VipOrders
from app.models.vip import VipLevel, Vip
from app.models.user import User
from app.core.config import settings
from app.core.logger import logger


class OrderService:

    async def create_vip_order(
        self, 
        db: Session, 
        user: User, 
        vip_level: VipLevel
    ) -> Optional[VipOrders]:
        """创建VIP订单"""
        try:
            # 获取VIP信息
            vip = db.query(Vip).filter(Vip.vip_level == vip_level).first()
            if not vip:
                logger.error(f"VIP level {vip_level} not found")
                return None

            # 创建订单
            order = VipOrders(
                user_id=user.id,
                vip_id=vip_level
                paid_amount=self.vip_prices[vip_level],
                is_paid=False
            )
            
            db.add(order)
            db.commit()
            db.refresh(order)
            
            return order
            
        except Exception as e:
            logger.error(f"Failed to create VIP order: {str(e)}", exc_info=True)
            db.rollback()
            return None

    async def create_wechat_payment(self, order: VipOrders) -> Optional[dict]:
        """创建微信支付订单"""
        try:
            # 调用微信支付统一下单API
            url = "https://api.mch.weixin.qq.com/v3/pay/transactions/jsapi"
            
            # 构建支付请求数据
            data = {
                "appid": settings.WECHAT_APP_ID,
                "mchid": settings.WECHAT_MCH_ID,
                "description": f"声之宝典VIP会员",
                "out_trade_no": str(order.id),  # 使用订单ID作为商户订单号
                "notify_url": f"{settings.API_HOST}/api/v1/orders/wechat-notify",
                "amount": {
                    "total": order.paid_amount,
                    "currency": "CNY"
                }
            }
            
            # TODO: 实现微信支付签名和认证
            # headers = self._get_wechat_pay_headers()
            # response = requests.post(url, json=data, headers=headers)
            # result = response.json()
            
            # 开发测试时模拟返回支付参数
            result = {
                "prepay_id": f"wx{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "timeStamp": str(int(datetime.now().timestamp())),
                "nonceStr": "nonceStr",
                "package": "prepay_id=wx123456789",
                "signType": "RSA",
                "paySign": "paySign"
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to create WeChat payment: {str(e)}", exc_info=True)
            return None

    async def handle_payment_notification(
        self, 
        db: Session, 
        order_id: int, 
        payment_success: bool
    ) -> bool:
        """处理支付回调通知"""
        try:
            order = db.query(VipOrders).filter(VipOrders.id == order_id).first()
            if not order:
                logger.error(f"Order {order_id} not found")
                return False

            if payment_success:
                # 更新订单状态
                order.is_paid = True
                order.paid_date = datetime.now()
                
                # 更新用户VIP状态
                user = db.query(User).filter(User.id == order.user_id).first()
                if user:
                    vip = db.query(Vip).filter(Vip.id == order.vip_id).first()
                    if vip:
                        user.is_vip = True
                        user.vip_start_date = datetime.now()
                        # 计算到期时间
                        duration_days = self.vip_durations.get(vip.vip_level, 0)
                        user.vip_expire_date = datetime.now() + timedelta(days=duration_days)
                
                db.commit()
                logger.info(f"Successfully processed payment for order {order_id}")
                return True
            else:
                logger.error(f"Payment failed for order {order_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to process payment notification: {str(e)}", exc_info=True)
            db.rollback()
            return False

    def _get_wechat_pay_headers(self) -> dict:
        """获取微信支付API请求头（包含签名等信息）"""
        # TODO: 实现微信支付API请求头生成
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "签名信息"
        }
