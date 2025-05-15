import unittest
from app.services.melody_service import MelodyService
from app.models.rhythm_settings import RhythmDifficulty, TimeSignature
from app.api.v1.schemas.request.pitch_request import MelodyQuestionRequest

class TestMelodyService(unittest.TestCase):
    def setUp(self):
        self.melody_service = MelodyService()
        self.test_request = MelodyQuestionRequest(
            difficulty=RhythmDifficulty.LOW,
            time_signature=TimeSignature.TWO_FOUR,
            measures_count=4,
            tempo=80,
            tonality="C",
            tonality_choice="major"
        )

    def test_apply_scale_change(self):
        """测试音阶变化"""
        melody = self.melody_service._apply_scale_change(self.test_request)
        self.assertIsNotNone(melody)
        self.assertIsNotNone(melody.measures)
        self.assertIsNotNone(melody.time_signature)
        self.assertIsNotNone(melody.tempo)

    def test_apply_tonality_change(self):
        """测试调性变化"""
        melody = self.melody_service._apply_tonality_change(self.test_request)
        self.assertIsNotNone(melody)
        self.assertIsNotNone(melody.measures)
        self.assertIsNotNone(melody.time_signature)
        self.assertIsNotNone(melody.tempo)

    def test_apply_accidental_change(self):
        """测试变音变化"""
        melody = self.melody_service._apply_accidental_change(self.test_request)
        self.assertIsNotNone(melody)
        self.assertIsNotNone(melody.measures)
        self.assertIsNotNone(melody.time_signature)
        self.assertIsNotNone(melody.tempo)

    def test_apply_octave_shift(self):
        """测试八度变化"""
        melody = self.melody_service._apply_octave_shift(self.test_request)
        self.assertIsNotNone(melody)
        self.assertIsNotNone(melody.measures)
        self.assertIsNotNone(melody.time_signature)
        self.assertIsNotNone(melody.tempo)

    def test_apply_note_reorder(self):
        """测试音符重排"""
        melody = self.melody_service._apply_note_reorder(self.test_request)
        self.assertIsNotNone(melody)
        self.assertIsNotNone(melody.measures)
        self.assertIsNotNone(melody.time_signature)
        self.assertIsNotNone(melody.tempo)

    def test_apply_measure_structure_change(self):
        """测试小节结构变化"""
        melody = self.melody_service._apply_measure_structure_change(self.test_request)
        self.assertIsNotNone(melody)
        self.assertIsNotNone(melody.measures)
        self.assertIsNotNone(melody.time_signature)
        self.assertIsNotNone(melody.tempo)

    def test_apply_rhythm_shift(self):
        """测试节奏变化"""
        melody = self.melody_service._apply_rhythm_shift(self.test_request)
        self.assertIsNotNone(melody)
        self.assertIsNotNone(melody.measures)
        self.assertIsNotNone(melody.time_signature)
        self.assertIsNotNone(melody.tempo)

    def test_generate_wrong_options_systematic(self):
        """测试生成错误选项"""
        options = self.melody_service._generate_wrong_options_systematic(self.test_request)
        self.assertIsNotNone(options)
        self.assertEqual(len(options), 4)  # 应该有4个选项
        for option in options:
            self.assertIsNotNone(option.measures)
            self.assertIsNotNone(option.time_signature)
            self.assertIsNotNone(option.tempo)

    def test_generate_melody_question(self):
        """测试生成旋律问题"""
        question = self.melody_service.generate_melody_question(self.test_request)
        self.assertIsNotNone(question)
        self.assertIsNotNone(question.measures)
        self.assertIsNotNone(question.time_signature)
        self.assertIsNotNone(question.tempo)
        self.assertIsNotNone(question.options)
        self.assertEqual(len(question.options), 4)  # 应该有4个选项

if __name__ == '__main__':
    unittest.main() 