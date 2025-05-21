from __future__ import annotations

import traceback

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from app.models.vip import VipLevel
from app.services.order_service import OrderService
from app.models.user import User
from app.models.order import VipOrder
from app.api.v1.auth_api import get_current_user, get_db
from app.core.i18n import i18n, get_language
from app.core.logger import logger
from app.services.vip_service import vip_service

router = APIRouter(prefix="/order", tags=["order"])
order_service = OrderService()

class OrderCreate(BaseModel):
    vip_id: int
    is_paid: Optional[bool] = None
    paid_date: Optional[datetime] = None
    paid_amount: Optional[int] = None
    is_return: Optional[bool] = None
    return_date: Optional[datetime] = None
    return_amount: Optional[int] = None

class OrderResponse(BaseModel):
    id: int
    trade_no: int
    user_id: int
    vip_id: int
    is_paid: bool | None
    paid_date: datetime | None
    paid_amount: int | None
    is_return: bool | None
    return_date: datetime | None
    return_amount: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True
    }


class WeChatPaymentResponse(BaseModel):
    prepay_id: str
    timeStamp: str
    nonceStr: str
    package: str
    signType: str
    paySign: str


@router.post("/vip", response_model=OrderResponse)
async def create_vip_order(
    request: Request,
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建VIP订单"""
    lang = get_language(request)
    try:
        # 检查VIP等级是否有效
        is_contain = await vip_service.contains_vip(order_data.vip_id)
        if not is_contain:
            logger.error(f"VIP {order_data.vip_id} not found")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=i18n.get_text("INVALID_VIP_LEVEL", lang)
            )

        vip_order = VipOrder(**order_data.model_dump())

        # 创建订单
        order = await order_service.create_vip_order(
            db=db,
            user=current_user,
            vip_order=vip_order
        )

        if not order:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=i18n.get_text("ORDER_CREATE_FAILED", lang)
            )

        return order
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in create_vip_order for user {current_user.id}: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
        )


@router.post("/{order_id}/pay", response_model=WeChatPaymentResponse)
async def create_payment(
    request: Request,
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """支付订单"""
    try:
        lang = get_language(request)

        # 检查订单是否存在且属于当前用户
        order = db.query(VipOrder).filter(
            VipOrder.id == order_id,
            VipOrder.user_id == current_user.id
        ).first()

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=i18n.get_text("ORDER_NOT_FOUND", lang)
            )

        if order.is_paid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=i18n.get_text("ORDER_ALREADY_PAID", lang)
            )

        # 创建微信支付订单
        payment_data = await order_service.create_wechat_payment(db, order, current_user)
        if not payment_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=i18n.get_text("PAYMENT_CREATE_FAILED", lang)
            )

        return payment_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in pay_order for order {order_id}: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
        )


@router.post("/wechat-notify")
async def wechat_payment_notify(
    request: Request,
    db: Session = Depends(get_db)
):
    """处理微信支付回调通知"""
    try:
        # 解析微信支付回调数据
        # TODO: 实现微信支付回调数据验证
        notification_data = await request.json()
        # 开发测试时模拟支付成功
        # notification_data = {
        #     "out_trade_no": "123",  # 订单ID
        #     "trade_state": "SUCCESS"
        # }
        
        order_id = int(notification_data["out_trade_no"])
        payment_success = notification_data["trade_state"] == "SUCCESS"
        
        # 处理支付结果
        success = await order_service.handle_payment_notification(
            db=db,
            order_id=order_id,
            payment_success=payment_success
        )
        
        if success:
            # 返回成功通知
            return {"code": "SUCCESS", "message": "OK"}
        else:
            return {"code": "FAIL", "message": "处理失败"}
            
    except Exception as e:
        logger.error(f"Failed to process payment notification: {str(e)}", exc_info=True)
        return {"code": "FAIL", "message": "处理失败"}
