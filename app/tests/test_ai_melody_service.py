import unittest
from app.services.ai_melody_service import AIMelodyService
from app.models.rhythm_settings import RhythmDifficulty, TimeSignature
from app.api.v1.schemas.request.pitch_request import MelodyQuestionRequest

class TestAIMelodyService(unittest.TestCase):
    def setUp(self):
        self.ai_melody_service = AIMelodyService()
        self.test_request = MelodyQuestionRequest(
            difficulty=RhythmDifficulty.LOW,
            time_signature=TimeSignature.TWO_FOUR,
            measures_count=4,
            tempo=80,
            tonality="C",
            tonality_choice="major"
        )

    def test_build_melody_prompt(self):
        """测试构建旋律提示词"""
        prompt = self.ai_melody_service._build_melody_prompt(self.test_request)
        self.assertIsNotNone(prompt)
        self.assertIn("2/4", prompt)
        self.assertIn("C", prompt)
        self.assertIn("major", prompt)
        self.assertIn("JSON", prompt)

    def test_parse_ai_response(self):
        """测试解析AI响应"""
        test_response = {
            "choices": [
                {
                    "message": {
                        "content": """
                        {
                            "measures": [
                                [
                                    {
                                        "notes": [
                                            {
                                                "duration": 0.5,
                                                "is_rest": false,
                                                "is_dotted": false,
                                                "tied_to_next": false,
                                                "pitch": {
                                                    "id": 40,
                                                    "pitch_number": 40,
                                                    "name": "C4",
                                                    "alias": null
                                                }
                                            }
                                        ]
                                    }
                                ]
                            ],
                            "time_signature": "2/4",
                            "tempo": 80
                        }
                        """
                    }
                }
            ]
        }

        melody = self.ai_melody_service._parse_ai_response(test_response, self.test_request)
        self.assertIsNotNone(melody)
        self.assertEqual(len(melody.measures), 1)
        self.assertEqual(len(melody.measures[0][0]["notes"]), 1)
        self.assertEqual(melody.measures[0][0]["notes"][0]["pitch"].name, "C4")

    def test_generate_melody(self):
        """测试生成旋律"""
        melody = self.ai_melody_service.generate_melody(self.test_request)
        self.assertIsNotNone(melody)
        self.assertIsNotNone(melody.measures)
        self.assertIsNotNone(melody.time_signature)
        self.assertIsNotNone(melody.tempo)

if __name__ == '__main__':
    unittest.main() 