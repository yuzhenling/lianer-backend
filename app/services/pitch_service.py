import random
from dataclasses import replace
from typing import Dict, List, Any

from numba.core.event import start_event
from sqlalchemy.orm import Session

from app.api.v1.schemas.request.pitch_request import PitchIntervalSettingRequest, PitchChordSettingRequest
from app.core.logger import logger
from app.models.chord_inversion import ChordInversion
from app.models.exam import Question, SinglePitchExam, ExamType, GroupPitchExam, GroupQuestion, IntervalQuestion, \
    PitchIntervalExam, ChordQuestion, PitchChordExam
from app.models.pitch import Pitch, PitchGroup, PITCH_GROUP_NAMES, PITCH_GROUP_RANGES, PitchInterval, Interval, \
    PitchIntervalPair, PitchChord, ChordEnum, PitchIntervalWithPitches, PitchIntervalType, PitchConcordanceType, \
    PitchChordTypeMapping, PitchChordType
from app.models.pitch_setting import AnswerMode, ConcordanceChoice, ChordAnswerMode


class PitchService:
    _instance = None
    PITCH_CACHE: Dict[int, Pitch] = {}  # ID -> Pitch对象的缓存
    PITCH_GROUP_CACHE: Dict[int, PitchGroup] = {}  # ID -> PitchGroup对象的缓存
    PITCH_INTERVAL_TYPE_CACHE: Dict[int, PitchIntervalType] = {}  # ID -> PitchInterval对象的缓存
    PITCH_INTERVAL_CONCORDANCE_TYPE_CACHE: Dict[int, PitchConcordanceType] = {}  # ID -> PitchInterval对象的缓存
    PITCH_INTERVAL_CACHE: Dict[int, PitchIntervalWithPitches] = {}  # ID -> PitchInterval对象的缓存
    PITCH_INTERVAL_HARMONIC_CACHE: Dict[int, List[Pitch]] = {}  # ID -> PitchInterval对象的缓存
    PITCH_CHORD_TYPE_CACHE: Dict[int, PitchChordType] = {}  # ID -> PitchChord对象的缓存
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

            # # 构建音组缓存
            # self.build_pitch_group_cache()
            # # 构建音程缓存
            # self.build_pitch_interval_cache(db)

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

    def build_pitch_interval_type_cache(self, db: Session):
        try:
            # 清空现有音程缓存
            self.PITCH_INTERVAL_TYPE_CACHE.clear()
            pitch_interval_types = db.query(PitchIntervalType).all()
            for pit in pitch_interval_types:
                self.PITCH_INTERVAL_TYPE_CACHE[pit.id] = pit

        except Exception as e:
            logger.error("Failed to build Pitch Interval cache", exc_info=True)
            raise e

    def build_pitch_concordance_type_cache(self, db: Session):
        try:
            # 清空现有音程缓存
            self.PITCH_INTERVAL_CONCORDANCE_TYPE_CACHE.clear()
            pitch_concordance_types = db.query(PitchConcordanceType).all()
            for pct in pitch_concordance_types:
                self.PITCH_INTERVAL_CONCORDANCE_TYPE_CACHE[pct.id] = pct

        except Exception as e:
            logger.error("Failed to build Pitch Concordance cache", exc_info=True)
            raise e

    def build_pitch_interval_cache(self, db: Session):
        """构建音程缓存"""
        try:
            self.build_pitch_interval_type_cache(db)
            self.build_pitch_concordance_type_cache(db)
            # 清空现有音程缓存
            self.PITCH_INTERVAL_CACHE.clear()
            pitch_intervals = db.query(PitchInterval).all()

            # 为每个音程创建缓存
            for pi in pitch_intervals:
                pitch_pairs = []
                # 遍历所有音高，找出符合当前音程的音高对
                for base_pitch in self.PITCH_CACHE.values():
                    target_number: int = int(base_pitch.pitch_number) + int(pi.semitone_number)
                    if target_number <= 88:  # 确保不超过钢琴最高音
                        if target_pitch := self.PITCH_CACHE.get(target_number):
                            pitch_interval_pair = PitchIntervalPair(
                                first=base_pitch,
                                second=target_pitch
                            )
                            pitch_pairs.append(pitch_interval_pair)

                # 创建音程对象并缓存
                pitch_interval_with_pair = PitchIntervalWithPitches(
                    id=pi.id,
                    name=pi.name,
                    semitone_number=pi.semitone_number,
                    type_id=pi.type_id,
                    type_name=self.PITCH_INTERVAL_TYPE_CACHE[pi.type_id].name,
                    black=pi.black,
                    concordance_id=pi.concordance_id,
                    concordance_name=self.PITCH_INTERVAL_CONCORDANCE_TYPE_CACHE[pi.concordance_id].name,
                    pitch_pairs=pitch_pairs,
                )
                self.PITCH_INTERVAL_CACHE[pi.id] = pitch_interval_with_pair

            logger.info(f"Successfully built Pitch Interval cache with {len(self.PITCH_INTERVAL_CACHE)} intervals")
        except Exception as e:
            logger.error("Failed to build Pitch Interval cache", exc_info=True)
            raise e



    def build_pitch_chord_cache(self, db: Session):
        """构建和弦缓存"""
        try:
            self.build_pitch_chord_type_cache(db)
            # 清空现有音程缓存
            self.PITCH_CHORD_CACHE.clear()


            pitch_chords = db.query(PitchChordTypeMapping).all()

            # 为每个音程创建缓存
            for chord in pitch_chords:
                interval1 = chord.interval_1
                interval2 = chord.interval_2
                interval3 = chord.interval_3
                pitch_pairs: List[List] = []

                # 遍历所有音高，找出符合当前音程的音高对
                for base_pitch in self.PITCH_CACHE.values():
                    pitch_chord_pair = []
                    pitch_chord_pair.append(base_pitch)
                    second_pitch_number = base_pitch.pitch_number + interval1
                    third_pitch_number = base_pitch.pitch_number + interval2
                    fourth_pitch_number = base_pitch.pitch_number + interval3 if interval3 is not None else None

                    if second_pitch_number <= 88:  # 确保不超过钢琴最高音
                        if second_pitch := self.PITCH_CACHE.get(second_pitch_number):
                            pitch_chord_pair.append(second_pitch)
                        if third_pitch_number <= 88:
                            if third_pitch := self.PITCH_CACHE.get(third_pitch_number):
                                pitch_chord_pair.append(third_pitch)
                            if fourth_pitch_number is not None and fourth_pitch_number <= 88:
                                if fourth_pitch := self.PITCH_CACHE.get(fourth_pitch_number):
                                    pitch_chord_pair.append(fourth_pitch)
                    else:
                        continue

                    if pitch_chord_pair and len(pitch_chord_pair) == chord.get_interval_count() +1:
                        pitch_pairs.append(pitch_chord_pair)

                if pitch_pairs:
                    # 创建音程对象并缓存
                    pitch_chord = PitchChord(
                        index = chord.id,
                        name = chord.name,
                        pair = pitch_pairs,
                        count = len(pitch_pairs),
                        is_three = True if self.PITCH_CHORD_TYPE_CACHE[chord.type_id].name.__contains__("three") else False,
                        simple_name = chord.simple_name,
                        type_id = chord.type_id,
                        type_name = self.PITCH_CHORD_TYPE_CACHE[chord.type_id].name,
                    )
                    self.PITCH_CHORD_CACHE[chord.id] = pitch_chord

            logger.info(f"Successfully built Pitch chord cache with {len(self.PITCH_CHORD_CACHE)} intervals")
        except Exception as e:
            logger.error("Failed to build Pitch chord cache", exc_info=True)
            raise e

    def build_pitch_chord_type_cache(self, db: Session):
        self.PITCH_CHORD_TYPE_CACHE.clear()
        chord_types = db.query(PitchChordType).all()
        for chord_type in chord_types:
            self.PITCH_CHORD_TYPE_CACHE[chord_type.id] = chord_type

    async def get_all_pitch(self) -> List[Pitch]:
        try:
            return list(self.PITCH_CACHE.values())
        except Exception as e:
            logger.error("Failed to load Pitch cache", exc_info=True)
            raise e

    def get_pitch_by_number(self, number: int) -> Pitch:
        try:
            return self.PITCH_CACHE[number]
        except Exception as e:
            logger.error("Failed to load Pitch cache", exc_info=True)
            raise e

    def get_pitch_by_name(self, name: str) -> List[Pitch]:
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


    async def generate_interval_exam(self, pitch_interval_setting: PitchIntervalSettingRequest) -> PitchIntervalExam:
        answer_mode_id = pitch_interval_setting.answer_mode
        exam_type = ExamType.INTERVAL.display_value
        question_num: int = ExamType.INTERVAL.question_num
        questions = []
        q= answer_mode_id
        if answer_mode_id == AnswerMode.CONCORDANCE.to_dict().get("index"):
            answer_choices = [ConcordanceChoice.CONCORDANCE.to_dict(),ConcordanceChoice.CONCORDANCE_PART.to_dict(),ConcordanceChoice.CONCORDANCE_NO.to_dict()]
            #生成检测题
            interval_ids = self.generate_default_interval_choices()
            if pitch_interval_setting.interval_list:
                interval_ids = pitch_interval_setting.interval_list
            questions= self.generate_interval_exam_concordance(interval_ids, question_num)

        elif answer_mode_id == AnswerMode.QUALITY.to_dict().get("index"):
            interval_ids = self.generate_default_interval_choices()
            if pitch_interval_setting.interval_list:
                interval_ids = pitch_interval_setting.interval_list
            questions = self.generate_interval_exam_quality(interval_ids, question_num)

        elif answer_mode_id == AnswerMode.PITCH.to_dict().get("index"):
            interval_ids = self.generate_default_interval_choices()
            if pitch_interval_setting.interval_list:
                interval_ids = pitch_interval_setting.interval_list
            questions = self.generate_interval_exam_pitch(interval_ids, question_num)

        pie = PitchIntervalExam(
            id = 0,
            user_id = 0,
            exam_type = ExamType.INTERVAL._value,
            question_num=ExamType.INTERVAL.question_num,
            questions=questions,
            correct_number = 0,
            wrong_number = 0,
        )

        return pie

    def generate_default_interval_choices(self) -> List[int]:
        list: List[int] = []
        for key, value in self.PITCH_INTERVAL_CACHE.items():
            if key <= 12:
                list.append(key)
        return list

    def generate_interval_exam_concordance(self, interval_list: List[int], question_num: int, play_mode: int, fix_mode_enabled: bool, fix_mode: int, fix_mode_val: str) -> List[dict]:
        questions = []
        # 从PITCH_INTERVAL_CACHE中获取所有可用的音程
        available_intervals = list(self.PITCH_INTERVAL_CACHE.keys())

        # 过滤出指定音程的条目
        filtered_intervals = []
        for id in interval_list:
            if id in available_intervals:
                pi = self.PITCH_INTERVAL_CACHE.get(id)
                if pi:
                    filtered_intervals.append(pi)

        if not filtered_intervals:
            raise ValueError("No valid intervals found in the cache")

        filtered_intervals_mode = []

        #filter mode
        if fix_mode_enabled :
            if fix_mode == 1:
                for pi in filtered_intervals:
                    pitch_pairs = pi.pitch_pairs
                    filter_pitch_pairs = []
                    for pitch_pair in pitch_pairs:
                        if pitch_pair.first_contain_start_not_black():
                            filter_pitch_pairs.append(pitch_pair)
                    new_pi = replace(pi, pitch_pairs=filter_pitch_pairs)
                    filtered_intervals_mode.append(new_pi)

            elif fix_mode == 2:
                for pi in filtered_intervals:
                    pitch_pairs = pi.pitch_pairs
                    filter_pitch_pairs = []
                    for pitch_pair in pitch_pairs:
                        if pitch_pair.second_contain_start_not_black():
                            filter_pitch_pairs.append(pitch_pair)
                    new_pi = replace(pi, pitch_pairs=filter_pitch_pairs)
                    filtered_intervals_mode.append(new_pi)

            else:
                for pi in filtered_intervals:
                    pitch_pairs = pi.pitch_pairs
                    filter_pitch_pairs = []
                    for pitch_pair in pitch_pairs:
                        if pitch_pair.contain_start_not_black():
                            filter_pitch_pairs.append(pitch_pair)
                    new_pi = replace(pi, pitch_pairs=filter_pitch_pairs)
                    filtered_intervals_mode.append(new_pi)

            filtered_intervals = filtered_intervals_mode

        # 生成20道题目
        for i in range(question_num):
            # 选一个答案音程
            interval: PitchIntervalWithPitches = random.choice(filtered_intervals)
            pitch_pair: PitchIntervalPair = random.choice(interval.pitch_pairs)

            # 创建题目
            question = IntervalQuestion(
                id= i + 1,
                answer_id= interval.concordance_id,
                answer_name= interval.concordance_name,
                question= pitch_pair,
            )
            questions.append(question)

        return questions

    def getPitchNameStart(self, fix_mode_val: str)-> str:
        if fix_mode_val == "Do":
            return "C"
        elif fix_mode_val == "Re":
            return "D"
        elif fix_mode_val == "Mi":
            return "E"
        if fix_mode_val == "Fa":
            return "F"
        elif fix_mode_val == "Sol":
            return "G"
        elif fix_mode_val == "La":
            return "A"
        if fix_mode_val == "Ti":
            return "B"

    def generate_interval_exam_quality(self, interval_list: List[int], question_num: int) -> List[dict]:
        questions = []
        # 从PITCH_INTERVAL_CACHE中获取所有可用的音程
        available_intervals = list(self.PITCH_INTERVAL_CACHE.keys())

        # 过滤出指定音程的条目
        filtered_intervals = []
        for id in interval_list:
            if id in available_intervals:
                pi = self.PITCH_INTERVAL_CACHE.get(id)
                if pi:
                    filtered_intervals.append(pi)

        if not filtered_intervals:
            raise ValueError("No valid intervals found in the cache")

        # 生成20道题目
        for i in range(question_num):
            # 选一个答案音程
            interval: PitchIntervalWithPitches = random.choice(filtered_intervals)
            pitch_pair = random.choice(interval.pitch_pairs)

            # 创建题目
            question = IntervalQuestion(
                id=i + 1,
                answer_id=interval.id,
                answer_name=interval.name,
                question=pitch_pair,
            )
            questions.append(question)

        return questions

    def generate_interval_exam_pitch(self, interval_list: List[int], question_num: int) -> List[dict]:
        questions = []
        # 从PITCH_INTERVAL_CACHE中获取所有可用的音程
        available_intervals = list(self.PITCH_INTERVAL_CACHE.keys())

        # 过滤出指定音程的条目
        filtered_intervals = []
        for id in interval_list:
            if id in available_intervals:
                pi = self.PITCH_INTERVAL_CACHE.get(id)
                if pi:
                    filtered_intervals.append(pi)

        if not filtered_intervals:
            raise ValueError("No valid intervals found in the cache")

        # 生成20道题目
        for i in range(question_num):
            # 选一个答案音程
            interval: PitchIntervalWithPitches = random.choice(filtered_intervals)
            pitch_pair = random.choice(interval.pitch_pairs)

            # 创建题目
            question = IntervalQuestion(
                id=i + 1,
                answer_id=interval.concordance_id,
                answer_name=interval.concordance_name,
                question=pitch_pair,
            )
            questions.append(question)

        return questions

    def generate_chord_exam_first(self, chord_list: List[int], question_num: int, play_mode: int, transfer_set: int) -> List[dict]:
        questions = []
        # 从PITCH_INTERVAL_CACHE中获取所有可用的音程
        available_chords = list(self.PITCH_CHORD_CACHE.keys())

        # 过滤出指定音程的条目
        filtered_chords = []
        for id in chord_list:
            if id in available_chords:
                chord = self.PITCH_CHORD_CACHE.get(id)
                if chord:
                    filtered_chords.append(chord)

        if not filtered_chords:
            raise ValueError("No valid chords found in the cache")

        # 生成20道题目
        for i in range(question_num):
            chord: PitchChord = random.choice(filtered_chords)
            pair: List[Pitch] = random.choice(chord.pair)
            transfer_pair = ChordInversion.invert(pair, transfer_set)

            # 创建题目
            question = ChordQuestion(
                id=i + 1,
                play_mode=play_mode,
                transfer_set=transfer_set,
                answer_id=chord.index,
                answer_name=chord.simple_name,
                question=transfer_pair,
            )
            questions.append(question)

        return questions

    def generate_chord_exam_second(self, chord_list: List[int], question_num: int, play_mode: int, transfer_set: int) -> List[dict]:
        questions = []
        available_chords = list(self.PITCH_CHORD_CACHE.keys())

        # 过滤出指定音程的条目
        filtered_chords = []
        for id in chord_list:
            if id in available_chords:
                chord = self.PITCH_CHORD_CACHE.get(id)
                if chord:
                    filtered_chords.append(chord)

        if not filtered_chords:
            raise ValueError("No valid chords found in the cache")

        # 生成20道题目
        for i in range(question_num):
            chord: PitchChord = random.choice(filtered_chords)
            pair: List[Pitch] = random.choice(chord.pair)
            transfer_pair = ChordInversion.invert(pair, transfer_set)

            # 创建题目
            question = ChordQuestion(
                id=i + 1,
                play_mode=play_mode,
                transfer_set=transfer_set,
                answer_id=chord.index,
                answer_name=chord.simple_name,
                question=transfer_pair,
            )
            questions.append(question)

        return questions

    async def generate_chord_exam(self, pitch_chord_setting: PitchChordSettingRequest) -> PitchIntervalExam:
        answer_mode_id = pitch_chord_setting.answer_mode
        play_mode = pitch_chord_setting.play_mode
        transfer_set = pitch_chord_setting.transfer_set
        exam_type = ExamType.CHORD.display_value
        question_num: int = ExamType.CHORD.question_num
        answer_choices = pitch_chord_setting.chord_list
        questions = []
        q = answer_mode_id
        if answer_mode_id == ChordAnswerMode.FIRST.to_dict().get("index"):
            # 生成检测题
            questions = self.generate_chord_exam_first(answer_choices, question_num, play_mode, transfer_set)

        elif answer_mode_id == ChordAnswerMode.SECOND.to_dict().get("index"):
            questions = self.generate_chord_exam_second(answer_choices, question_num, play_mode, transfer_set)


        pce = PitchChordExam(
            id=0,
            user_id=0,
            exam_type=ExamType.CHORD._value,
            question_num=ExamType.CHORD.question_num,
            questions=questions,
            correct_number=0,
            wrong_number=0,
        )

        return pce

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