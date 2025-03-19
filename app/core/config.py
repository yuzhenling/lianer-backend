from pydantic_settings import BaseSettings
from typing import Optional
import secrets


class Settings(BaseSettings):
    PROJECT_NAME: str = "声之宝典"
    API_V1_STR: str = "/api/v1"
    
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
    WECHAT_APP_ID: Optional[str] = None
    WECHAT_APP_SECRET: Optional[str] = None
    
    # 音频处理配置
    AUDIO_UPLOAD_DIR: str = "uploads/audio"
    MAX_AUDIO_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_AUDIO_TYPES: list = ["audio/wav", "audio/mp3", "audio/m4a"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings() 