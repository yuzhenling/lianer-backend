from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncEngine
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

from app.core.config import settings
from app.db.database import engine, get_db, Base
from app.middleware.logging import LoggingMiddleware
from app.api.v1 import auth_api, order_api, vip_api, piano_pitch_api, rhythm_api, melody_api, tuner_api, \
    payment_api, exam_api
from app.db.init_data import init_vip_levels, init_pitches, init_intervals, init_pitch_chord
from app.core.logger import logger
from fastapi.staticfiles import StaticFiles

# 导入所有模型以确保它们被注册到Base.metadata
from app.services.pitch_service import pitch_service
from app.services.vip_service import vip_service

async def create_tables(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

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
        await create_tables(engine=engine)
        
        # 初始化数据库数据
        db_gen = get_db()
        try:
            async for db in db_gen:
                logger.info("Initializing database data...")
                await init_vip_levels(db)

                await init_pitches(db)

                await init_intervals(db)

                await init_pitch_chord(db)

                logger.info("Loading VIP cache...")
                await vip_service.load_vip_cache(db)

                logger.info("Loading Pitch cache...")
                await pitch_service.load_pitch_cache(db)

                logger.info("building Pitch Group cache...")
                pitch_service.build_pitch_group_cache()

                logger.info("building Pitch Interval cache...")
                await pitch_service.build_pitch_interval_cache(db)

                logger.info("building Pitch Chord cache...")
                await pitch_service.build_pitch_chord_cache(db)
        finally:
            logger.info("Initializing database data done...")
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
app.add_middleware(HTTPSRedirectMiddleware)

# 注册路由
app.include_router(auth_api.router, prefix=settings.API_V1_STR)
app.include_router(vip_api.router, prefix=settings.API_V1_STR)
app.include_router(order_api.router, prefix=settings.API_V1_STR)
app.include_router(piano_pitch_api.router, prefix=settings.API_V1_STR)
app.include_router(rhythm_api.router, prefix=settings.API_V1_STR)
app.include_router(melody_api.router, prefix=settings.API_V1_STR)
app.include_router(tuner_api.router, prefix=settings.API_V1_STR)
# app.include_router(payment_api.router, prefix=settings.API_V1_STR)
app.include_router(exam_api.router, prefix=settings.API_V1_STR)



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

@app.get("/files/audio")
async def list_files():
    import os
    from pathlib import Path

    static_dir = Path(__file__).parent / "app" / "static" / "audio"
    print(f"Static dir: {static_dir}")

    if not static_dir.exists():
        raise HTTPException(status_code=500, detail=f"Static dir not found: {static_dir}")

    return os.listdir(static_dir)

@app.get("/files/audio/compress")
async def list_compress_files():
    import os
    from pathlib import Path

    static_dir = Path(__file__).parent / "app" / "static" / "compress"
    print(f"Static dir: {static_dir}")

    if not static_dir.exists():
        raise HTTPException(status_code=500, detail=f"Static dir not found: {static_dir}")

    return os.listdir(static_dir)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

for route in app.routes:
    print(f"{route.path}")
