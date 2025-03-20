from pydantic_settings import BaseSettings
from typing import Optional
import secrets


class Settings(BaseSettings):
    PROJECT_NAME: str = "声之宝典"
    API_V1_STR: str = "/api/v1"
    API_HOST: str = "https://api.shengyibaodian.com"  # API域名
    
    # PostgreSQL数据库配置
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "123456"
    POSTGRES_DB: str = "shengyibaodian"
    POSTGRES_PORT: str = "5432"
    
    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        """构建PostgreSQL数据库URL"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # JWT配置
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # 微信小程序配置
    WECHAT_APP_ID: str = "wx19a50120a8380422"
    WECHAT_APP_SECRET: str = "c129f82d2b3c42cac5bbf442ae128bd8"
    
    # 微信支付配置
    WECHAT_MCH_ID: str = "1234567890"  # 商户号
    WECHAT_PAY_SERIAL_NO: str = ""  # 商户证书序列号
    WECHAT_PAY_KEY: str = ""  # API v3密钥
    WECHAT_PAY_CERT_PATH: str = "cert/apiclient_cert.pem"  # 商户证书路径
    WECHAT_PAY_KEY_PATH: str = "cert/apiclient_key.pem"  # 商户私钥路径
    
    # 音频处理配置
    AUDIO_UPLOAD_DIR: str = "uploads/audio"
    MAX_AUDIO_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_AUDIO_TYPES: list = ["audio/wav", "audio/mp3", "audio/m4a"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings() 