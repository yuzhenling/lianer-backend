import copy
from typing import Dict, List, Any, Coroutine
from urllib.parse import quote

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logger import logger
from app.db.base import SessionLocal
from app.models.pitch import Pitch, PitchGroup, PITCH_GROUP_NAMES, PITCH_GROUP_RANGES


class PitchService:
    _instance = None
    PITCH_CACHE: Dict[int, Pitch] = {}  # ID -> Pitch对象的缓存
    PITCH_GROUP_CACHE: Dict[int, PitchGroup] = {}  # ID -> PitchGroup对象的缓存

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PitchService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # 单例模式，避免重复初始化
        if not hasattr(self, '_initialized'):
            self._initialized = True

    async def load_pitch_cache(self, db: Session) -> None:
        """从数据库加载所有Pitch数据到缓存"""
        try:
            pitches = db.query(Pitch).order_by(Pitch.pitch_number).all()
            # 清空现有缓存
            self.PITCH_CACHE.clear()

            # 更新缓存
            for pitch in pitches:
            #     url = quote(pitch.url)
            #     pitch.url = f"{settings.API_HOST}{settings.API_V1_STR}{url}"
                self.PITCH_CACHE[pitch.pitch_number] = pitch

            #音组
            for pitch in pitches:
                self.PITCH_CACHE[pitch.pitch_number] = pitch

            logger.info(f"Successfully loaded {len(pitches)} Pitch into cache")
        except Exception as e:
            logger.error("Failed to load Pitch cache", exc_info=True)
            raise e

    def build_pitch_group_cache(self):
        i = 1
        for group_name, (start, end) in zip(PITCH_GROUP_NAMES, PITCH_GROUP_RANGES):
            # 获取当前音组的所有 Pitch 实例
            pitches = [pitch for pitch in self.PITCH_CACHE.values() if start <= pitch.pitch_number <= end]

            # 构建 PitchGroup 实例
            pitch_group = PitchGroup(
                index = i,
                name=group_name,
                pitches=pitches,
                count=len(pitches),
            )

            # 添加到缓存
            self.PITCH_GROUP_CACHE[i] = pitch_group
            i += 1

        logger.info(f"Successfully build Pitch Group into cache")

    async def get_all_pitch(self) -> List[Pitch]:
        try:
            return list(self.PITCH_CACHE.values())
        except Exception as e:
            logger.error("Failed to load Pitch cache", exc_info=True)
            raise e

    async def get_pitch_by_number(self, number: int) -> Pitch:
        try:
            return self.PITCH_CACHE[number]
        except Exception as e:
            logger.error("Failed to load Pitch cache", exc_info=True)
            raise e

    async def get_pitch_by_name(self, name: str) -> List[Pitch]:
        try:
            filter_data = {k:v for k,v in self.PITCH_CACHE.items() if name == v.name or (v.alias is not None and name == v.alias)}
            return list(filter_data.values())
        except Exception as e:
            logger.error("Failed to load Pitch cache", exc_info=True)
            raise e

    async def get_all_pitchgroups(self) -> List[PitchGroup]:
        try:
            return list(self.PITCH_GROUP_CACHE.values())
        except Exception as e:
            logger.error("Failed to load Pitch cache", exc_info=True)
            raise e

pitch_service = PitchService()