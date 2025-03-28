import random
from typing import Dict, List

from sqlalchemy.orm import Session

from app.core.logger import logger
from app.models.exam import Question, SinglePitchExam, ExamType, GroupPitchExam, GroupQuestion
from app.models.pitch import Pitch, PitchGroup, PITCH_GROUP_NAMES, PITCH_GROUP_RANGES, PitchInterval, Interval, \
    PitchIntervalPair, PitchChord, Chord


class PitchService:
    _instance = None
    PITCH_CACHE: Dict[int, Pitch] = {}  # ID -> Pitch对象的缓存
    PITCH_GROUP_CACHE: Dict[int, PitchGroup] = {}  # ID -> PitchGroup对象的缓存
    PITCH_INTERVAL_CACHE: Dict[int, PitchInterval] = {}  # ID -> PitchInterval对象的缓存
    PITCH_INTERVAL_NAME_CACHE: List[Dict[int, str]] = {}  # ID -> PitchInterval对象的缓存
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
            self.PITCH_INTERVAL_NAME_CACHE.clear()

            self.PITCH_INTERVAL_NAME_CACHE = {
                1: "小二度",
                2: "大二度",
                3: "小三度",
                4: "大三度",
                5: "纯四度",
                6: "增四度",
                7: "减五度",
                8: "纯五度",
                9: "小六度",
                10: "大六度",
                11: "小七度",
                12: "大七度",
                13: "纯八度",
                # 复音程
                14: "小九度",
                15: "大九度",
                16: "小十度",
                17: "大十度",
                18: "纯十一度",
                19: "增十一度",
                20: "减十二度",
                21: "纯十二度",
                22: "小十三度",
                23: "大十三度",
                24: "小十四度",
                25: "大十四度",
                26: "纯十五度"
            }
            
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

    #, pitch_black_keys: List[str], mode_key:int
    async def get_pitches_by_setting(self, min_pitch_number: int, max_pitch_number: int) -> List[Pitch]:
        try:
            list = []
            for i in range(min_pitch_number, max_pitch_number+1):
                list.append(self.PITCH_CACHE[i])
            return list
        except Exception as e:
            logger.error("Failed to load Pitch cache", exc_info=True)
            raise e

    async def generate_single_exam(self, min_pitch_number: int, max_pitch_number: int, pitch_black_keys: List[str]) -> SinglePitchExam:
        """根据设置生成考试题目"""
        # 获取指定音域范围内的所有可用音高
        available_pitches = await self.get_pitches_by_range_black(min_pitch_number, max_pitch_number, pitch_black_keys)

        # 生成指定数量的随机题目
        questions = self.generate_single_questions(available_pitches, ExamType.SINGLE.question_num)

        # 创建考试对象
        exam = SinglePitchExam(
            id = 0,
            user_id = 0,
            exam_type= ExamType.SINGLE._value,
            question_num=ExamType.SINGLE.question_num,
            questions=questions,
            correct_number = 0,
            wrong_number = 0,
        )
        return exam

    def generate_single_questions(self, available_pitches: List[Pitch], question_num: int) -> List[Question]:
        """生成指定数量的随机题目"""
        questions = []
        index = 1
        while len(questions) < question_num:
            # 随机选择一个音高
            pitch = random.choice(available_pitches)
            questions.append(Question(
                id=index,
                pitch=pitch,
            ))
            index += 1

        return questions

    async def generate_group_exam(self, min_pitch_number: int, max_pitch_number: int, pitch_black_keys: List[str], count: int ) -> SinglePitchExam:
        """根据设置生成考试题目"""
        # 获取指定音域范围内的所有可用音高
        available_pitches = await self.get_pitches_by_range_black(min_pitch_number, max_pitch_number, pitch_black_keys)

        # 生成指定数量的随机题目
        questions = self.generate_group_questions(available_pitches, ExamType.GROUP.question_num, count)

        # 创建考试对象
        exam = GroupPitchExam(
            id = 0,
            user_id = 0,
            exam_type= ExamType.GROUP._value,
            question_num=ExamType.GROUP.question_num,
            questions=questions,
            correct_number = 0,
            wrong_number = 0,
        )
        return exam

    def generate_group_questions(self, available_pitches: List[Pitch], question_num: int, count: int) -> List[Question]:
        """生成指定数量的随机题目"""
        questions = []
        index = 1
        while len(questions) < question_num:
            # 随机选择一个音高
            pitches = random.choices(available_pitches, k=count)
            questions.append(GroupQuestion(
                id=index,
                pitches=pitches,
            ))
            index += 1

        return questions

    async def get_pitches_by_range_black(self,min_pitch_number: int, max_pitch_number: int, pitch_black_keys: List[str]) -> List[Pitch]:
        pitches = await self.get_pitches_by_setting(min_pitch_number, max_pitch_number)
        available_pitches = []
        for p in pitches:
            if not p.name.__contains__("#"):
                available_pitches.append(p)
                continue
            for pitch_black_key in pitch_black_keys:
                if p.name.__contains__("#") and pitch_black_key in p.name:
                    available_pitches.append(p)
                    continue
        return available_pitches
    # def create_student_exam(self, user_id: int, exam_id: int) -> StudentExam:
    #     """创建学生考试记录"""
    #     return StudentExam(
    #         id=random.randint(1000, 9999),  # 临时ID生成方式
    #         user_id=user_id,
    #         exam_id=exam_id
    #     )
    #
    # def update_student_exam_result(
    #         self,
    #         student_exam: StudentExam,
    #         correct: bool
    # ) -> StudentExam:
    #     """更新学生考试结果"""
    #     if correct:
    #         student_exam.correct_number += 1
    #     else:
    #         student_exam.wrong_number += 1
    #
    #     # 如果所有题目都已完成，设置完成时间
    #     if student_exam.correct_number + student_exam.wrong_number == student_exam.question_num:
    #         student_exam.completed_at = datetime.now()
    #
    #     return student_exam

pitch_service = PitchService()