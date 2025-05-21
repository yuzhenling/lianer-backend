# app/services/rhythm_service.py

import random
from typing import List, Tuple

from app.api.v1.schemas.request.pitch_request import RhythmSettingRequest
from app.api.v1.schemas.response.pitch_response import RhythmQuestionResponse, RhythmNote, RhythmMeasure, RhythmScore
from app.core.logger import logger
from app.models.rhythm_settings import RhythmDifficulty, TimeSignature


class RhythmService:
    def __init__(self):
        logger.info("Initializing RhythmService")
        # 定义不同难度的节奏模板
        #1.5    附点四分音符
        #1      四分音符
        #0.75   附点八分
        #0.5    八分音符
        #0.25   十六分音符
        #0.125  三十二分音符
        self.rhythm_patterns: dict = {
            RhythmDifficulty.LOW: {
                TimeSignature.TWO_FOUR: self._generate_rhythm_combinations(2, [1, 0.5]),
                TimeSignature.THREE_FOUR: self._generate_rhythm_combinations(3, [1, 0.5]),
                TimeSignature.FOUR_FOUR: self._generate_rhythm_combinations(4, [1, 0.5]),
            },
            RhythmDifficulty.MEDIUM: {
                TimeSignature.TWO_FOUR: self._generate_rhythm_combinations(2, [1, 0.5, 0.25, 1.5]),
                TimeSignature.THREE_FOUR: self._generate_rhythm_combinations(3, [1, 0.5, 0.25, 1.5]),
                TimeSignature.FOUR_FOUR: self._generate_rhythm_combinations(4, [1, 0.5, 0.25, 1.5], 10000),
            },
            RhythmDifficulty.HIGH: {
                TimeSignature.TWO_FOUR: self._generate_rhythm_combinations(2, [1, 0.5, 0.25, 0.125, 1.5, 0.75], 1),
                TimeSignature.THREE_FOUR: self._generate_rhythm_combinations(3, [1, 0.5, 0.25, 0.125, 1.5, 0.75], 1),
                TimeSignature.FOUR_FOUR: self._generate_rhythm_combinations(4, [1, 0.5, 0.25, 0.125, 1.5, 0.75], 1),
            },
        }
        logger.info("Rhythm patterns initialized")
        self.durations: dict = {
            RhythmDifficulty.LOW: {1.0, 0.5},  # 四分音符和八分音符
            RhythmDifficulty.MEDIUM: {1.0, 0.5, 0.25, 1.5},  # 四分音符、八分音符、十六分音符和附点四分音符
            RhythmDifficulty.HIGH: {1.0, 0.5, 0.25, 0.125, 1.5, 0.75}  # 所有时值
        }

    def _generate_rhythm_combinations(self, beats: int, durations: List[float], max_combinations: int = 1000) -> List[List[float]]:
        """生成所有可能的节奏组合，包括不同的元素和不同的顺序
        
        Args:
            beats: 小节拍数（如2/4拍为2，3/4拍为3，4/4拍为4）
            durations: 可用的音符时值列表
            max_combinations: 最大组合数限制
            
        Returns:
            List[List[float]]: 所有可能的节奏组合
        """
        logger.info(f"Generating rhythm combinations for beats={beats}, durations={durations}, max_combinations={max_combinations}")
        combinations = []
        print(beats, durations, max_combinations)
        
        def backtrack(current: List[float], remaining: float):
            # 如果已经达到最大组合数，直接返回
            if len(combinations) >= max_combinations:
                return
                
            if abs(remaining) < 0.001:  # 处理浮点数精度问题
                combinations.append(current.copy())
                return
            
            if remaining < 0:
                return
            
            # 尝试所有可能的时值
            for duration in durations:
                if duration <= remaining:
                    current.append(duration)
                    backtrack(current, remaining - duration)
                    # 如果已经达到最大组合数，直接返回
                    if len(combinations) >= max_combinations:
                        return
                    current.pop()
        
        # 生成所有排列组合
        backtrack([], beats)
        
        print(len(combinations))
        print(combinations[len(combinations)-1])
        logger.info(f"Generated {len(combinations)} rhythm combinations")
        return combinations

    def _generate_random_rhythm_combination(self, beats: int, durations: List[float]) -> List[float]:
        """随机生成一个符合拍数要求的节奏组合

        Args:
            beats: 小节拍数（如2/4拍为2，3/4拍为3，4/4拍为4）
            durations: 可用的音符时值列表
            max_notes: 最大音符数量限制

        Returns:
            List[float]: 随机生成的节奏组合
        """
        combination = []
        remaining = beats

        # 随机选择音符数量，但不超过max_notes
        num_notes = int(beats / min(durations))

        for _ in range(num_notes - 1):
            # 计算剩余可用的时值
            available_durations = [d for d in durations if d <= remaining]
            if not available_durations:
                break

            # 随机选择一个时值
            duration = random.choice(available_durations)
            combination.append(duration)
            remaining -= duration

            # 如果剩余拍数小于最小音符时值，结束生成
            if remaining < min(durations):
                break

        # 添加最后一个音符，确保总拍数正确
        if abs(remaining) > 0.001:  # 处理浮点数精度问题
            combination.append(remaining)

        # 随机打乱音符顺序
        random.shuffle(combination)

        return combination

    def _generate_random_rhythm_combinations(self, beats: int, durations: List[float], count: int = 8) -> List[List[float]]:
        """生成指定数量的随机节奏组合

        Args:
            beats: 小节拍数
            durations: 可用的音符时值列表
            count: 需要生成的组合数量

        Returns:
            List[List[float]]: 随机生成的节奏组合列表
        """
        combinations = []

        while len(combinations) < count:
            combo = self._generate_random_rhythm_combination(beats, durations)
            combinations.add(combo)

        return combinations

    def _filter_rhythm_combinations(self, combinations: List[List[float]], difficulty: RhythmDifficulty) -> List[List[float]]:
        """根据难度过滤节奏组合
        
        Args:
            combinations: 所有可能的节奏组合
            difficulty: 难度级别
            
        Returns:
            List[List[float]]: 过滤后的节奏组合
        """
        filtered = []
        
        # 定义每个难度级别的允许时值

        
        allowed = self.durations[difficulty]
        
        for combo in combinations:
            # 检查组合中的所有时值是否都在允许范围内
            if all(d in allowed for d in combo):
                filtered.append(combo)
        
        # 如果过滤后组合太多，随机选择一部分
        max_filtered = 50  # 设置最大过滤后组合数
        if len(filtered) > max_filtered:
            import random
            filtered = random.sample(filtered, max_filtered)
        
        return filtered

    async def generate_question(self, request: RhythmSettingRequest) -> RhythmQuestionResponse:
        """生成一个完整的节奏听写题"""
        logger.info(f"Generating rhythm question with request: {request.dict()}")
        
        # 生成正确答案
        logger.info("Generating correct rhythm")
        correct_rhythm = await self.generate_rhythm(
            request.difficulty,
            request.time_signature,
            request.measures_count.value,
            request.tempo.value
        )
        logger.info("Correct rhythm generated")

        # 使用系统化方法生成错误选项
        logger.info("Generating wrong options")
        wrong_options = self._generate_wrong_options_systematic(correct_rhythm, request.difficulty ,count=3)
        logger.info(f"Generated {len(wrong_options)} wrong options")

        # 确保每个错误选项都是唯一的
        logger.info("Checking uniqueness of wrong options")
        unique_wrong_options = []
        for wrong_rhythm in wrong_options:
            if self._is_unique_rhythm(wrong_rhythm, unique_wrong_options) and self._is_unique_rhythm(wrong_rhythm,[correct_rhythm]):
                unique_wrong_options.append(wrong_rhythm)
        logger.info(f"Found {len(unique_wrong_options)} unique wrong options")

        # 如果生成的唯一错误选项不足3个，使用基本变化补充
        if len(unique_wrong_options) < 3:
            logger.info("Adding basic variations to reach 3 unique options")
            basic_wrong = correct_rhythm.copy(deep=True)
            basic_wrong.is_correct = False
            # 将第一个音符改为休止符作为基本变化
            # if (len(basic_wrong.measures) > 0 and
            #     len(basic_wrong.measures[0]) > 0 and
            #     len(basic_wrong.measures[0][0].notes) > 0):
            #     basic_wrong.measures[0][0].notes[0].is_rest = True
            random_measure = random.choice(basic_wrong.measures)
            # 随机选择一个 voice（声部）
            random_voice = random.choice(random_measure)
            # 随机选择一个音符
            random_note = random.choice(random_voice.notes)
            # 将该音符改为休止符
            random_note.is_rest = True

            if self._is_unique_rhythm(basic_wrong, unique_wrong_options):
                unique_wrong_options.append(basic_wrong)


        # 随机排列选项
        logger.info("Randomizing options")
        all_options = [correct_rhythm] + unique_wrong_options
        random.shuffle(all_options)

        # 找出正确答案的位置
        correct_answer = chr(65 + all_options.index(correct_rhythm))  # A, B, C, or D
        logger.info(f"Correct answer is option {correct_answer}")

        for rr in all_options:
            rr.measures

        return RhythmQuestionResponse(
            correct_answer=correct_answer,
            options=all_options,
            tempo=request.tempo,
            time_signature=request.time_signature,
            measures_count=request.measures_count,
            difficulty=request.difficulty
        )

    async def generate_rhythm(
            self,
            difficulty: RhythmDifficulty,
            time_signature: TimeSignature,
            measures_count: int,
            tempo: int = 80,
    ) -> RhythmScore:
        """生成一个正确的节奏模式"""
        logger.info(f"Generating rhythm with difficulty={difficulty}, time_signature={time_signature}, measures_count={measures_count}")
        measures = []
        measures_sub = []
        patterns = self.rhythm_patterns[difficulty][time_signature]
        logger.info(f"Selected {len(patterns)} patterns for the given parameters")
        
        if difficulty == RhythmDifficulty.HIGH:
            logger.info("Generating high difficulty rhythm patterns")
            beats = 0
            duration = [1, 0.5, 0.25, 0.125, 1.5, 0.75]
            if time_signature == TimeSignature.TWO_FOUR :
                beats = 2
            elif time_signature == TimeSignature.THREE_FOUR:
                beats = 3
            elif time_signature == TimeSignature.FOUR_FOUR:
                beats = 4
            patterns = self._generate_random_rhythm_combinations(beats, duration, measures_count*2)
            logger.info(f"Generated {len(patterns)} high difficulty patterns")

        pattern_selected = random.choices(patterns, k=measures_count)
        logger.info(f"Selected {len(pattern_selected)} patterns for measures")
        
        for pattern in pattern_selected:
            notes = [
                RhythmNote(duration=duration)
                for duration in pattern
            ]
            measures_sub.append(RhythmMeasure(notes=notes))

        measures.append(measures_sub)
        logger.info("Successfully created rhythm measures")

        return RhythmScore(
            measures=measures,
            time_signature=time_signature,
            tempo=tempo,
            is_correct=True
        )

    # def generate_wrong_rhythm(
    #         self,
    #         correct_rhythm: RhythmScore,
    #         difficulty: RhythmDifficulty,
    #         time_signature: TimeSignature,
    # ) -> RhythmScore:
    #     """生成一个错误的节奏变体"""
    #     # 复制正确的节奏
    #     wrong_rhythm = correct_rhythm.copy(deep=True)
    #     wrong_rhythm.is_correct = False
    #
    #     # 定义可能的变化类型
    #     variation_types = [
    #         'change_duration',    # 改变音符时值
    #         'add_rest',          # 添加休止符
    #         'add_dot',           # 添加附点
    #         'merge_notes',       # 合并音符
    #         'split_notes',       # 拆分音符
    #         'shift_rhythm'       # 移动节奏位置
    #     ]
    #
    #     # 随机选择变化类型
    #     variation_type = random.choice(variation_types)
    #
    #     try:
    #         if variation_type == 'change_duration':
    #             # 随机改变某些音符的时值
    #             measure_group_idx = random.randint(0, len(wrong_rhythm.measures) - 1)
    #             measure_idx = random.randint(0, len(wrong_rhythm.measures[measure_group_idx]) - 1)
    #             measure = wrong_rhythm.measures[measure_group_idx][measure_idx]
    #
    #             if len(measure.notes) > 0:
    #                 note_idx = random.randint(0, len(measure.notes) - 1)
    #                 note = measure.notes[note_idx]
    #
    #                 # 改变时值但保持小节总时值不变
    #                 if note.duration == 1.0:
    #                     note.duration = 0.5
    #                     # 添加一个新的八分音符
    #                     measure.notes.insert(
    #                         note_idx + 1,
    #                         RhythmNote(duration=0.5)
    #                     )
    #                 elif note.duration == 2.0:
    #                     note.duration = 1.0
    #                     # 添加一个新的四分音符
    #                     measure.notes.insert(
    #                         note_idx + 1,
    #                         RhythmNote(duration=1.0)
    #                     )
    #
    #         elif variation_type == 'add_rest':
    #             # 将某个音符改为休止符
    #             measure_group_idx = random.randint(0, len(wrong_rhythm.measures) - 1)
    #             measure_idx = random.randint(0, len(wrong_rhythm.measures[measure_group_idx]) - 1)
    #             measure = wrong_rhythm.measures[measure_group_idx][measure_idx]
    #
    #             if len(measure.notes) > 0:
    #                 note_idx = random.randint(0, len(measure.notes) - 1)
    #                 measure.notes[note_idx].is_rest = True
    #
    #         elif variation_type == 'add_dot':
    #             # 添加附点音符
    #             measure_group_idx = random.randint(0, len(wrong_rhythm.measures) - 1)
    #             measure_idx = random.randint(0, len(wrong_rhythm.measures[measure_group_idx]) - 1)
    #             measure = wrong_rhythm.measures[measure_group_idx][measure_idx]
    #
    #             if len(measure.notes) > 1:  # 需要至少两个音符
    #                 note_idx = random.randint(0, len(measure.notes) - 2)  # 确保后面还有音符
    #                 note = measure.notes[note_idx]
    #                 next_note = measure.notes[note_idx + 1]
    #
    #                 if note.duration == 1.0 and next_note.duration >= 0.5:
    #                     # 将四分音符变为附点四分音符
    #                     note.duration = 1.5
    #                     note.is_dotted = True
    #                     next_note.duration = 0.5
    #
    #         elif variation_type == 'merge_notes':
    #             # 合并相邻音符
    #             measure_group_idx = random.randint(0, len(wrong_rhythm.measures) - 1)
    #             measure_idx = random.randint(0, len(wrong_rhythm.measures[measure_group_idx]) - 1)
    #             measure = wrong_rhythm.measures[measure_group_idx][measure_idx]
    #
    #             if len(measure.notes) > 1:
    #                 note_idx = random.randint(0, len(measure.notes) - 2)
    #                 note1 = measure.notes[note_idx]
    #                 note2 = measure.notes[note_idx + 1]
    #
    #                 # 合并两个音符
    #                 note1.duration = note1.duration + note2.duration
    #                 measure.notes.pop(note_idx + 1)
    #
    #         elif variation_type == 'split_notes':
    #             # 拆分音符
    #             measure_group_idx = random.randint(0, len(wrong_rhythm.measures) - 1)
    #             measure_idx = random.randint(0, len(wrong_rhythm.measures[measure_group_idx]) - 1)
    #             measure = wrong_rhythm.measures[measure_group_idx][measure_idx]
    #
    #             if len(measure.notes) > 0:
    #                 note_idx = random.randint(0, len(measure.notes) - 1)
    #                 note = measure.notes[note_idx]
    #
    #                 if note.duration >= 1.0:
    #                     # 将一个较长的音符拆分为两个较短的音符
    #                     original_duration = note.duration
    #                     note.duration = original_duration / 2
    #                     measure.notes.insert(
    #                         note_idx + 1,
    #                         RhythmNote(duration=original_duration / 2)
    #                     )
    #
    #         elif variation_type == 'shift_rhythm':
    #             # 移动节奏位置（在相邻小节之间交换音符）
    #             measure_group_idx = random.randint(0, len(wrong_rhythm.measures) - 1)
    #             measure_group = wrong_rhythm.measures[measure_group_idx]
    #
    #             if len(measure_group) >= 2:
    #                 measure_idx = random.randint(0, len(measure_group) - 2)
    #                 measure1 = measure_group[measure_idx]
    #                 measure2 = measure_group[measure_idx + 1]
    #
    #                 if (len(measure1.notes) > 0 and len(measure2.notes) > 0 and
    #                     measure1.notes[-1].duration == measure2.notes[0].duration):
    #                     # 交换相邻小节的最后一个和第一个音符
    #                     measure1.notes[-1], measure2.notes[0] = measure2.notes[0], measure1.notes[-1]
    #
    #     except Exception as e:
    #         # 如果变化失败，至少确保返回一个不同的节奏
    #         if len(wrong_rhythm.measures) > 0 and len(wrong_rhythm.measures[0]) > 0:
    #             measure = wrong_rhythm.measures[0][0]
    #             if len(measure.notes) > 0:
    #                 measure.notes[0].is_rest = True
    #
    #     return wrong_rhythm

    def _is_unique_rhythm(self, new_rhythm: RhythmScore, existing_rhythms: List[RhythmScore]) -> bool:
        """检查新生成的节奏是否与现有的错误答案不同"""
        for existing in existing_rhythms:
            if self._are_rhythms_similar(new_rhythm, existing):
                return False
        return True

    def _are_rhythms_similar(self, rhythm1: RhythmScore, rhythm2: RhythmScore) -> bool:
        """比较两个节奏是否相似"""
        if len(rhythm1.measures) != len(rhythm2.measures):
            return False
            
        for measure_group1, measure_group2 in zip(rhythm1.measures, rhythm2.measures):
            if len(measure_group1) != len(measure_group2):
                return False
                
            for m1, m2 in zip(measure_group1, measure_group2):
                if len(m1.notes) != len(m2.notes):
                    return False
                    
                for n1, n2 in zip(m1.notes, m2.notes):
                    if (n1.duration != n2.duration):
                        return False
                    
        return True

    def _generate_random_rhythm_combination(self, beats: int, durations: List[float], max_notes: int = 8) -> List[float]:
        """随机生成一个符合拍数要求的节奏组合
        
        Args:
            beats: 小节拍数（如2/4拍为2，3/4拍为3，4/4拍为4）
            durations: 可用的音符时值列表
            max_notes: 最大音符数量限制
            
        Returns:
            List[float]: 随机生成的节奏组合
        """
        combination = []
        remaining = beats
        
        # 随机选择音符数量，但不超过max_notes
        num_notes = random.randint(1, min(max_notes, int(beats / min(durations))))
        
        for _ in range(num_notes - 1):
            # 计算剩余可用的时值
            available_durations = [d for d in durations if d <= remaining]
            if not available_durations:
                break
                
            # 随机选择一个时值
            duration = random.choice(available_durations)
            combination.append(duration)
            remaining -= duration
            
            # 如果剩余拍数小于最小音符时值，结束生成
            if remaining < min(durations):
                break
        
        # 添加最后一个音符，确保总拍数正确
        if abs(remaining) > 0.001:  # 处理浮点数精度问题
            combination.append(remaining)
            
        # 随机打乱音符顺序
        random.shuffle(combination)
        
        return combination

    def _generate_random_rhythm_combinations(self, beats: int, durations: List[float], count: int = 1000) -> List[List[float]]:
        """生成指定数量的随机节奏组合
        
        Args:
            beats: 小节拍数
            durations: 可用的音符时值列表
            count: 需要生成的组合数量
            
        Returns:
            List[List[float]]: 随机生成的节奏组合列表
        """
        combinations = set()
        
        while len(combinations) < count:
            combo = self._generate_random_rhythm_combination(beats, durations)
            # 将组合转换为元组以便去重
            combo_tuple = tuple(combo)
            if combo_tuple not in combinations:
                combinations.add(combo_tuple)
                
        return [list(combo) for combo in combinations]

    def _generate_wrong_options_systematic(self, correct_rhythm: RhythmScore, difficulty: RhythmDifficulty, count: int = 3) -> List[RhythmScore]:
        """系统化生成错误选项
        
        Args:
            correct_rhythm: 正确答案
            count: 需要生成的错误选项数量
            
        Returns:
            List[RhythmScore]: 生成的错误选项列表
        """
        wrong_options = []
        
        # 定义变化规则
        variation_rules = [
            # 规则1: 改变音符时值
            lambda rhythm: self._apply_duration_change(rhythm),
            #规则2: 添加休止符
            lambda rhythm: self._apply_rest_addition(rhythm),
            # 规则3: 添加附点
            # lambda rhythm: self._apply_dot_addition(rhythm),
            # 规则4: 合并音符
            lambda rhythm: self._apply_note_merge(rhythm),
            # 规则5: 拆分音符
            lambda rhythm: self._apply_note_split(rhythm),
            # 规则6: 移动节奏位置
            lambda rhythm: self._apply_rhythm_shift(rhythm),
            # 规则7: 改变音符顺序
            lambda rhythm: self._apply_note_reorder(rhythm),
            # 规则8: 改变小节结构
            lambda rhythm: self._apply_measure_structure_change(rhythm)
        ]
        if difficulty == RhythmDifficulty.HIGH:
            variation_rules = [
                # 规则1: 改变音符时值
                lambda rhythm: self._apply_duration_change(rhythm),
                # 规则2: 添加休止符
                lambda rhythm: self._apply_rest_addition(rhythm),
                # 规则3: 添加附点
                lambda rhythm: self._apply_dot_addition(rhythm),
                # 规则4: 合并音符
                lambda rhythm: self._apply_note_merge(rhythm),
                # 规则5: 拆分音符
                lambda rhythm: self._apply_note_split(rhythm),
                # 规则6: 移动节奏位置
                lambda rhythm: self._apply_rhythm_shift(rhythm),
                # 规则7: 改变音符顺序
                lambda rhythm: self._apply_note_reorder(rhythm),
                # 规则8: 改变小节结构
                lambda rhythm: self._apply_measure_structure_change(rhythm)
            ]

        
        # 随机选择变化规则
        selected_rules = random.sample(variation_rules, count)
        
        for apply_rule in selected_rules:
            wrong_rhythm = correct_rhythm.copy(deep=True)
            wrong_rhythm.is_correct = False
            apply_rule(wrong_rhythm)
            wrong_options.append(wrong_rhythm)
        
        return wrong_options

    def _apply_duration_change(self, rhythm: RhythmScore) -> None:
        """改变音符时值"""
        measure_group_idx = random.randint(0, len(rhythm.measures) - 1)
        measure_idx = random.randint(0, len(rhythm.measures[measure_group_idx]) - 1)
        measure = rhythm.measures[measure_group_idx][measure_idx]
        
        if len(measure.notes) > 0:
            note_idx = random.randint(0, len(measure.notes) - 1)
            note = measure.notes[note_idx]
            
            # 根据当前时值选择合适的变化
            if note.duration == 1.0:
                note.duration = 0.5
                measure.notes.insert(note_idx + 1, RhythmNote(duration=0.5))
            elif note.duration == 0.5:
                note.duration = 0.25
                measure.notes.insert(note_idx + 1, RhythmNote(duration=0.25))

    def _apply_rest_addition(self, rhythm: RhythmScore) -> None:
        """添加休止符"""
        measure_group_idx = random.randint(0, len(rhythm.measures) - 1)
        measure_idx = random.randint(0, len(rhythm.measures[measure_group_idx]) - 1)
        measure = rhythm.measures[measure_group_idx][measure_idx]
        
        if len(measure.notes) > 0:
            note_idx = random.randint(0, len(measure.notes) - 1)
            measure.notes[note_idx].is_rest = True

    def _apply_dot_addition(self, rhythm: RhythmScore) -> None:
        """添加附点"""
        measure_group_idx = random.randint(0, len(rhythm.measures) - 1)
        measure_idx = random.randint(0, len(rhythm.measures[measure_group_idx]) - 1)
        measure = rhythm.measures[measure_group_idx][measure_idx]
        
        if len(measure.notes) > 1:
            note_idx = random.randint(0, len(measure.notes) - 2)
            note = measure.notes[note_idx]
            next_note = measure.notes[note_idx + 1]
            
            if note.duration == 1.0 and next_note.duration >= 0.5:
                note.duration = 1.5
                note.is_dotted = True
                next_note.duration = 0.5

    def _apply_note_merge(self, rhythm: RhythmScore) -> None:
        """合并音符"""
        measure_group_idx = random.randint(0, len(rhythm.measures) - 1)
        measure_idx = random.randint(0, len(rhythm.measures[measure_group_idx]) - 1)
        measure = rhythm.measures[measure_group_idx][measure_idx]
        
        if len(measure.notes) > 1:
            note_idx = random.randint(0, len(measure.notes) - 2)
            note1 = measure.notes[note_idx]
            note2 = measure.notes[note_idx + 1]
            
            note1.duration = note1.duration + note2.duration
            measure.notes.pop(note_idx + 1)

    def _apply_note_split(self, rhythm: RhythmScore) -> None:
        """拆分音符"""
        measure_group_idx = random.randint(0, len(rhythm.measures) - 1)
        measure_idx = random.randint(0, len(rhythm.measures[measure_group_idx]) - 1)
        measure = rhythm.measures[measure_group_idx][measure_idx]
        
        if len(measure.notes) > 0:
            note_idx = random.randint(0, len(measure.notes) - 1)
            note = measure.notes[note_idx]
            
            if note.duration >= 1.0:
                original_duration = note.duration
                note.duration = original_duration / 2
                measure.notes.insert(note_idx + 1, RhythmNote(duration=original_duration / 2))

    def _apply_rhythm_shift(self, rhythm: RhythmScore) -> None:
        """移动节奏位置，只交换不同的音符
        
        Args:
            rhythm: 要修改的节奏
        """
        measure_group_idx = random.randint(0, len(rhythm.measures) - 1)
        measure_group = rhythm.measures[measure_group_idx]
        
        if len(measure_group) >= 2:
            # 找出所有可以交换的相邻小节对
            valid_pairs = []
            for i in range(len(measure_group) - 1):
                measure1 = measure_group[i]
                measure2 = measure_group[i + 1]
                
                if (len(measure1.notes) > 0 and len(measure2.notes) > 0 and
                    # 检查两个音符是否不同
                    (measure1.notes[-1].duration != measure2.notes[0].duration)):
                    valid_pairs.append(i)
            
            # 如果有可以交换的小节对，随机选择一对进行交换
            if valid_pairs:
                pair_idx = random.choice(valid_pairs)
                measure1 = measure_group[pair_idx]
                measure2 = measure_group[pair_idx + 1]
                measure1.notes[-1], measure2.notes[0] = measure2.notes[0], measure1.notes[-1]

    def _apply_note_reorder(self, rhythm: RhythmScore) -> None:
        """改变音符顺序，只交换不同时值的音符
        
        Args:
            rhythm: 要修改的节奏
        """
        measure_group_idx = random.randint(0, len(rhythm.measures) - 1)
        measure_idx = random.randint(0, len(rhythm.measures[measure_group_idx]) - 1)
        measure = rhythm.measures[measure_group_idx][measure_idx]
        
        if len(measure.notes) > 1:
            # 找出所有不同时值的音符对
            different_duration_pairs = []
            for i in range(len(measure.notes)):
                for j in range(i + 1, len(measure.notes)):
                    if measure.notes[i].duration != measure.notes[j].duration:
                        different_duration_pairs.append((i, j))
            
            # 如果有不同时值的音符对，随机选择一对进行交换
            if different_duration_pairs:
                idx1, idx2 = random.choice(different_duration_pairs)
                measure.notes[idx1], measure.notes[idx2] = measure.notes[idx2], measure.notes[idx1]

    def _apply_measure_structure_change(self, rhythm: RhythmScore) -> None:
        """改变小节结构，只交换不同的小节
        
        Args:
            rhythm: 要修改的节奏
        """
        if len(rhythm.measures) > 1:
            # 找出所有不同的小节对
            different_measure_pairs = []
            for i in range(len(rhythm.measures)):
                for j in range(i + 1, len(rhythm.measures)):
                    # 检查两个小节是否不同
                    if not self._are_measures_similar(rhythm.measures[i], rhythm.measures[j]):
                        different_measure_pairs.append((i, j))
            
            # 如果有不同的小节对，随机选择一对进行交换
            if different_measure_pairs:
                idx1, idx2 = random.choice(different_measure_pairs)
                rhythm.measures[idx1], rhythm.measures[idx2] = rhythm.measures[idx2], rhythm.measures[idx1]

    def _are_measures_similar(self, measure1: List[RhythmMeasure], measure2: List[RhythmMeasure]) -> bool:
        """比较两个小节是否相似
        
        Args:
            measure1: 第一个小节
            measure2: 第二个小节
            
        Returns:
            bool: 如果小节相似返回True，否则返回False
        """
        if len(measure1) != len(measure2):
            return False
            
        for m1, m2 in zip(measure1, measure2):
            if len(m1.notes) != len(m2.notes):
                return False
                
            for n1, n2 in zip(m1.notes, m2.notes):
                if (n1.duration != n2.duration):
                    return False
                    
        return True

rhythm_service = RhythmService()