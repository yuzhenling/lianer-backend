from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from starlette.staticfiles import StaticFiles

from app.core.config import settings
from app.middleware.logging import LoggingMiddleware
from app.api.v1 import auth_api, pitch_api, order_api, vip_api, piano_pitch_api, rhythm_api, melody_api, tuner_api
from app.db.init_data import init_vip_levels, init_pitches, init_intervals, init_pitch_chord
from app.db.base import SessionLocal, Base, engine
from app.core.logger import logger

# 导入所有模型以确保它们被注册到Base.metadata
from app.models import user, pitch, order
from app.services.pitch_service import pitch_service
from app.services.vip_service import vip_service

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用程序生命周期管理
    在应用启动时执行初始化，在应用关闭时执行清理
    """
    # 启动时执行
    try:
        # 创建所有表
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        
        # 初始化数据库数据
        db = SessionLocal()
        try:
            logger.info("Initializing database data...")
            init_vip_levels(db)

            init_pitches(db)

            init_intervals(db)

            init_pitch_chord(db)

            logger.info("Loading VIP cache...")
            await vip_service.load_vip_cache(db)

            logger.info("Loading Pitch cache...")
            await pitch_service.load_pitch_cache(db)

            logger.info("building Pitch Group cache...")
            pitch_service.build_pitch_group_cache()

            logger.info("building Pitch Interval cache...")
            pitch_service.build_pitch_interval_cache(db)

            logger.info("building Pitch Chord cache...")
            pitch_service.build_pitch_chord_cache(db)
        finally:
            db.close()
    except Exception as e:
        logger.error("Failed to initialize application", exc_info=True)
        raise e

    yield

    # 关闭时执行
    logger.info("Shutting down application...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)


# app.mount("/static", StaticFiles(directory=Path("app/static")), name="static")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# 添加日志中间件
app.add_middleware(LoggingMiddleware)

# 注册路由
app.include_router(auth_api.router, prefix=settings.API_V1_STR)
app.include_router(vip_api.router, prefix=settings.API_V1_STR)
app.include_router(order_api.router, prefix=settings.API_V1_STR)
app.include_router(piano_pitch_api.router, prefix=settings.API_V1_STR)
app.include_router(rhythm_api.router, prefix=settings.API_V1_STR)
app.include_router(melody_api.router, prefix=settings.API_V1_STR)

app.include_router(tuner_api.router, prefix=settings.API_V1_STR)



@app.get("/")
async def root():
    return {
        "message": "Welcome to 声之宝典 API",
        "version": "1.0.0",
        "docs_url": f"/docs"
    }


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
