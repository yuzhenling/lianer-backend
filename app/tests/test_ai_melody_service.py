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

    def test_parse_ai_response(self):
        """测试解析AI响应的功能"""
        # 模拟DeepSeek API的响应
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
                                            },
                                            {
                                                "duration": 0.5,
                                                "is_rest": false,
                                                "is_dotted": false,
                                                "tied_to_next": false,
                                                "pitch": {
                                                    "id": 42,
                                                    "pitch_number": 42,
                                                    "name": "D4",
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

        # 调用_parse_ai_response方法
        melody = self.ai_melody_service._parse_ai_response(test_response, self.test_request)

        # 验证结果
        self.assertIsNotNone(melody)
        self.assertEqual(len(melody.measures), 1)  # 验证小节数量
        self.assertEqual(len(melody.measures[0]), 1)  # 验证每个小节组中的小节数量
        self.assertEqual(len(melody.measures[0][0]["notes"]), 2)  # 验证音符数量
        
        # 验证第一个音符
        first_note = melody.measures[0][0]["notes"][0]
        self.assertEqual(first_note["duration"], 0.5)
        self.assertEqual(first_note["is_rest"], False)
        self.assertEqual(first_note["is_dotted"], False)
        self.assertEqual(first_note["tied_to_next"], False)
        self.assertEqual(first_note["pitch"].name, "C4")
        self.assertEqual(first_note["pitch"].pitch_number, 40)

        # 验证第二个音符
        second_note = melody.measures[0][0]["notes"][1]
        self.assertEqual(second_note["duration"], 0.5)
        self.assertEqual(second_note["is_rest"], False)
        self.assertEqual(second_note["is_dotted"], False)
        self.assertEqual(second_note["tied_to_next"], False)
        self.assertEqual(second_note["pitch"].name, "D4")
        self.assertEqual(second_note["pitch"].pitch_number, 42)

if __name__ == '__main__':
    unittest.main() 