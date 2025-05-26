from __future__ import annotations

import traceback

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

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
    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "example": [
                {
                "vip_id": 2,
                "paid_amount": 100
                }
            ]
        }
    }

class OrderQuery(BaseModel):
    id: Optional[int] = None
    user_id: Optional[int] = None
    vip_id: Optional[int] = None
    trade_no: Optional[int] = None
    prepay_id: Optional[str] = None
    is_paid: Optional[bool] = None
    paid_date_s: Optional[datetime] = None
    paid_date_e: Optional[datetime] = None
    paid_amount: Optional[int] = None
    is_return: Optional[bool] = None
    return_date_s: Optional[datetime] = None
    return_date_e: Optional[datetime] = None
    return_amount: Optional[int] = None
    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "example": [

            ]
        }
    }

# class OrderServiceQuery(BaseModel):
#     user_id: Optional[int] = None
#     # is_paid: bool = True
#     # is_return: bool = False
#     model_config = {
#         "from_attributes": True,
#         "arbitrary_types_allowed": True,
#         "json_schema_extra": {
#             "example": [
#
#             ]
#         }
#     }

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

class OrderServiceResponse(BaseModel):
    count: int
    orders: list[OrderResponse]

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
    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "example": [
                {
                    "prepay_id": 1111,
                    "timeStamp": 1111,
                    "nonceStr": 1111,
                    "package": 1111,
                    "signType": 1111,
                    "paySign": 1111,
                }
            ]
        }
    }


@router.post("/vip", response_model=OrderResponse)
async def create_vip_order(
    request: Request,
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建VIP订单接口
    
    为用户创建VIP购买订单，包括订单状态、支付信息等。
    
    Args:
        request: FastAPI请求对象
        order_data: 订单创建请求体
            - vip_id: VIP等级ID
            - is_paid: 是否已支付（可选）
            - paid_date: 支付日期（可选）
            - paid_amount: 支付金额（可选）
            - is_return: 是否退款（可选）
            - return_date: 退款日期（可选）
            - return_amount: 退款金额（可选）
        current_user: 当前登录用户对象
        db: 数据库会话依赖
        
    Returns:
        OrderResponse: 创建的订单信息
            - id: 订单ID
            - user_id: 用户ID
            - vip_id: VIP等级ID
            - order_date: 订单日期
            - status: 订单状态
            - amount: 订单金额
            
    Raises:
        HTTPException:
            - 400: 无效的VIP等级
            - 500: 服务器内部错误

    """
    lang = get_language(request)
    try:
        # 检查VIP等级是否有效
        is_contain = vip_service.contains_vip(order_data.vip_id)
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


@router.post(path="/query", response_model=OrderServiceResponse)
async def get_vip_orders(
        request: Request,
        order_query: OrderQuery,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    获取当前用户下单的VIP订单列表接口
    
    根据查询条件获取用户的VIP订单列表，包括未支付的、支付的全部订单。
    
    Args:
        request: FastAPI请求对象
        order_query: 订单查询条件
            - id: 订单ID（可选）
            - user_id: 用户ID（可选）
            - vip_id: VIP等级ID（可选）
            - trade_no: 交易号（可选）
            - prepay_id: 预支付ID（可选）
            - is_paid: 是否已支付（可选）
            - paid_date_s: 起始支付日期（可选）
            - paid_date_e: 结束支付日期（可选）
            - paid_amount: 支付金额（可选）
            - is_return: 是否退款（可选）
            - return_date_s: 起始退款日期（可选）
            - return_date_e: 结束退款日期（可选）
            - return_amount: 退款金额（可选）
        current_user: 当前登录用户对象
        db: 数据库会话依赖
        
    Returns:
        OrderServiceResponse: 订单信息列表
        
    Raises:
        HTTPException:
            - 500: 服务器内部错误
    """
    lang = get_language(request)
    try:
        # 将查询参数转换为字典，并移除None值
        query_params = {k: v for k, v in order_query.model_dump().items() if v is not None}
        
        # 调用服务层方法获取订单列表
        orders = await order_service.get_vip_orders(
            db=db,
            query_params=query_params,
            user_id=current_user.id
        )

        if not orders:
            return OrderServiceResponse(
                count=0,
                orders=[],
            )

        return OrderServiceResponse(
            count=len(orders),
            orders=orders,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to query create_vip_order for user {current_user.id}: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
        )


@router.get(path="/service", response_model=OrderServiceResponse)
async def get_vip_service(
        request: Request,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    获取当前用户的生效的VIP订单列表接口

    根据查询条件获取用户的VIP订单列表。

    Args:
        request: FastAPI请求对象
        current_user: 当前登录用户对象
        db: 数据库会话依赖

    Returns:
        OrderServiceResponse: 订单信息列表

    Raises:
        HTTPException:
            - 500: 服务器内部错误
    """
    lang = get_language(request)
    try:
        # 将查询参数转换为字典，并移除None值

        # 调用服务层方法获取订单列表
        orders = await order_service.get_service_orders(
            db=db,
            user_id=current_user.id
        )

        if not orders:
            return OrderServiceResponse(
                count=0,
                orders=[],
            )

        return OrderServiceResponse(
                count=len(orders),
                orders=orders,
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to query create_vip_order for user {current_user.id}: {str(e)}\nTraceback: {traceback.format_exc()}")
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
    """
    创建订单支付接口
    
    为指定订单创建微信支付订单，返回支付所需的参数。
    
    Args:
        request: FastAPI请求对象
        order_id: 订单ID
        current_user: 当前登录用户对象
        db: 数据库会话依赖
        
    Returns:
        WeChatPaymentResponse: 微信支付参数
            - prepay_id: 预支付ID
            - timeStamp: 时间戳
            - nonceStr: 随机字符串
            - package: 订单详情扩展字符串
            - signType: 签名类型
            - paySign: 签名
            
    Raises:
        HTTPException:
            - 404: 订单不存在
            - 400: 订单已支付
            - 500: 服务器内部错误
            
    """
    try:
        lang = get_language(request)

        # 检查订单是否存在且属于当前用户
        # order = await db.query(VipOrder).filter(
        #     VipOrder.id == order_id,
        #     VipOrder.user_id == current_user.id
        # ).first()
        result = await db.execute(select(VipOrder).where(VipOrder.id == order_id, VipOrder.user_id == current_user.id))
        order = result.scalar_one_or_none()

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
    """
    处理微信支付回调通知接口
    
    接收并处理微信支付的异步通知，更新订单支付状态。
    
    Args:
        request: FastAPI请求对象
        db: 数据库会话依赖
        
    Returns:
        dict: 处理结果
            - code: 处理结果代码（SUCCESS/FAIL）
            - message: 处理结果消息
            
    Example Response:
        ```json
        {
            "code": "SUCCESS",
            "message": "OK"
        }
        ```
    """
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
