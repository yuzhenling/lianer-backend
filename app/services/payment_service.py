import hashlib
import time
import xml.etree.ElementTree as ET
import requests
from typing import Optional, Dict, Any
from app.models.payment import Payment, Order, PaymentStatus, PaymentType
from app.db.session import get_db
from sqlalchemy.orm import Session
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class PaymentService:
    def __init__(self):
        self.app_id = "your_app_id"  # 微信小程序appid
        self.mch_id = "your_mch_id"  # 商户号
        self.api_key = "your_api_key"  # API密钥
        self.notify_url = "https://your-domain.com/api/v1/payment/notify"  # 支付回调地址
        
    def create_order(self, db: Session, user_id: str, amount: float, description: str) -> Dict[str, Any]:
        """创建订单和支付记录
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            amount: 支付金额
            description: 订单描述
            
        Returns:
            Dict[str, Any]: 包含订单和支付信息的字典
        """
        # 生成订单号
        order_id = self._generate_order_id()
        
        # 创建订单
        order = Order(
            order_id=order_id,
            user_id=user_id,
            amount=amount,
            description=description,
            status="pending"
        )
        db.add(order)
        db.flush()
        
        # 创建支付记录
        payment = Payment(
            user_id=user_id,
            order_id=order_id,
            amount=amount,
            payment_type=PaymentType.WECHAT_MINI,
            description=description,
            status=PaymentStatus.PENDING
        )
        db.add(payment)
        db.flush()
        
        # 更新订单的支付ID
        order.payment_id = payment.id
        db.commit()
        
        return {
            "order_id": order_id,
            "payment_id": payment.id,
            "amount": amount,
            "description": description
        }
    
    def create_wechat_payment(self, db: Session, payment_id: int, openid: str) -> Dict[str, Any]:
        """创建微信支付
        
        Args:
            db: 数据库会话
            payment_id: 支付记录ID
            openid: 用户openid
            
        Returns:
            Dict[str, Any]: 微信支付参数
        """
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise ValueError("Payment not found")
            
        # 统一下单接口
        url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
        
        # 构建请求参数
        params = {
            "appid": self.app_id,
            "mch_id": self.mch_id,
            "nonce_str": self._generate_nonce_str(),
            "body": payment.description,
            "out_trade_no": payment.order_id,
            "total_fee": int(payment.amount * 100),  # 转换为分
            "spbill_create_ip": "127.0.0.1",
            "notify_url": self.notify_url,
            "trade_type": "JSAPI",
            "openid": openid
        }
        
        # 生成签名
        params["sign"] = self._generate_sign(params)
        
        # 发送请求
        response = requests.post(url, data=self._dict_to_xml(params))
        result = self._xml_to_dict(response.text)
        
        if result["return_code"] == "SUCCESS" and result["result_code"] == "SUCCESS":
            # 更新支付记录
            payment.prepay_id = result["prepay_id"]
            db.commit()
            
            # 生成小程序支付参数
            pay_params = {
                "appId": self.app_id,
                "timeStamp": str(int(time.time())),
                "nonceStr": self._generate_nonce_str(),
                "package": f"prepay_id={result['prepay_id']}",
                "signType": "MD5"
            }
            pay_params["paySign"] = self._generate_sign(pay_params)
            
            return pay_params
        else:
            raise ValueError(f"WeChat payment creation failed: {result.get('err_code_des', 'Unknown error')}")
    
    def handle_payment_notify(self, xml_data: str) -> Dict[str, Any]:
        """处理支付回调
        
        Args:
            xml_data: 微信支付回调XML数据
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        try:
            # 解析XML数据
            data = self._xml_to_dict(xml_data)
            
            # 验证签名
            if not self._verify_sign(data):
                return {"return_code": "FAIL", "return_msg": "Invalid signature"}
            
            # 获取支付记录
            db = next(get_db())
            payment = db.query(Payment).filter(Payment.order_id == data["out_trade_no"]).first()
            
            if not payment:
                return {"return_code": "FAIL", "return_msg": "Payment not found"}
            
            # 更新支付状态
            if data["return_code"] == "SUCCESS" and data["result_code"] == "SUCCESS":
                payment.status = PaymentStatus.SUCCESS
                payment.transaction_id = data["transaction_id"]
                payment.paid_at = datetime.utcnow()
                
                # 更新订单状态
                order = payment.order
                order.status = "paid"
                
                db.commit()
                
                return {"return_code": "SUCCESS", "return_msg": "OK"}
            else:
                payment.status = PaymentStatus.FAILED
                db.commit()
                
                return {"return_code": "FAIL", "return_msg": data.get("err_code_des", "Unknown error")}
                
        except Exception as e:
            logger.error(f"Payment notify error: {str(e)}")
            return {"return_code": "FAIL", "return_msg": str(e)}
    
    def _generate_order_id(self) -> str:
        """生成订单号"""
        return f"{int(time.time())}{hashlib.md5(str(time.time()).encode()).hexdigest()[:6]}"
    
    def _generate_nonce_str(self) -> str:
        """生成随机字符串"""
        return hashlib.md5(str(time.time()).encode()).hexdigest()
    
    def _generate_sign(self, params: Dict[str, Any]) -> str:
        """生成签名"""
        # 按字典序排序
        sorted_params = sorted(params.items(), key=lambda x: x[0])
        # 拼接字符串
        string = "&".join([f"{k}={v}" for k, v in sorted_params if k != "sign" and v])
        # 添加API密钥
        string += f"&key={self.api_key}"
        # MD5加密
        return hashlib.md5(string.encode()).hexdigest().upper()
    
    def _verify_sign(self, data: Dict[str, Any]) -> bool:
        """验证签名"""
        sign = data.pop("sign", "")
        return sign == self._generate_sign(data)
    
    def _dict_to_xml(self, params: Dict[str, Any]) -> str:
        """字典转XML"""
        xml = "<xml>"
        for k, v in params.items():
            xml += f"<{k}>{v}</{k}>"
        xml += "</xml>"
        return xml
    
    def _xml_to_dict(self, xml: str) -> Dict[str, Any]:
        """XML转字典"""
        root = ET.fromstring(xml)
        return {child.tag: child.text for child in root}


payment_service = PaymentService() 