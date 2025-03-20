import logging
import json
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler
import sys
from typing import Any, Dict

# 创建日志目录
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# 日志格式
class CustomJsonFormatter(logging.Formatter):
    def __init__(self):
        super().__init__()
    
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = {
                "type": str(record.exc_info[0].__name__),
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
            
        # 添加额外字段
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "ip"):
            log_data["ip"] = record.ip
        if hasattr(record, "path"):
            log_data["path"] = record.path
        if hasattr(record, "method"):
            log_data["method"] = record.method
            
        return json.dumps(log_data, ensure_ascii=False)

# 创建logger
logger = logging.getLogger("shengyibaodian")
logger.setLevel(logging.INFO)

# 控制台处理器
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(CustomJsonFormatter())
logger.addHandler(console_handler)

# 文件处理器 (按天轮转)
file_handler = RotatingFileHandler(
    filename=log_dir / "app.log",
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=30,  # 保留30个备份
    encoding="utf-8"
)
file_handler.setFormatter(CustomJsonFormatter())
logger.addHandler(file_handler)

# 错误日志单独记录
error_file_handler = RotatingFileHandler(
    filename=log_dir / "error.log",
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=30,  # 保留30个备份
    encoding="utf-8"
)
error_file_handler.setLevel(logging.ERROR)
error_file_handler.setFormatter(CustomJsonFormatter())
logger.addHandler(error_file_handler) 