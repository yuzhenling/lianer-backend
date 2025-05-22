import json
from typing import Optional, Literal

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, outerjoin

from app.core import logger
from app.core.config import settings
from app.models.user import User, UserInfo
from app.services.auth_service import AuthService
from app.db.database import get_db
from app.core.i18n import i18n, get_language
from app.core.logger import logger

router = APIRouter(prefix="", tags=["auth"])
auth_service = AuthService()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")


class Token(BaseModel):
    access_token: str
    token_type: str


class WeChatLogin(BaseModel):
    code: str


class WeChatUserInfo(BaseModel):
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
    gender: Literal["男", "女"] = Field(..., description="性别只能是 '男' 或 '女'")
    country: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    language: Optional[str] = None

async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    lang = get_language(request)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=i18n.get_text("COULD_NOT_VALIDATE_CREDENTIALS", lang),
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = auth_service.verify_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=i18n.get_text("INVALID_TOKEN", lang)
            )
            
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
        # 使用异步查询
        result = await db.execute(select(User).filter(User.id == int(user_id)))
        user = result.scalar_one_or_none()
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=i18n.get_text("USER_NOT_FOUND", lang)
            )
            
        return user
    except Exception as e:
        raise credentials_exception


@router.post("/auth/wechat-login", response_model=Token)
async def wechat_login(
    request: Request,
    login_data: WeChatLogin,
    db: Session = Depends(get_db)
):
    """微信小程序登录"""
    lang = get_language(request)
    
    try:
        wechat_data = await auth_service.verify_wechat_code(login_data.code)
        reps = '{"openid": "ox75Z7NkQ58loRuhVu9OoNHTDtJY", "session_key": "qNnx7kln91EW/xBBbqP85A=="}'
        # reps = '{"openid": "oqqiv6YxTvbPA0dGJXf-XAMGp6Gs", "session_key": "psbJmWtjELRODF9umW5rwA=="}'
        wechat_data = json.loads(reps)
        logger.info(wechat_data)
        if not wechat_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=i18n.get_text("INVALID_WECHAT_CODE", lang)
            )
        
        # 查找或创建用户
        # user = await db.query(User).filter(User.wechat_openid == wechat_data["openid"]).first()
        result = await db.execute(select(User).where(User.wechat_openid == wechat_data["openid"]))
        user: User = result.scalar_one_or_none()
        if not user:
            user = User(
                wechat_openid=wechat_data["openid"],
                unionid=wechat_data.get("unionid"),
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        # 创建访问令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth_service.create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        logger.error(e, status.HTTP_401_UNAUTHORIZED)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=i18n.get_text("WECHAT_LOGIN_FAILED", lang)
        )


@router.post("/auth/update/userinfo")
async def update_user_info(
        request: Request,
        user_info: WeChatUserInfo,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """更新微信用户信息"""
    lang = get_language(request)
    try:
        # 检查是否已存在用户信息
        # existing_info = db.query(UserInfo).filter(UserInfo.user_id == current_user.id).first()
        result = await db.execute(select(UserInfo).where(UserInfo.user_id == current_user.id))
        existing_info: User = result.scalar_one_or_none()
        if existing_info:
            # 更新现有信息
            for field, value in user_info.model_dump(exclude_unset=True).items():
                setattr(existing_info, field, value)
            db.add(existing_info)
        else:
            # 创建新的用户信息
            new_info = UserInfo(
                user_id=current_user.id,
                **user_info.model_dump(exclude_unset=True)
            )
            db.add(new_info)

        db.commit()

        return {
            "code": 0,
            "message": i18n.get_text("USER_INFO_UPDATED", lang),
            "data": user_info.model_dump(exclude_unset=True)
        }
    except Exception as e:
        logger.error(f"Failed to update user info: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
        )


@router.get("/auth/myinfo")
async def get_user_info(
        request: Request,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """获取用户信息"""
    lang = get_language(request)
    try:
        # 使用 join 查询用户信息和用户基本信息
        # result = db.query(User, UserInfo).outerjoin(UserInfo, User.id == UserInfo.user_id).filter(User.id == current_user.id).first()
        result = await db.execute(select(User, UserInfo).select_from(outerjoin(User, UserInfo, User.id == UserInfo.user_id)).where(User.id == current_user.id))
        result: User = result.scalar_one_or_none()

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=i18n.get_text("USER_NOT_FOUND", lang)
            )

        user, user_info = result

        # 构建返回数据：
        response_data = {
            "id": user.id,
            "email": user.email,
            "phone": user.phone,
            "wechat_openid": user.wechat_openid,
            "unionid": user.unionid,
            "is_active": user.is_active,
            "is_vip": user.is_vip,
            "vip_start_date": user.vip_start_date,
            "vip_expire_date": user.vip_expire_date,
            # "total_practice_time": user.total_practice_time,
            # "pitch_test_count": user.pitch_test_count,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }

        # 如果存在用户信息，添加到返回数据中
        if user_info:
            user_info_dict = {
                "nickname": user_info.nickname,
                "avatar_url": user_info.avatar_url,
                "gender": user_info.gender,
                "country": user_info.country,
                "province": user_info.province,
                "city": user_info.city,
                "language": user_info.language
            }
            response_data.update(user_info_dict)

        return response_data
    except Exception as e:
        logger.error(f"Failed to get user info: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
        )
