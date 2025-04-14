from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from app.api.v1.auth_api import get_db
from app.services.payment_service import payment_service
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/pay", tags=["pay"])

class CreateOrderRequest(BaseModel):
    user_id: str
    amount: float
    description: str

class CreatePaymentRequest(BaseModel):
    payment_id: int
    openid: str


@router.post("/add")
async def create_payment(
    request: CreatePaymentRequest,
    db: Session = Depends(get_db)
):
    """创建支付"""
    try:
        result = payment_service.create_wechat_payment(
            db=db,
            payment_id=request.payment_id,
            openid=request.openid
        )
        return {"code": 0, "message": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/notify")
async def payment_notify(
    xml_data: str = Body(..., media_type="application/xml")
):
    """支付回调通知"""
    try:
        result = payment_service.handle_payment_notify(xml_data)
        return result
    except Exception as e:
        return {"return_code": "FAIL", "return_msg": str(e)} 