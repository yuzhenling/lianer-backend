# app/services/rhythm_service.py

import random
from typing import List, Tuple

from app.api.v1.schemas.request.pitch_request import RhythmQuestionRequest
from app.api.v1.schemas.response.pitch_response import RhythmQuestionResponse, RhythmNote, RhythmMeasure, RhythmScore
from app.models.rhythm import *
from app.models.rhythm_settings import RhythmDifficulty, TimeSignature


class RhythmService:
    def __init__(self):
        # 定义不同难度的节奏模板
        #1.5    附点四分音符
        #1      四分音符
        #0.75   附点八分
        #0.5    八分音符
        #0.25   十六分音符
        #0.125  三十二分音符
        self.rhythm_patterns = {
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
                TimeSignature.TWO_FOUR: self._generate_rhythm_combinations(2, [1, 0.5, 0.25, 0.125, 1.5, 0.75], 50000),
                TimeSignature.THREE_FOUR: self._generate_rhythm_combinations(3, [1, 0.5, 0.25, 0.125, 1.5, 0.75], 1000000),
                TimeSignature.FOUR_FOUR: self._generate_rhythm_combinations(4, [1, 0.5, 0.25, 0.125, 1.5, 0.75], 10000000),
            },
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
        allowed_durations = {
            RhythmDifficulty.LOW: {1.0, 0.5},  # 四分音符和八分音符
            RhythmDifficulty.MEDIUM: {1.0, 0.5, 0.25, 1.5},  # 四分音符、八分音符、十六分音符和附点四分音符
            RhythmDifficulty.HIGH: {1.0, 0.5, 0.25, 0.125, 1.5, 0.75}  # 所有时值
        }
        
        allowed = allowed_durations[difficulty]
        
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

    def generate_question(self, request: RhythmQuestionRequest) -> RhythmQuestionResponse:
        """生成一个完整的节奏听写题"""
        # 生成正确答案
        correct_rhythm = self.generate_rhythm(
            request.difficulty,
            request.time_signature,
            request.measures_count.value,
            request.tempo.value
        )

        # 生成三个错误选项
        wrong_options = []
        max_attempts = 10  # 最大尝试次数，防止无限循环
        
        while len(wrong_options) < 3 and max_attempts > 0:
            wrong_rhythm = self.generate_wrong_rhythm(
                correct_rhythm,
                request.difficulty,
                request.time_signature
            )
            
            # 检查新生成的错误答案是否与已有的不同
            if self._is_unique_rhythm(wrong_rhythm, wrong_options):
                wrong_options.append(wrong_rhythm)
            
            max_attempts -= 1

        # 如果没有生成足够的错误答案，使用基本变化生成剩余的
        while len(wrong_options) < 3:
            basic_wrong = correct_rhythm.copy(deep=True)
            basic_wrong.is_correct = False
            # 将第一个音符改为休止符作为基本变化
            if (len(basic_wrong.measures) > 0 and 
                len(basic_wrong.measures[0]) > 0 and 
                len(basic_wrong.measures[0][0].notes) > 0):
                basic_wrong.measures[0][0].notes[0].is_rest = True
            wrong_options.append(basic_wrong)

        # 随机排列选项
        all_options = [correct_rhythm] + wrong_options
        random.shuffle(all_options)

        # 找出正确答案的位置
        correct_answer = chr(65 + all_options.index(correct_rhythm))  # A, B, C, or D

        return RhythmQuestionResponse(
            correct_answer=correct_answer,
            options=all_options,
            tempo=request.tempo,
            time_signature=request.time_signature,
            measures_count=request.measures_count,
            difficulty=request.difficulty
        )

    def generate_rhythm(
            self,
            difficulty: RhythmDifficulty,
            time_signature: TimeSignature,
            measures_count: int,
            tempo: int = 80,
    ) -> RhythmScore:
        """生成一个正确的节奏模式"""
        measures = []
        measures_sub = []
        patterns = self.rhythm_patterns[difficulty][time_signature]

        pattern_selected = random.choices(patterns, k=measures_count)
        for pattern in pattern_selected:
            notes = [
                RhythmNote(duration=duration)
                for duration in pattern
            ]
            measures_sub.append(RhythmMeasure(notes=notes))

        measures.append(measures_sub)

        return RhythmScore(
            measures=measures,
            time_signature=time_signature,
            tempo=tempo,
            is_correct=True
        )

    def generate_wrong_rhythm(
            self,
            correct_rhythm: RhythmScore,
            difficulty: RhythmDifficulty,
            time_signature: TimeSignature,
    ) -> RhythmScore:
        """生成一个错误的节奏变体"""
        # 复制正确的节奏
        wrong_rhythm = correct_rhythm.copy(deep=True)
        wrong_rhythm.is_correct = False

        # 定义可能的变化类型
        variation_types = [
            'change_duration',    # 改变音符时值
            'add_rest',          # 添加休止符
            'add_dot',           # 添加附点
            'merge_notes',       # 合并音符
            'split_notes',       # 拆分音符
            'shift_rhythm'       # 移动节奏位置
        ]

        # 随机选择变化类型
        variation_type = random.choice(variation_types)

        try:
            if variation_type == 'change_duration':
                # 随机改变某些音符的时值
                measure_group_idx = random.randint(0, len(wrong_rhythm.measures) - 1)
                measure_idx = random.randint(0, len(wrong_rhythm.measures[measure_group_idx]) - 1)
                measure = wrong_rhythm.measures[measure_group_idx][measure_idx]
                
                if len(measure.notes) > 0:
                    note_idx = random.randint(0, len(measure.notes) - 1)
                    note = measure.notes[note_idx]

                    # 改变时值但保持小节总时值不变
                    if note.duration == 1.0:
                        note.duration = 0.5
                        # 添加一个新的八分音符
                        measure.notes.insert(
                            note_idx + 1,
                            RhythmNote(duration=0.5)
                        )
                    elif note.duration == 2.0:
                        note.duration = 1.0
                        # 添加一个新的四分音符
                        measure.notes.insert(
                            note_idx + 1,
                            RhythmNote(duration=1.0)
                        )

            elif variation_type == 'add_rest':
                # 将某个音符改为休止符
                measure_group_idx = random.randint(0, len(wrong_rhythm.measures) - 1)
                measure_idx = random.randint(0, len(wrong_rhythm.measures[measure_group_idx]) - 1)
                measure = wrong_rhythm.measures[measure_group_idx][measure_idx]
                
                if len(measure.notes) > 0:
                    note_idx = random.randint(0, len(measure.notes) - 1)
                    measure.notes[note_idx].is_rest = True

            elif variation_type == 'add_dot':
                # 添加附点音符
                measure_group_idx = random.randint(0, len(wrong_rhythm.measures) - 1)
                measure_idx = random.randint(0, len(wrong_rhythm.measures[measure_group_idx]) - 1)
                measure = wrong_rhythm.measures[measure_group_idx][measure_idx]
                
                if len(measure.notes) > 1:  # 需要至少两个音符
                    note_idx = random.randint(0, len(measure.notes) - 2)  # 确保后面还有音符
                    note = measure.notes[note_idx]
                    next_note = measure.notes[note_idx + 1]

                    if note.duration == 1.0 and next_note.duration >= 0.5:
                        # 将四分音符变为附点四分音符
                        note.duration = 1.5
                        note.is_dotted = True
                        next_note.duration = 0.5

            elif variation_type == 'merge_notes':
                # 合并相邻音符
                measure_group_idx = random.randint(0, len(wrong_rhythm.measures) - 1)
                measure_idx = random.randint(0, len(wrong_rhythm.measures[measure_group_idx]) - 1)
                measure = wrong_rhythm.measures[measure_group_idx][measure_idx]
                
                if len(measure.notes) > 1:
                    note_idx = random.randint(0, len(measure.notes) - 2)
                    note1 = measure.notes[note_idx]
                    note2 = measure.notes[note_idx + 1]
                    
                    # 合并两个音符
                    note1.duration = note1.duration + note2.duration
                    measure.notes.pop(note_idx + 1)

            elif variation_type == 'split_notes':
                # 拆分音符
                measure_group_idx = random.randint(0, len(wrong_rhythm.measures) - 1)
                measure_idx = random.randint(0, len(wrong_rhythm.measures[measure_group_idx]) - 1)
                measure = wrong_rhythm.measures[measure_group_idx][measure_idx]
                
                if len(measure.notes) > 0:
                    note_idx = random.randint(0, len(measure.notes) - 1)
                    note = measure.notes[note_idx]
                    
                    if note.duration >= 1.0:
                        # 将一个较长的音符拆分为两个较短的音符
                        original_duration = note.duration
                        note.duration = original_duration / 2
                        measure.notes.insert(
                            note_idx + 1,
                            RhythmNote(duration=original_duration / 2)
                        )

            elif variation_type == 'shift_rhythm':
                # 移动节奏位置（在相邻小节之间交换音符）
                measure_group_idx = random.randint(0, len(wrong_rhythm.measures) - 1)
                measure_group = wrong_rhythm.measures[measure_group_idx]
                
                if len(measure_group) >= 2:
                    measure_idx = random.randint(0, len(measure_group) - 2)
                    measure1 = measure_group[measure_idx]
                    measure2 = measure_group[measure_idx + 1]
                    
                    if (len(measure1.notes) > 0 and len(measure2.notes) > 0 and
                        measure1.notes[-1].duration == measure2.notes[0].duration):
                        # 交换相邻小节的最后一个和第一个音符
                        measure1.notes[-1], measure2.notes[0] = measure2.notes[0], measure1.notes[-1]

        except Exception as e:
            # 如果变化失败，至少确保返回一个不同的节奏
            if len(wrong_rhythm.measures) > 0 and len(wrong_rhythm.measures[0]) > 0:
                measure = wrong_rhythm.measures[0][0]
                if len(measure.notes) > 0:
                    measure.notes[0].is_rest = True

        return wrong_rhythm

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
                    if (n1.duration != n2.duration or
                        n1.is_rest != n2.is_rest or
                        n1.is_dotted != n2.is_dotted):
                        return False
                    
        return True

rhythm_service = RhythmService()