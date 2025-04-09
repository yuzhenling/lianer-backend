import copy
import random

from fastapi import HTTPException
from starlette import status

from app.api.v1.schemas.request.pitch_request import  MelodyQuestionRequest
from app.api.v1.schemas.response.pitch_response import RhythmNote, RhythmMeasure, RhythmScore, \
    MelodyQuestionResponse, MelodyScorePitch, MelodyNotePitch, \
    MelodyMeasurePitch, PitchResponse
from app.core.i18n import i18n
from app.core.logger import logger
from app.models.melody_settings import Tonality, TonalityChoice
from app.models.pitch import Pitch
from app.models.rhythm import *
from app.models.rhythm_settings import RhythmDifficulty, TimeSignature
from app.services.pitch_service import pitch_service


class MelodyService:
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


    def generate_question(self, request: MelodyQuestionRequest) -> MelodyQuestionResponse:
        """生成一个完整的节奏听写题"""
        # 生成正确答案
        correct_melody = self.generate_melody(
            request.difficulty,
            request.time_signature,
            request.measures_count.value,
            request.tempo.value,
            request.tonality,
            request.tonality_choice,
        )

        # 生成三个错误选项
        wrong_options = []
        for i in range(3):
            wrong_melody = self.generate_wrong_melody(
                correct_melody,
                request.difficulty,
                request.time_signature,
                request.measures_count.value,
                request.tempo.value,
                request.tonality,
                request.tonality_choice,
            )
            wrong_options.append(wrong_melody)


        return MelodyQuestionResponse(
            correct_answer=correct_melody,
            options=wrong_options,
            tempo=request.tempo,
            time_signature=request.time_signature,
            measures_count=request.measures_count,
            difficulty=request.difficulty
        )

    def generate_melody(
            self,
            difficulty: RhythmDifficulty,
            time_signature: TimeSignature,
            measures_count: int,
            tempo: int = 80,
            tonality: int = 1,
            tonality_choice: int = 1,
    ) -> MelodyScorePitch:
        """生成一个正确的节奏模式"""
        measures = []
        measures_sub = []
        patterns = self.rhythm_patterns[difficulty][time_signature]

        pitch_list = self.get_pitch_list(tonality, tonality_choice, difficulty)
        pitch_index = 0
        pattern_selected = random.choices(patterns, k=measures_count)
        for pattern in pattern_selected:
            notes = []
            for duration in pattern:
                notes.append(MelodyNotePitch(
                    duration=duration,
                    pitch=pitch_list[pitch_index%len(pitch_list)],
                ))
                pitch_index += 1

            measures_sub.append(MelodyMeasurePitch(notes=notes))

        measures.append(measures_sub)

        return MelodyScorePitch(
            measures=measures,
            time_signature=time_signature,
            tempo=tempo,
            is_correct=True
        )

    def generate_wrong_melody(
            self,
            correct_melody: MelodyScorePitch,
            difficulty: RhythmDifficulty,
            time_signature: TimeSignature,
            measures_count: int,
            tempo: int = 80,
            tonality: int = 1,
            tonality_choice: int = 1,
    ) -> MelodyScorePitch:
        """生成一个错误的节奏变体"""
        try:
            # 复制正确的旋律
            wrong_melody = copy.deepcopy(correct_melody)
            wrong_melody.is_correct = False

            # 获取调式和调式选择类型
            tonality_obj = self.get_tonality(tonality)
            tonality_choice_obj = self.get_tonality_choice(tonality_choice)

            # 定义可能的变化类型
            variation_types = [
                'change_scale',  # 改变音阶类型
                'change_tonality',  # 改变调式
                'add_accidental',  # 添加变化音
                'shift_octave'  # 移动八度
            ]

            # 随机选择变化类型
            variation_type = random.choice(variation_types)
            if variation_type == 'change_scale':
                # 改变音阶类型（例如：从自然大调变为和声大调）
                # 获取所有可用的调式选择类型
                available_choices = [
                    t for t in TonalityChoice
                    if t != tonality_choice_obj
                ]
                if available_choices:
                    new_choice: TonalityChoice = random.choice(available_choices)
                    # 使用新的音阶生成旋律
                    measures = []
                    measures_sub = []
                    patterns = self.rhythm_patterns[difficulty][time_signature]
                    pattern_selected = random.choices(patterns, k=measures_count)

                    pitch_list = self.get_pitch_list(tonality, new_choice.get_index(), difficulty)
                    pitch_index = 0
                    for pattern in pattern_selected:
                        notes = []
                        for duration in pattern:
                            notes.append(MelodyNotePitch(
                                duration=duration,
                                pitch=pitch_list[pitch_index%len(pitch_list)],
                            ))
                            pitch_index += 1
                        measures_sub.append(MelodyMeasurePitch(notes=notes))
                    measures.append(measures_sub)
                    wrong_melody.measures = measures

            elif variation_type == 'change_tonality':
                # 改变调式（例如：从C大调变为G大调）
                # 获取所有可用的调式
                available_tonalities = [
                    t for t in Tonality
                    if t != tonality_obj
                ]
                if available_tonalities:
                    new_tonality:Tonality = random.choice(available_tonalities)
                    # 使用新的调式生成旋律
                    measures = []
                    measures_sub = []
                    patterns = self.rhythm_patterns[difficulty][time_signature]
                    pattern_selected = random.choices(patterns, k=measures_count)

                    pitch_list = self.get_pitch_list(new_tonality.get_index(), tonality_choice, difficulty)
                    pitch_index = 0
                    for pattern in pattern_selected:
                        notes = []
                        for duration in pattern:
                            pitch = pitch_list[pitch_index % len(pitch_list)]

                            notes.append(MelodyNotePitch(
                                duration=duration,
                                pitch=PitchResponse(
                                    id= pitch.id,
                                    pitch_number=pitch.pitch_number,
                                    name=pitch.name,
                                    alias=pitch.alias,
                                ),
                            ))
                            pitch_index += 1
                        measures_sub.append(MelodyMeasurePitch(notes=notes))
                    measures.append(measures_sub)
                    wrong_melody.measures = measures

            elif variation_type == 'add_accidental':
                ms = wrong_melody.measures
                sub = random.choice(ms)
                mmp = random.choice(sub)
                origin_notes: List[MelodyNotePitch] = mmp.notes

                for note in origin_notes:
                    # 随机决定是否添加变化音
                    if random.random() < 0.3:  # 50%的概率添加变化音
                        pn = note.pitch.pitch_number
                        if pn == 88:
                            continue
                        change_num = pn + random.randint(1, 88-pn)
                        new_pitch = pitch_service.get_pitch_by_number(change_num)
                        new_note = MelodyNotePitch(
                                    duration=note.duration,
                                    pitch=new_pitch,
                                )
                        note = new_note

            elif variation_type == 'shift_octave':
                # 移动八度
                measures = []
                measures_sub = []
                patterns = self.rhythm_patterns[difficulty][time_signature]
                pattern_selected = random.choices(patterns, k=measures_count)
                pitch_list = self.get_pitch_list(tonality, tonality_choice, difficulty)

                pitch_index = 0
                for pattern in pattern_selected:
                    notes = []
                    for duration in pattern:
                        pitch_t = pitch_list[pitch_index%len(pitch_list)],
                        pitch:Pitch = pitch_t[0]
                        change_pitch = None
                        # 随机决定是否移动八度
                        if random.random() < 0.5:  # 30%的概率移动八度
                            if random.choice([True, False]):
                                pitch_num = 88 if pitch.pitch_number+12 > 88 else pitch.pitch_number+12
                            else:
                                pitch_num = 0 if pitch.pitch_number-12 < 0 else pitch.pitch_number-12

                            change_pitch = pitch_service.get_pitch_by_number(pitch_num)

                        notes.append(MelodyNotePitch(
                            duration=duration,
                            pitch=pitch if change_pitch is None else change_pitch,
                        ))
                        pitch_index += 1
                    measures_sub.append(RhythmMeasure(notes=notes))
                measures.append(measures_sub)
                wrong_melody.measures = measures

            return wrong_melody
        except Exception as e:
            logger.error(f"Error generating wrong melody: {str(e)}")

    def get_pitch_list(self, tonality:int, tonality_choice: int, difficulty: RhythmDifficulty) -> List[Pitch]:
        t = self.get_tonality(tonality)
        choice = self.get_tonality_choice(tonality_choice)
        root_note = t.get_root_note()
        interval_nums = choice.get_interval_nums()
        pitch_list:List[Pitch] = []
        num = random.randint(1,7)
        for interval_num in interval_nums:
            pitch_name = f'{root_note}{num}'#TODO
            pitches = pitch_service.get_pitch_by_name(pitch_name)
            if not pitches and len(pitches) != 1:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Not Found Pitch"
                )
            pitch = pitches[0]
            pitch = pitch_service.get_pitch_by_number(pitch.pitch_number+interval_num)
            pitch_list.append(pitch)

        if difficulty == RhythmDifficulty.MEDIUM:
            point = random.randint(1, len(pitch_list)-1)
            pitch_list = pitch_list[point:] + pitch_list[:point]

        elif difficulty == RhythmDifficulty.HIGH:
            pitch_list = random.sample(pitch_list, len(pitch_list))

        return pitch_list


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

    def get_tonality(self, index: int) -> Tonality:
        for tonality in Tonality:
            if tonality._index == index:
                return tonality

    def get_tonality_choice(self, index: int) -> TonalityChoice:
        for tc in TonalityChoice:
            if tc._index == index:
                return tc

melody_service = MelodyService()