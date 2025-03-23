from typing import Dict, List

from sqlalchemy.orm import Session

from app.core.logger import logger
from app.db.base import SessionLocal
from app.models.pitch import Pitch


class PitchService:
    _instance = None
    _pitch_cache: Dict[int, Pitch] = {}  # ID -> Pitch对象的缓存

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
            pitches = db.query(Pitch).all()
            # 清空现有缓存
            self._pitch_cache.clear()

            # 更新缓存
            for pitch in pitches:
                self._pitch_cache[pitch.pitch_number] = pitch

            logger.info(f"Successfully loaded {len(pitches)} Pitch into cache")
        except Exception as e:
            logger.error("Failed to load Pitch cache", exc_info=True)
            raise e

    async def get_all_pitch(self) -> List[Pitch]:
        try:
            if not self._pitch_cache:
                db = SessionLocal()
                try:
                    await self.load_pitch_cache(db)
                except Exception as e:
                    raise e
                finally:
                    db.close()
            return list(self._pitch_cache.values())
        except Exception as e:
            logger.error("Failed to load Pitch cache", exc_info=True)
            raise e

    async def get_pitch_by_number(self, number: int) -> Pitch:
        try:
            return self._pitch_cache[number]
        except Exception as e:
            logger.error("Failed to load Pitch cache", exc_info=True)
            raise e

pitch_service = PitchService()