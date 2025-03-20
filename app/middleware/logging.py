import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import traceback

from app.core.logger import logger
from app.core.i18n import i18n, get_language


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        # 生成请求ID
        request_id = str(uuid.uuid4())
        
        # 获取请求开始时间
        start_time = time.time()
        
        # 记录请求信息
        logger.info(
            "Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": str(request.url.path),
                "ip": request.client.host if request.client else None,
            }
        )
        
        response = None
        try:
            # 调用下一个中间件或路由处理器
            response = await call_next(request)
            
            # 记录响应信息
            process_time = time.time() - start_time
            logger.info(
                "Request completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": str(request.url.path),
                    "status_code": response.status_code,
                    "process_time": f"{process_time:.3f}s"
                }
            )
            
            return response
            
        except Exception as e:
            # 获取语言设置
            lang = get_language(request)
            
            # 记录异常信息
            process_time = time.time() - start_time
            logger.error(
                "Request failed",
                exc_info=True,
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": str(request.url.path),
                    "process_time": f"{process_time:.3f}s",
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }
            )
            
            # 返回500错误
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=500,
                content={
                    "detail": i18n.get_text("INTERNAL_SERVER_ERROR", lang),
                    "request_id": request_id
                }
            ) 