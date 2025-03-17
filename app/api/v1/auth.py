from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional
from pydantic import BaseModel

from app.core.config import settings
from app.services.auth import AuthService
from app.db.base import SessionLocal
from app.models.user import User, VipLevel

router = APIRouter()
auth_service = AuthService()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")


class Token(BaseModel):
    access_token: str
    token_type: str


class WeChatLogin(BaseModel):
    code: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = auth_service.verify_token(token)
    if not payload:
        raise credentials_exception
        
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
        
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
        
    return user


@router.post("/auth/wechat-login", response_model=Token)
async def wechat_login(
    login_data: WeChatLogin,
    db: Session = Depends(get_db)
):
    """微信小程序登录"""
    wechat_data = await auth_service.verify_wechat_code(login_data.code)
    if not wechat_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid WeChat code"
        )
    
    # 查找或创建用户
    user = db.query(User).filter(User.wechat_openid == wechat_data["openid"]).first()
    if not user:
        user = User(
            wechat_openid=wechat_data["openid"],
            vip_level=VipLevel.FREE
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
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