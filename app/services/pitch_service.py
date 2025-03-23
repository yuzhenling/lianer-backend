import copy
from typing import Dict, List, Any, Coroutine
from urllib.parse import quote

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logger import logger
from app.db.base import SessionLocal
from app.models.pitch import Pitch, PitchGroup, PITCH_GROUP_NAMES, PITCH_GROUP_RANGES, PitchInterval, Interval, \
    PitchIntervalPair, PitchChord, Chord


class PitchService:
    _instance = None
    PITCH_CACHE: Dict[int, Pitch] = {}  # ID -> Pitch对象的缓存
    PITCH_GROUP_CACHE: Dict[int, PitchGroup] = {}  # ID -> PitchGroup对象的缓存
    PITCH_INTERVAL_CACHE: Dict[int, PitchInterval] = {}  # ID -> PitchInterval对象的缓存
    PITCH_CHORD_CACHE: Dict[int, PitchChord] = {}  # ID -> PitchChord对象的缓存

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
                self.PITCH_CACHE[pitch.pitch_number] = pitch

            # 构建音组缓存
            self.build_pitch_group_cache()
            # 构建音程缓存
            self.build_pitch_interval_cache()

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

    def build_pitch_interval_cache(self):
        """构建音程缓存"""
        try:
            # 清空现有音程缓存
            self.PITCH_INTERVAL_CACHE.clear()
            
            # 音程与半音数的映射
            interval_semitones = {
                # 单音程
                Interval.MINOR_SECOND: 1,    # 小二度
                Interval.MAJOR_SECOND: 2,    # 大二度
                Interval.MINOR_THIRD: 3,     # 小三度
                Interval.MAJOR_THIRD: 4,     # 大三度
                Interval.PERFECT_FOURTH: 5,  # 纯四度
                Interval.TRITONE: 6,         # 增四度/减五度
                Interval.PERFECT_FIFTH: 7,   # 纯五度
                Interval.MINOR_SIXTH: 8,     # 小六度
                Interval.MAJOR_SIXTH: 9,     # 大六度
                Interval.MINOR_SEVENTH: 10,  # 小七度
                Interval.MAJOR_SEVENTH: 11,  # 大七度
                Interval.PERFECT_OCTAVE: 12, # 纯八度
                # 复音程
                Interval.MINOR_NINTH: 13,    # 小九度
                Interval.MAJOR_NINTH: 14,    # 大九度
                Interval.MINOR_TENTH: 15,    # 小十度
                Interval.MAJOR_TENTH: 16,    # 大十度
                Interval.PERFECT_ELEVENTH: 17,  # 纯十一度
                Interval.AUGMENTED_ELEVENTH: 18,  # 增十一度
                Interval.PERFECT_TWELFTH: 19,    # 纯十二度
                Interval.MINOR_THIRTEENTH: 20,   # 小十三度
                Interval.MAJOR_THIRTEENTH: 21,   # 大十三度
                Interval.MINOR_FOURTEENTH: 22,   # 小十四度
                Interval.MAJOR_FOURTEENTH: 23,   # 大十四度
                Interval.PERFECT_FIFTEENTH: 24,  # 纯十五度
            }

            index = 1
            # 为每个音程创建缓存
            for interval, semitones in interval_semitones.items():
                pitch_pairs = []
                # 遍历所有音高，找出符合当前音程的音高对
                for base_pitch in self.PITCH_CACHE.values():
                    target_number = base_pitch.pitch_number + semitones
                    if target_number <= 88:  # 确保不超过钢琴最高音
                        if target_pitch := self.PITCH_CACHE.get(target_number):
                            pitch_interval_pair = PitchIntervalPair(
                                first=base_pitch,
                                second=target_pitch
                            )
                            pitch_pairs.append(pitch_interval_pair)

                # 创建音程对象并缓存
                pitch_interval = PitchInterval(
                    index=index,
                    interval=interval,
                    semitones=semitones,
                    list=pitch_pairs,
                    count=len(pitch_pairs),
                )
                self.PITCH_INTERVAL_CACHE[semitones] = pitch_interval
                index += 1

            logger.info(f"Successfully built Pitch Interval cache with {len(self.PITCH_INTERVAL_CACHE)} intervals")
        except Exception as e:
            logger.error("Failed to build Pitch Interval cache", exc_info=True)
            raise e

    def build_pitch_chord_cache(self):
        """构建和弦缓存"""
        try:
            # 清空现有音程缓存
            self.PITCH_CHORD_CACHE.clear()

            index = 1
            # 为每个音程创建缓存
            for chord in Chord:
                intervals = chord.intervals
                pitch_pairs: List[List] = []
                # 遍历所有音高，找出符合当前音程的音高对
                for base_pitch in self.PITCH_CACHE.values():
                    pitch_chord_pair = []
                    pitch_chord_pair.append(base_pitch)
                    for interval in intervals:
                        target_number = base_pitch.pitch_number + interval
                        if target_number <= 88:  # 确保不超过钢琴最高音
                            if target_pitch := self.PITCH_CACHE.get(target_number):
                                pitch_chord_pair.append(target_pitch)
                    if pitch_chord_pair and len(pitch_chord_pair) == len(intervals)+1:
                        pitch_pairs.append(pitch_chord_pair)

                if pitch_pairs:
                    # 创建音程对象并缓存
                    pitch_chord = PitchChord(
                        index = index,
                        value = chord.value,
                        cn_value = chord.cn_value,
                        list = pitch_pairs,
                        count = len(pitch_pairs),
                    )
                    self.PITCH_CHORD_CACHE[index] = pitch_chord
                index += 1

            logger.info(f"Successfully built Pitch chord cache with {len(self.PITCH_CHORD_CACHE)} intervals")
        except Exception as e:
            logger.error("Failed to build Pitch chord cache", exc_info=True)
            raise e

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

    async def get_all_intervals(self) -> List[PitchInterval]:
        """获取所有音程"""
        try:
            return list(self.PITCH_INTERVAL_CACHE.values())
        except Exception as e:
            logger.error("Failed to get all intervals", exc_info=True)
            raise e

    async def get_interval_by_index(self, index: int) -> PitchInterval:
        """根据索引获取特定音程"""
        try:
            return self.PITCH_INTERVAL_CACHE[index]
        except Exception as e:
            logger.error(f"Failed to get interval with index {index}", exc_info=True)
            raise e

    async def get_all_chords(self) -> List[PitchChord]:
        """获取所有音程"""
        try:
            return list(self.PITCH_CHORD_CACHE.values())
        except Exception as e:
            logger.error("Failed to get all chords", exc_info=True)
            raise e

    async def get_chord_by_index(self, index: int) -> PitchChord:
        """根据索引获取特定音程"""
        try:
            return self.PITCH_CHORD_CACHE[index]
        except Exception as e:
            logger.error(f"Failed to get chord with index {index}", exc_info=True)
            raise e

pitch_service = PitchService()