import datetime
import json
from typing import Optional, Literal

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, outerjoin, desc

from app.core import logger
from app.core.config import settings
from app.models.order import VipOrder
from app.models.user import User, UserInfo, CombineUser
from app.models.vip import Vip
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


async def get_current_user_vip(
        request: Request,
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
) -> CombineUser:
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
        # result = await db.execute(select(User,VipOrder).filter(User.id == int(user_id)))
        result = await db.execute(
            select(User, VipOrder, Vip)
            .select_from(User)
            .outerjoin(VipOrder, (User.id == VipOrder.user_id) &
                       (VipOrder.is_paid == True) &
                       (VipOrder.is_return == False))
            .outerjoin(Vip, VipOrder.vip_id == Vip.id)
            .where(
                User.id == int(user_id),
                User.vip_expire_date >= datetime.datetime.now()
            )
            .order_by(desc(Vip.id))
        )
        row = result.first()
        if row:
            user, order, vip = row
            if order is None or vip is None:
                order = None
                vip = None
        else:
            # 用户不存在
            user = None

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=i18n.get_text("USER_NOT_FOUND", lang)
            )

        combine_user = CombineUser(
            id=user.id,
            wechat_openid=user.wechat_openid,
            is_active=user.is_active,
            is_vip=user.is_vip,
            vip_start_date=user.vip_start_date,
            vip_expire_date=user.vip_expire_date,
            is_super_admin=user.is_super_admin,

        )
        if order is not None:
            combine_user.order_id = order.id
        if vip is not None:
            combine_user.vip_id = vip.id
            combine_user.vip_level = vip.level

        return combine_user
    except Exception as e:
        raise credentials_exception

@router.post("/auth/wechat-login", response_model=Token)
async def wechat_login(
    request: Request,
    login_data: WeChatLogin,
    db: Session = Depends(get_db)
):
    """
    微信小程序登录接口
    
    通过微信小程序的code进行用户登录认证，如果用户不存在则自动创建新用户。
    
    Args:
        request: FastAPI请求对象
        login_data: 包含微信登录code的请求体
        db: 数据库会话依赖
        
    Returns:
        Token: 包含访问令牌的响应对象
        
    Raises:
        HTTPException: 
            - 401: 微信code无效或登录失败
            - 500: 服务器内部错误
            
    Example:
        ```json
        {
            "code": "023Qc5000Yw1j24qL3000Yw1j2Qc50g"
        }
        ```
    """
    lang = get_language(request)
    
    try:
        wechat_data = await auth_service.verify_wechat_code(login_data.code)
        # wechat_data: dict = {"openid": "ox75Z7NkQ58loRuhVu9OoNHTDtJY", "session_key": "qNnx7kln91EW/xBBbqP85A=="}
        # wechat_data = json.dumps(reps)
        logger.info("wechat login:" + wechat_data.__str__())
        if not wechat_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=i18n.get_text("INVALID_WECHAT_CODE", lang)
            )
        # 查找或创建用户
        result = await db.execute(select(User).where(User.wechat_openid == wechat_data["openid"]))
        user: User = result.scalar_one_or_none()
        if not user:
            user = User(
                wechat_openid=wechat_data["openid"],
                unionid=wechat_data.get("unionid"),
                vip_start_date=datetime.datetime.now(),
                vip_expire_date=datetime.datetime.now()+datetime.timedelta(days=1),
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
    """
    更新用户信息接口
    
    更新当前登录用户的个人信息，包括昵称、头像、性别等基本信息。
    
    Args:
        request: FastAPI请求对象
        user_info: 用户信息更新请求体
        current_user: 当前登录用户对象
        db: 数据库会话依赖
        
    Returns:
        dict: 包含更新结果的响应对象
            - code: 状态码
            - message: 响应消息
            - data: 更新后的用户信息
            
    Raises:
        HTTPException:
            - 401: 未认证或认证失败
            - 500: 服务器内部错误
            
    Example:
        ```json
        {
            "nickname": "张三",
            "avatar_url": "https://example.com/avatar.jpg",
            "gender": "男",
            "country": "中国",
            "province": "广东",
            "city": "深圳",
            "language": "zh_CN"
        }
        ```
    """
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
    """
    获取用户信息接口
    
    获取当前登录用户的完整信息，包括基本信息和扩展信息。
    
    Args:
        request: FastAPI请求对象
        current_user: 当前登录用户对象
        db: 数据库会话依赖
        
    Returns:
        dict: 包含用户完整信息的响应对象
            - id: 用户ID
            - email: 邮箱
            - phone: 手机号
            - wechat_openid: 微信OpenID
            - unionid: 微信UnionID
            - is_active: 是否激活
            - is_vip: 是否VIP
            - vip_start_date: VIP开始日期
            - vip_expire_date: VIP过期日期
            - created_at: 创建时间
            - updated_at: 更新时间
            - nickname: 昵称
            - avatar_url: 头像URL
            - gender: 性别
            - country: 国家
            - province: 省份
            - city: 城市
            - language: 语言
            
    Raises:
        HTTPException:
            - 401: 未认证或认证失败
            - 404: 用户不存在
            - 500: 服务器内部错误
    """
    lang = get_language(request)
    try:
        # 使用 join 查询用户信息和用户基本信息
        # result = db.query(User, UserInfo).outerjoin(UserInfo, User.id == UserInfo.user_id).filter(User.id == current_user.id).first()
        result = await db.execute(select(User, UserInfo).select_from(outerjoin(User, UserInfo, User.id == UserInfo.user_id)).where(User.id == current_user.id))
        user, user_info = result.first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=i18n.get_text("USER_NOT_FOUND", lang)
            )

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
