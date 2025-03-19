from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.core.config import settings

# 创建PostgreSQL引擎，移除SQLite特定的connect_args
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # 添加连接池健康检查
    pool_size=200,         # 连接池大小
    max_overflow=100      # 最大溢出连接数
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base() 