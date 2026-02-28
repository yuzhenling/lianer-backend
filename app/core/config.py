from pathlib import Path

from pydantic_settings import BaseSettings
from typing import Optional
import secrets


class Settings(BaseSettings):
    PROJECT_NAME: str = ""
    API_V1_STR: str = "/api/v1"
    # API_HOST: str = "https://api.shengyibaodian.com"  # API域名


    APP_DIR: str = Path(__file__).resolve().parent.parent.as_posix()

    # PostgreSQL数据库配置
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""
    POSTGRES_PORT: str = ""

    # 数据库连接池配置
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 100
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800

    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        """构建PostgreSQL数据库URL"""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # JWT配置
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # 微信小程序配置
    # WECHAT_APP_ID: str = ""
    # WECHAT_APP_SECRET: str = ""

    WECHAT_APP_ID: str = ""
    WECHAT_APP_SECRET: str = ""
    
    # 微信支付配置
    # WECHAT_MCH_ID: str = ""  # 商户号
    # WECHAT_PAY_SERIAL_NO: str = ""  # 商户证书序列号
    # WECHAT_PAY_KEY: str = ""  # API v3密钥
    # WECHAT_PAY_CERT_PATH: str = APP_DIR+"/wepay/apiclient_cert.pem"  # 商户证书路径
    # WECHAT_PAY_KEY_PATH: str = APP_DIR+"/wepay/apiclient_key.pem"  # 商户私钥路径
    # WECHAT_NOTIFY_URL: str = "http://:8000/api/v1/order/wechat-notify"

    WECHAT_MCH_ID: str = "1717958217"  # 商户号
    WECHAT_PAY_SERIAL_NO: str = ""  # 商户证书序列号
    WECHAT_PAY_KEY: str = ""  # API v3密钥
    WECHAT_PAY_CERT_PATH: str = APP_DIR + "/wepay/apiclient_cert.pem"  # 商户证书路径
    WECHAT_PAY_KEY_PATH: str = APP_DIR + "/wepay/apiclient_key.pem"  # 商户私钥路径
    WECHAT_NOTIFY_URL: str = "https://www..cn/api/v1/order/wechat-notify"
    
    # 音频处理配置
    AUDIO_UPLOAD_DIR: str = "uploads/audio"
    MAX_AUDIO_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_AUDIO_TYPES: list = ["audio/wav", "audio/mp3", "audio/m4a"]
    
    # DeepSeek API settings
    DEEPSEEK_API_KEY: str = "sk-"
    DEEPSEEK_API_URL: str = "https://api.deepseek.com/v1/chat/completions"
    

    class Config:
        env_file = ".env"
        case_sensitive = True



settings = Settings() 
