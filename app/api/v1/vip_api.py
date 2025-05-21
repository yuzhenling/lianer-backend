import traceback

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy import Enum
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from app.api.v1.auth_api import get_current_user, get_db
from app.core.logger import logger
from app.models.vip import VipLevel
from app.services.vip_service import vip_service
from app.models.user import User

from app.core.i18n import i18n, get_language

router = APIRouter(prefix="/vip", tags=["vip"])

class VipBase(BaseModel):
    level: VipLevel
    describe: str
    price: float = Field(..., gt=0)  # 价格必须大于0
    discount: float = Field(..., ge=0, le=1)  # 折扣必须在0到1之间

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True
    }


class VipCreate(VipBase):
    pass


class VipUpdate(BaseModel):
    describe: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    discount: Optional[float] = Field(None, ge=0, le=1)


class VipResponse(VipBase):
    id: int
    level: VipLevel
    describe: str
    price: float
    discount: float
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True
    }


@router.get("", response_model=List[VipResponse])
async def get_all_vips(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    lang = get_language(request)
    try:
        """获取所有VIP等级信息"""
        # return vip_service.get_all_vips()
        vips = await vip_service.get_all_vips()
        if not vips:
            return []
        return [VipResponse.model_validate(vip) for vip in vips]
    except Exception as e:
        logger.error(f"Error in get_all_vips: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
        )

@router.get("/{vip_id}", response_model=VipResponse)
async def get_vip_by_id(
    request: Request,
    vip_id: int,
    current_user: User = Depends(get_current_user)
):
    """通过ID获取VIP等级信息"""
    lang = get_language(request)
    try:
        vip = vip_service.get_vip_by_id(vip_id)
        if not vip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=i18n.get_text("VIP_NOT_FOUND", lang)
            )
        return vip
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_vip_by_id for id {vip_id}: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
        )


@router.post("", response_model=VipResponse)
async def create_vip(
    request: Request,
    vip_data: VipCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新的VIP等级"""
    lang = get_language(request)
    try:
        # 检查权限（这里假设只有管理员可以创建VIP等级）
        if not current_user.is_super_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=i18n.get_text("PERMISSION_DENIED", lang)
            )

        vip = await vip_service.create_vip(
            db=db,
            vip_level=vip_data.level,
            vip_describe=vip_data.describe,
            vip_price=vip_data.price,
            vip_discount=vip_data.discount
        )

        if not vip:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=i18n.get_text("VIP_CREATE_FAILED", lang)
            )

        return vip
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in create_vip: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
        )


@router.put("/{vip_id}", response_model=VipResponse)
async def update_vip(
    request: Request,
    vip_id: int,
    vip_data: VipUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新VIP等级信息"""
    lang = get_language(request)
    try:
        if not current_user.is_super_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=i18n.get_text("PERMISSION_DENIED", lang)
            )

        vip = vip_service.get_vip_by_id(vip_id)
        if not vip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=i18n.get_text("VIP_NOT_FOUND", lang)
            )

        update_data = {}
        if vip_data.describe is not None:
            update_data["describe"] = vip_data.describe
        if vip_data.price is not None:
            update_data["price"] = vip_data.price
        if vip_data.discount is not None:
            update_data["discount"] = vip_data.discount

        updated_vip = await vip_service.update_vip(db, vip_id, update_data)
        if not updated_vip:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=i18n.get_text("VIP_UPDATE_FAILED", lang)
            )

        return updated_vip
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_vip for id {vip_id}: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
        )


@router.delete("/{vip_id}")
async def delete_vip(
    request: Request,
    vip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除VIP等级"""
    lang = get_language(request)
    try:
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=i18n.get_text("PERMISSION_DENIED", lang)
            )

        vip = vip_service.get_vip_by_id(vip_id)
        if not vip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=i18n.get_text("VIP_NOT_FOUND", lang)
            )

        success = await vip_service.delete_vip(db, vip_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=i18n.get_text("VIP_DELETE_FAILED", lang)
            )

        return {"message": i18n.get_text("VIP_DELETE_SUCCESS", lang)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delete_vip for id {vip_id}: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
        )
