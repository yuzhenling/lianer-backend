from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from app.core.config import settings

# 创建异步引擎
engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,  # 基础连接池大小
    max_overflow=100,  # 最大溢出连接数
    pool_timeout=30,  # 连接超时时间
    pool_recycle=1800,  # 连接回收时间（30分钟）
    pool_pre_ping=True,  # 连接池健康检查
    echo=False  # 是否打印SQL语句
)

# 创建异步会话工厂
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话的异步生成器
    使用上下文管理器确保会话正确关闭
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

Base = declarative_base()