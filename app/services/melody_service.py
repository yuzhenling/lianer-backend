import copy
import random
from typing import List

from fastapi import HTTPException
from starlette import status

from app.api.v1.schemas.request.pitch_request import MelodySettingRequest
from app.api.v1.schemas.response.pitch_response import (
    MelodyNotePitch, MelodyMeasurePitch, MelodyScorePitch, MelodyQuestionResponse,
    PitchResponse
)
from app.core.i18n import i18n
from app.core.logger import logger
from app.models.melody_settings import Tonality, TonalityChoice
from app.models.pitch import Pitch
from app.models.rhythm_settings import RhythmDifficulty, TimeSignature
from app.services.pitch_service import pitch_service
from app.services.rhythm_service import rhythm_service


class MelodyService:
    def __init__(self):
        pass

    def generate_question(self, request: MelodySettingRequest) -> MelodyQuestionResponse:
        """生成一个完整的旋律听写题"""
        # 生成正确答案
        correct_melody = self.generate_melody(
            request.difficulty,
            request.time_signature,
            request.measures_count.value,
            request.tempo.value,
            request.tonality,
            request.tonality_choice,
        )

        # 使用系统化方法生成错误选项
        wrong_options = self._generate_wrong_options_systematic(correct_melody, request, count=4)

        # 确保每个错误选项都是唯一的
        unique_wrong_options = []
        for wrong_melody in wrong_options:
            if self._is_unique_melody(wrong_melody, unique_wrong_options) and self._is_unique_melody(wrong_melody, [correct_melody]):
                unique_wrong_options.append(wrong_melody)

        # 如果生成的唯一错误选项不足3个，使用基本变化补充
        while len(unique_wrong_options) < 3:
            basic_wrong = correct_melody.copy(deep=True)
            basic_wrong.is_correct = False
            # 将第一个音符改为变化音作为基本变化
            if (len(basic_wrong.measures) > 0 and 
                len(basic_wrong.measures[0]) > 0 and 
                len(basic_wrong.measures[0][0].notes) > 0):
                note = basic_wrong.measures[0][0].notes[0]
                new_pitch = self._get_variant_pitch(note.pitch)
                note.pitch = new_pitch
            if self._is_unique_melody(basic_wrong, unique_wrong_options) and self._is_unique_melody(basic_wrong, [correct_melody]):
                unique_wrong_options.append(basic_wrong)

        # 随机排列选项
        all_options = [correct_melody] + unique_wrong_options
        random.shuffle(all_options)

        # 找出正确答案的位置
        correct_answer = chr(65 + all_options.index(correct_melody))  # A, B, C, or D

        return MelodyQuestionResponse(
            correct_answer=correct_answer,  # 传入正确的旋律对象
            options=all_options,
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
        """生成一个正确的旋律"""
        # 使用rhythm_service生成节奏
        rhythm = rhythm_service.generate_rhythm(
            difficulty,
            time_signature,
            measures_count,
            tempo
        )

        # 获取音高列表
        pitch_list = self.get_pitch_list(tonality, tonality_choice, difficulty)
        pitch_index = 0

        # 将节奏转换为旋律
        measures = []
        for measure_group in rhythm.measures:
            measures_sub = []
            for measure in measure_group:
                notes = []
                for note in measure.notes:
                    melody_note = MelodyNotePitch(
                        duration=note.duration,
                        pitch=pitch_list[pitch_index % len(pitch_list)],
                        is_rest=note.is_rest,
                        is_dotted=note.is_dotted,
                        tied_to_next=note.tied_to_next
                    )
                    notes.append(melody_note)
                    pitch_index += 1
                measures_sub.append(MelodyMeasurePitch(notes=notes))
            measures.append(measures_sub)

        return MelodyScorePitch(
            measures=measures,
            time_signature=time_signature,
            tempo=tempo,
            is_correct=True
        )

    def _generate_wrong_options_systematic(self, correct_melody: MelodyScorePitch, request: MelodySettingRequest, count: int = 3) -> List[MelodyScorePitch]:
        """系统化生成错误选项
        
        Args:
            correct_melody: 正确的旋律
            request: 请求参数，包含调式和调式选择类型
            count: 需要生成的错误选项数量
            
        Returns:
            List[MelodyScorePitch]: 错误选项列表
        """
        wrong_options = []
        variation_rules = [
            lambda m: self._apply_scale_change(m, request),  # 改变音阶类型
            lambda m: self._apply_tonality_change(m, request),  # 改变调式
            self._apply_accidental_change,  # 添加变化音
            self._apply_octave_shift,  # 移动八度
            self._apply_note_reorder,  # 改变音符顺序
            self._apply_measure_structure_change,  # 改变小节结构
            self._apply_rhythm_shift  # 移动节奏位置
        ]

        while len(wrong_options) < count:
            # 复制正确的旋律
            wrong_melody = copy.deepcopy(correct_melody)
            wrong_melody.is_correct = False

            # 随机选择变化规则
            variation_rule = random.choice(variation_rules)
            variation_rule(wrong_melody)

            # 检查是否与现有选项重复
            if self._is_unique_melody(wrong_melody, wrong_options):
                wrong_options.append(wrong_melody)

        return wrong_options

    def _apply_scale_change(self, melody: MelodyScorePitch, request: MelodySettingRequest) -> None:
        """改变音阶类型，确保生成不同的音高序列"""
        # 获取所有可用的调式选择类型
        available_choices = [
            t for t in TonalityChoice
            if t != self.get_tonality_choice(request.tonality_choice)
        ]
        if available_choices:
            # 尝试不同的调式选择类型，直到找到生成不同音高序列的
            for _ in range(3):  # 最多尝试3次
                new_choice = random.choice(available_choices)
                pitch_list = self.get_pitch_list(
                    request.tonality,
                    new_choice.get_index(),
                    request.difficulty
                )
                # 检查新生成的音高序列是否与原始旋律不同
                if not self._are_pitch_sequences_similar(melody, pitch_list):
                    self._update_melody_pitches(melody, pitch_list)
                    return

    def _apply_tonality_change(self, melody: MelodyScorePitch, request: MelodySettingRequest) -> None:
        """改变调式，确保生成不同的音高序列"""
        # 获取所有可用的调式
        available_tonalities = [
            t for t in Tonality
            if t != self.get_tonality(request.tonality)
        ]
        if available_tonalities:
            # 尝试不同的调式，直到找到生成不同音高序列的
            for _ in range(3):  # 最多尝试3次
                new_tonality = random.choice(available_tonalities)
                pitch_list = self.get_pitch_list(
                    new_tonality.get_index(),
                    request.tonality_choice,
                    request.difficulty
                )
                # 检查新生成的音高序列是否与原始旋律不同
                if not self._are_pitch_sequences_similar(melody, pitch_list):
                    self._update_melody_pitches(melody, pitch_list)
                    return

    def _apply_accidental_change(self, melody: MelodyScorePitch) -> None:
        """添加变化音，确保至少改变一个音符"""
        changed = False
        for measure_group in melody.measures:
            for measure in measure_group:
                for note in measure.notes:
                    if not note.is_rest and random.random() < 0.3:  # 30%的概率改变音符
                        new_pitch = self._get_variant_pitch(note.pitch)
                        if new_pitch and new_pitch.pitch_number != note.pitch.pitch_number:
                            note.pitch = new_pitch
                            changed = True
                            break
                if changed:
                    break
            if changed:
                break

    def _apply_octave_shift(self, melody: MelodyScorePitch) -> None:
        """移动八度，确保至少改变一个音符"""
        changed = False
        for measure_group in melody.measures:
            for measure in measure_group:
                for note in measure.notes:
                    if not note.is_rest and random.random() < 0.3:  # 30%的概率改变音符
                        # 随机选择向上或向下移动八度
                        shift = 12 if random.random() < 0.5 else -12
                        new_pitch_num = note.pitch.pitch_number + shift
                        if 0 <= new_pitch_num <= 88:
                            new_pitch = pitch_service.get_pitch_by_number(new_pitch_num)
                            if new_pitch:
                                note.pitch = new_pitch
                                changed = True
                                break
                if changed:
                    break
            if changed:
                break

    def _apply_note_reorder(self, melody: MelodyScorePitch) -> None:
        """改变音符顺序，确保至少改变一个小节的音符顺序"""
        for measure_group in melody.measures:
            for measure in measure_group:
                # 只处理非休止符的音符
                notes = [note for note in measure.notes if not note.is_rest]
                if len(notes) > 1:
                    # 随机选择两个不同的音符交换位置
                    idx1, idx2 = random.sample(range(len(notes)), 2)
                    notes[idx1], notes[idx2] = notes[idx2], notes[idx1]
                    return

    def _apply_measure_structure_change(self, melody: MelodyScorePitch) -> None:
        """改变小节结构，确保至少改变一个小节的结构"""
        for measure_group in melody.measures:
            if len(measure_group) > 1:
                # 随机选择两个不同的小节交换位置
                idx1, idx2 = random.sample(range(len(measure_group)), 2)
                measure_group[idx1], measure_group[idx2] = measure_group[idx2], measure_group[idx1]
                return

    def _apply_rhythm_shift(self, melody: MelodyScorePitch) -> None:
        """移动节奏位置，确保至少改变一个音符的节奏"""
        for measure_group in melody.measures:
            for measure in measure_group:
                for note in measure.notes:
                    if not note.is_rest and random.random() < 0.3:  # 30%的概率改变音符
                        # 随机改变音符的时值
                        new_duration = random.choice([0.25, 0.5, 1.0, 2.0])
                        if new_duration != note.duration:
                            note.duration = new_duration
                            return

    def _update_melody_pitches(self, melody: MelodyScorePitch, pitch_list: List[Pitch]) -> None:
        """更新旋律中的音高"""
        pitch_index = 0
        for measure_group in melody.measures:
            for measure in measure_group:
                for note in measure.notes:
                    if not note.is_rest:
                        note.pitch = pitch_list[pitch_index % len(pitch_list)]
                        pitch_index += 1

    def _get_variant_pitch(self, pitch: Pitch) -> Pitch:
        """获取变化音"""
        if pitch.pitch_number == 88:
            return pitch
        change_num = pitch.pitch_number + random.randint(1, 88 - pitch.pitch_number)
        return pitch_service.get_pitch_by_number(change_num)

    def _is_unique_melody(self, new_melody: MelodyScorePitch, existing_melodies: List[MelodyScorePitch]) -> bool:
        """检查新生成的旋律是否与现有的错误答案不同"""
        for existing in existing_melodies:
            if self._are_melodies_similar(new_melody, existing):
                return False
        return True

    def _are_melodies_similar(self, melody1: MelodyScorePitch, melody2: MelodyScorePitch) -> bool:
        """比较两个旋律是否相似"""
        if len(melody1.measures) != len(melody2.measures):
            return False
            
        for measure_group1, measure_group2 in zip(melody1.measures, melody2.measures):
            if len(measure_group1) != len(measure_group2):
                return False
                
            for m1, m2 in zip(measure_group1, measure_group2):
                if len(m1.notes) != len(m2.notes):
                    return False
                    
                for n1, n2 in zip(m1.notes, m2.notes):
                    if (n1.duration != n2.duration or
                        n1.is_rest != n2.is_rest or
                        n1.is_dotted != n2.is_dotted or
                        n1.pitch.pitch_number != n2.pitch.pitch_number):
                        return False
                    
        return True

    def _are_measures_similar(self, measure1: List[MelodyMeasurePitch], measure2: List[MelodyMeasurePitch]) -> bool:
        """比较两个小节是否相似"""
        if len(measure1) != len(measure2):
            return False
            
        for m1, m2 in zip(measure1, measure2):
            if len(m1.notes) != len(m2.notes):
                return False
                
            for n1, n2 in zip(m1.notes, m2.notes):
                if (n1.duration != n2.duration or
                    n1.is_rest != n2.is_rest or
                    n1.is_dotted != n2.is_dotted or
                    n1.pitch.pitch_number != n2.pitch.pitch_number):
                    return False
                    
        return True

    def _are_pitch_sequences_similar(self, melody: MelodyScorePitch, pitch_list: List[Pitch]) -> bool:
        """检查旋律的音高序列是否与给定的音高列表相似"""
        pitch_index = 0
        for measure_group in melody.measures:
            for measure in measure_group:
                for note in measure.notes:
                    if not note.is_rest:
                        if note.pitch.pitch_number == pitch_list[pitch_index % len(pitch_list)].pitch_number:
                            return True
                        pitch_index += 1
        return False

    def get_pitch_list(self, tonality: int, tonality_choice: int, difficulty: RhythmDifficulty) -> List[Pitch]:
        """获取指定调式和调式选择类型的音高列表"""
        try:
            t = self.get_tonality(tonality)
            choice = self.get_tonality_choice(tonality_choice)
            root_note = t.get_root_note()
            interval_nums = choice.get_interval_nums()
            pitch_list: List[Pitch] = []
            num = random.randint(1, 7)
            
            for interval_num in interval_nums:
                pitch_name = f'{root_note}{num}'
                pitches = pitch_service.get_pitch_by_name(pitch_name)
                if not pitches or len(pitches) != 1:
                    # 如果找不到指定的音高，使用默认音高
                    default_pitch = pitch_service.get_pitch_by_number(60)  # 使用C4作为默认音高
                    if default_pitch:
                        pitch = default_pitch
                    else:
                        # 如果连默认音高都找不到，使用一个安全的音高范围
                        pitch = pitch_service.get_pitch_by_number(60 + interval_num)
                else:
                    pitch = pitches[0]
                
                # 确保音高在有效范围内
                target_pitch_num = pitch.pitch_number + interval_num
                if target_pitch_num < 0:
                    target_pitch_num = 0
                elif target_pitch_num > 88:
                    target_pitch_num = 88
                
                pitch = pitch_service.get_pitch_by_number(target_pitch_num)
                if pitch:
                    pitch_list.append(pitch)

            if not pitch_list:
                # 如果音高列表为空，返回一个默认的音高序列
                return [pitch_service.get_pitch_by_number(i) for i in range(60, 67) if pitch_service.get_pitch_by_number(i)]

            if difficulty == RhythmDifficulty.MEDIUM:
                point = random.randint(1, len(pitch_list) - 1)
                pitch_list = pitch_list[point:] + pitch_list[:point]
            elif difficulty == RhythmDifficulty.HIGH:
                pitch_list = random.sample(pitch_list, len(pitch_list))

            return pitch_list
        except Exception as e:
            logger.error(f"Error in get_pitch_list: {str(e)}")
            # 返回一个安全的默认音高序列
            return [pitch_service.get_pitch_by_number(i) for i in range(60, 67) if pitch_service.get_pitch_by_number(i)]

    def get_tonality(self, index: int) -> Tonality:
        """获取指定索引的调式"""
        for tonality in Tonality:
            if tonality._index == index:
                return tonality

    def get_tonality_choice(self, index: int) -> TonalityChoice:
        """获取指定索引的调式选择类型"""
        for tc in TonalityChoice:
            if tc._index == index:
                return tc


melody_service = MelodyService()