from typing import Dict, Optional
from fastapi import Request
from enum import Enum
import os
from pathlib import Path


class Language(str, Enum):
    ZH = "zh"
    EN = "en"


class I18nService:
    def __init__(self):
        self.translations: Dict[str, Dict[str, str]] = {}
        self._load_translations()
        
    def _load_translations(self):
        """加载所有语言的翻译文件"""
        base_path = Path(__file__).parent.parent / "locales"
        
        for lang in Language:
            self.translations[lang] = {}
            properties_file = base_path / lang.value / "messages.properties"
            
            if properties_file.exists():
                with open(properties_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        # 跳过空行和注释
                        if not line or line.startswith("#"):
                            continue
                        
                        # 解析key=value格式
                        if "=" in line:
                            key, value = line.split("=", 1)
                            self.translations[lang][key.strip()] = value.strip()
    
    def get_text(self, key: str, lang: str = Language.ZH) -> str:
        """获取指定语言的文本"""
        return self.translations.get(lang, {}).get(key, key)
    
    def reload(self):
        """重新加载所有翻译文件"""
        self.translations.clear()
        self._load_translations()


# 创建全局i18n服务实例
i18n = I18nService()


def get_language(request: Optional[Request] = None) -> str:
    """获取当前请求的语言"""
    # 如果没有Request对象，默认返回中文
    if not request:
        return Language.ZH
        
    # 从请求头中获取语言设置
    accept_language = request.headers.get("accept-language", Language.ZH)
    
    # 简单处理，如果包含zh则返回中文，否则返回英文
    return Language.ZH if "zh" in accept_language.lower() else Language.EN 