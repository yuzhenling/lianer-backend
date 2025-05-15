import unittest
from app.services.rhythm_service import RhythmService
from app.models.rhythm_settings import RhythmDifficulty, TimeSignature
from app.api.v1.schemas.request.rhythm_request import RhythmQuestionRequest

class TestRhythmService(unittest.TestCase):
    def setUp(self):
        self.rhythm_service = RhythmService()
        self.test_request = RhythmQuestionRequest(
            difficulty=RhythmDifficulty.LOW,
            time_signature=TimeSignature.TWO_FOUR,
            measures_count=4,
            tempo=80
        )

    def test_generate_rhythm_combinations(self):
        """测试生成节奏组合"""
        combinations = self.rhythm_service._generate_rhythm_combinations(
            self.test_request.difficulty,
            self.test_request.time_signature
        )
        self.assertIsNotNone(combinations)
        self.assertGreater(len(combinations), 0)
        for combo in combinations:
            self.assertIsNotNone(combo.measures)
            self.assertIsNotNone(combo.time_signature)
            self.assertIsNotNone(combo.tempo)

    def test_generate_rhythm(self):
        """测试生成节奏"""
        rhythm = self.rhythm_service.generate_rhythm(self.test_request)
        self.assertIsNotNone(rhythm)
        self.assertIsNotNone(rhythm.measures)
        self.assertIsNotNone(rhythm.time_signature)
        self.assertIsNotNone(rhythm.tempo)

    def test_generate_question(self):
        """测试生成节奏问题"""
        question = self.rhythm_service.generate_question(self.test_request)
        self.assertIsNotNone(question)
        self.assertIsNotNone(question.measures)
        self.assertIsNotNone(question.time_signature)
        self.assertIsNotNone(question.tempo)
        self.assertIsNotNone(question.options)
        self.assertEqual(len(question.options), 4)  # 应该有4个选项

    def test_different_difficulties(self):
        """测试不同难度级别"""
        difficulties = [RhythmDifficulty.LOW, RhythmDifficulty.MEDIUM, RhythmDifficulty.HIGH]
        for difficulty in difficulties:
            request = RhythmQuestionRequest(
                difficulty=difficulty,
                time_signature=TimeSignature.TWO_FOUR,
                measures_count=4,
                tempo=80
            )
            question = self.rhythm_service.generate_question(request)
            self.assertIsNotNone(question)
            self.assertIsNotNone(question.measures)
            self.assertIsNotNone(question.time_signature)
            self.assertIsNotNone(question.tempo)

    def test_different_time_signatures(self):
        """测试不同拍号"""
        time_signatures = [
            TimeSignature.TWO_FOUR,
            TimeSignature.THREE_FOUR,
            TimeSignature.FOUR_FOUR
        ]
        for time_signature in time_signatures:
            request = RhythmQuestionRequest(
                difficulty=RhythmDifficulty.LOW,
                time_signature=time_signature,
                measures_count=4,
                tempo=80
            )
            question = self.rhythm_service.generate_question(request)
            self.assertIsNotNone(question)
            self.assertIsNotNone(question.measures)
            self.assertEqual(question.time_signature, time_signature.value)
            self.assertIsNotNone(question.tempo)

if __name__ == '__main__':
    unittest.main() 