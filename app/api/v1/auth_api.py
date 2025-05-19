import json

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel

from app.core import logger
from app.core.config import settings
from app.models.user import User
from app.services.auth_service import AuthService
from app.db.base import SessionLocal
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


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
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
            
        user = db.query(User).filter(User.id == int(user_id)).first()
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
        if not wechat_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=i18n.get_text("INVALID_WECHAT_CODE", lang)
            )
        
        # 查找或创建用户
        user = db.query(User).filter(User.wechat_openid == wechat_data["openid"]).first()
        if not user:
            user = User(
                wechat_openid=wechat_data["openid"],
                unionid=wechat_data.get("unionid"),
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
    except Exception as e:
        logger.error(e, status.HTTP_401_UNAUTHORIZED)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=i18n.get_text("WECHAT_LOGIN_FAILED", lang)
        )