import base64
import json
import os
import random
import string
import struct
import time
from datetime import  timedelta
from typing import Optional
import requests
from OpenSSL import crypto
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from sqlalchemy.orm import Session

from app.models.order import VipOrder
from app.models.vip import VipLevel, Vip
from app.models.user import User
from app.core.config import settings
from app.core.logger import logger
from app.services.vip_service import vip_service


class OrderService:

    async def create_vip_order(
        self, 
        db: Session, 
        user: User,
        vip_order: VipOrder
    ) -> Optional[VipOrder]:
        """创建VIP订单"""
        try:
            out_trade_no = f"{int(time.time())}{random.randint(100, 999)}"
            # 创建订单
            order = VipOrder(
                user_id=user.id,
                vip_id=vip_order.vip_id,
                trade_no=out_trade_no,
                is_paid=vip_order.is_paid,
                paid_amount=vip_order.paid_amount,
                is_return=vip_order.is_return,
                return_amount=vip_order.return_amount,
                return_date=vip_order.return_date,
            )
            db.add(order)
            db.commit()
            db.refresh(order)
            
            return order
            
        except Exception as e:
            logger.error(f"Failed to create VIP order: {str(e)}", exc_info=True)
            db.rollback()
            return None

    async def create_wechat_payment(self, db: Session, order: VipOrder, current_user: User) -> Optional[dict]:
        """创建微信支付订单"""
        try:
            # 调用微信支付统一下单API
            url = "https://api.mch.weixin.qq.com/v3/pay/transactions/jsapi"
            
            # 构建支付请求数据
            data = {
                "appid": settings.WECHAT_APP_ID,
                "mchid": settings.WECHAT_MCH_ID,
                "description": f"声之宝典VIP会员",
                "out_trade_no": str(order.trade_no),  # 使用订单ID作为商户订单号
                "notify_url": f"{settings.API_HOST}/api/v1/orders/wechat-notify",
                "amount": {
                    "total": order.paid_amount,
                    "currency": "CNY"
                },
                "payer": {
                    "openid": current_user.wechat_openid,
                }
            }
            body_str = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
            logger.info(f"WECHAT PAY POST body: {body_str}")
            
            # TODO: 实现微信支付签名和认证

            timestamp = str(int(time.time()))
            nonce_str = self.generate_nonce_str()

            headers = self._get_wechat_pay_headers(method="POST", url=url, timestamp=timestamp, nonce_str=nonce_str, body=body_str, mch_id=settings.WECHAT_MCH_ID, serial_no=settings.WECHAT_PAY_SERIAL_NO, private_key_path=settings.WECHAT_PAY_KEY_PATH)
            logger.info(f"WECHAT PAY POST headers: {headers}")
            response = requests.post(url, data=body_str.encode('utf-8'), headers=headers)
            resp = response.json()
            # #TODO 模拟
            # resp = {"prepay_id": "wx19171500523387e20884ba3048ea1e0001"}
            #更新order
            order.prepay_id = resp.get("prepay_id")
            db.add(order)
            db.commit()

            paySign = self.build_pay_signature(settings.WECHAT_APP_ID, timestamp, nonce_str, resp)

            # 开发测试时模拟返回支付参数
            result = {
                "prepay_id": resp.get("prepay_id"),
                "timeStamp": timestamp,
                "nonceStr": nonce_str,
                "package": "prepay_id="+resp.get("prepay_id"),
                "signType": "RSA",
                "paySign": paySign
            }
            logger.info(f"WECHAT PAY return UI: {result}")
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
            order = db.query(VipOrder).filter(VipOrder.id == order_id).first()
            if not order:
                logger.error(f"Order {order_id} not found")
                return False

            if payment_success:
                # 更新订单状态
                order.is_paid = True
                order.paid_date = datetime.now()
                db.add(order)
                db.commit()
                
                # 更新用户VIP状态
                user = db.query(User).filter(User.id == order.user_id).first()
                if user:
                    vip = db.query(Vip).filter(Vip.id == order.vip_id).first()
                    if vip:
                        user.is_vip = True
                        user.vip_start_date = datetime.now()
                        # 计算到期时间
                        duration_days = vip_service.getDaysById(order.vip_id)
                        user.vip_expire_date = datetime.now() + timedelta(days=duration_days)
                        db.add(user)
                        db.commit()
                        db.refresh(user)

                logger.info(f"Successfully processed payment for order {order_id}")
                return True
            else:
                logger.error(f"Payment failed for order {order_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to process payment notification: {str(e)}", exc_info=True)
            db.rollback()
            return False


    def _get_wechat_pay_headers(self, method, url, timestamp, nonce_str, body, mch_id, serial_no, private_key_path) -> dict:
        """获取微信支付API请求头（包含签名等信息）"""
        # TODO: 实现微信支付API请求头生成
        authorization = self.generate_authorization(method, url, timestamp, nonce_str, body, mch_id, serial_no, private_key_path)
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": authorization
        }

    def generate_authorization(self, method, url, timestamp, nonce_str, body, mch_id, serial_no, private_key_path):
        """
        生成微信支付V3 API的Authorization头
        https://pay.weixin.qq.com/doc/v3/merchant/4012365336
        HTTP请求方法\n
        URL\n
        请求时间戳\n
        请求随机串\n
        请求报文主体\n

        参数:
        - method: HTTP方法，如'POST'
        - url: 请求的完整URL
        - body: 请求体内容(JSON字符串)
        - mch_id: 商户号
        - serial_no: 商户证书序列号
        - private_key_path: 商户私钥文件路径

        返回:
        - 完整的Authorization头
        """
        # 2. 构造签名信息
        message = self.build_sign_message(method, url, timestamp, nonce_str, body)

        # 3. 生成签名
        signature = self.sign_message(message, private_key_path)

        # 4. 构造Authorization头
        token = f'WECHATPAY2-SHA256-RSA2048 mchid="{mch_id}",nonce_str="{nonce_str}",signature="{signature}",timestamp="{timestamp}",serial_no="{serial_no}"'

        return token

    def generate_nonce_str(self, length=32):
        """生成随机字符串"""
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

    def generate_hex_string(self):
        random_bytes = os.urandom(16)  # 生成16字节随机数
        parts = struct.unpack('>4I', random_bytes)  # 按大端序解包成4个unsigned int
        return ''.join(f'{part:08X}' for part in parts)

    def build_sign_message(self, method, url, timestamp, nonce_str, body):
        """
        构造待签名的消息
        """
        # 获取URL路径和查询参数部分
        url_path = "/"+url.split('//', 1)[-1].split('/', 1)[-1]

        # 构造签名信息
        message = f"{method}\n{url_path}\n{timestamp}\n{nonce_str}\n{body}\n"
        return message

    def sign_message(self, message, private_key_path):
        """
        使用私钥对消息进行签名
        """
        # 加载私钥
        with open(private_key_path, 'rb') as f:
            private_key = load_pem_private_key(f.read(), password=None)

        # 对消息进行签名
        signature = private_key.sign(
            message.encode('utf-8'),
            padding.PKCS1v15(),
            hashes.SHA256()
        )

        # Base64编码签名结果
        return base64.b64encode(signature).decode('utf-8')

    def build_pay_signature(self, appid, timestamp, nonce_str, prepay_id):
        message = f"{appid}\n{timestamp}\n{nonce_str}\n{prepay_id}\n"
        sign = self.sign_message(message, settings.WECHAT_PAY_KEY_PATH)
        return sign

    def get_serial_no_from_cert(self, cert_path):
        with open(cert_path, 'r') as f:
            cert_content = f.read()
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_content)
        return cert.get_serial_number()


