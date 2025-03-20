from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.middleware.logging import LoggingMiddleware
from app.api.v1 import auth, pitch

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
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

# 注册路由
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(pitch.router, prefix=settings.API_V1_STR) 