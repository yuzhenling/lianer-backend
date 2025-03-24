# app/services/rhythm_service.py

import random
from typing import List, Tuple
from app.models.rhythm import *
from app.models.rhythmSettings import RhythmDifficulty, TimeSignature


class RhythmService:
    def __init__(self):
        # 定义不同难度的节奏模板
        self.rhythm_patterns = {
            RhythmDifficulty.LOW: {
                TimeSignature.TWO_FOUR: [
                    [1, 1],  # 四分音符
                    [2],  # 二分音符
                ],
                TimeSignature.THREE_FOUR: [
                    [1, 1, 1],
                    [2, 1],
                ],
                TimeSignature.FOUR_FOUR: [
                    [1, 1, 1, 1],
                    [2, 2],
                    [2, 1, 1],
                ],
            },
            RhythmDifficulty.MEDIUM: {
                TimeSignature.TWO_FOUR: [
                    [0.5, 0.5, 1],  # 两个八分音符+四分音符
                    [1, 0.5, 0.5],
                ],
                # ... 其他拍号的模板
            },
            RhythmDifficulty.HIGH: {
                TimeSignature.TWO_FOUR: [
                    [0.25, 0.25, 0.5, 1],  # 包含十六分音符
                    [1.5, 0.5],  # 符点四分音符
                ],
                # ... 其他拍号的模板
            },
        }

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
        for _ in range(3):
            wrong_rhythm = self.generate_wrong_rhythm(
                correct_rhythm,
                request.difficulty,
                request.time_signature
            )
            wrong_options.append(wrong_rhythm)

        # 随机排列选项
        all_options = [correct_rhythm] + wrong_options
        random.shuffle(all_options)

        # 找出正确答案的位置
        correct_answer = chr(65 + all_options.index(correct_rhythm))  # A, B, C, or D

        return RhythmQuestionResponse(
            id=random.randint(1, 10000),  # 实际应该使用数据库ID
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

        # 随机选择变化类型
        variation_type = random.choice([
            'change_duration',
            'add_rest',
            'add_dot',
            'change_grouping'
        ])

        if variation_type == 'change_duration':
            # 随机改变某些音符的时值
            measure_idx = random.randint(0, len(wrong_rhythm.measures) - 1)
            note_idx = random.randint(0, len(wrong_rhythm.measures[measure_idx].notes) - 1)
            note = wrong_rhythm.measures[measure_idx].notes[note_idx]

            # 改变时值但保持小节总时值不变
            if note.duration == 1.0:
                note.duration = 0.5
                # 添加一个新的八分音符
                wrong_rhythm.measures[measure_idx].notes.insert(
                    note_idx + 1,
                    RhythmNote(duration=0.5)
                )

        elif variation_type == 'add_rest':
            # 将某个音符改为休止符
            measure_idx = random.randint(0, len(wrong_rhythm.measures) - 1)
            note_idx = random.randint(0, len(wrong_rhythm.measures[measure_idx].notes) - 1)
            wrong_rhythm.measures[measure_idx].notes[note_idx].is_rest = True

        return wrong_rhythm

rhythm_service = RhythmService()