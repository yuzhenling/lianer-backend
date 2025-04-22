import time
from typing import List, Optional, Dict, Any
import random
import logging

from app.api.v1.schemas.request.pitch_request import MelodyQuestionRequest
from app.api.v1.schemas.response.pitch_response import MelodyQuestionResponse, MelodyScorePitch, MelodyNotePitch, \
    MelodyMeasurePitch
from app.core.logger import logger
from app.models.rhythm_settings import RhythmDifficulty
from app.services.melody_service import MelodyService, melody_service
from app.core.config import settings
import requests
import json

from app.services.pitch_service import pitch_service


class AIMelodyService:
    def __init__(self):
        self.melody_service = MelodyService()
        self.deepseek_api_key = settings.DEEPSEEK_API_KEY
        self.deepseek_api_url = settings.DEEPSEEK_API_URL
        self.difficulty_durations = {
            RhythmDifficulty.LOW: [1.0, 0.5],  # 四分音符和八分音符
            RhythmDifficulty.MEDIUM: [1.0, 0.5, 0.25, 1.5],  # 四分音符、八分音符、十六分音符和附点四分音符
            RhythmDifficulty.HIGH: [1.0, 0.5, 0.25, 0.125, 1.5, 0.75]  # 所有时值
        }
        self.difficulty_durations_desc = {
            RhythmDifficulty.LOW: ["四分音符", "八分音符"],  # 四分音符和八分音符
            RhythmDifficulty.MEDIUM: ["四分音符", "八分音符", "十六分音符", "附点四分音符"],  # 四分音符、八分音符、十六分音符和附点四分音符
            RhythmDifficulty.HIGH: ["四分音符", "八分音符", "十六分音符","三十二分音符", "附点八分音符", "附点四分音符"]  # 所有时值
        }
        logger.info("AIMelodyService initialized with DeepSeek API configuration")

    async def generate_melody_question(self, request: MelodyQuestionRequest) -> MelodyQuestionResponse:
        """生成旋律听写题，使用AI生成主旋律"""
        try:
            logger.info(f"Generating melody question with parameters: {request.dict()}")
            
            # 1. 使用DeepSeek生成主旋律
            correct_melody = await self._generate_ai_melody(request)
            logger.info("Successfully generated correct melody")

            # 使用系统化方法生成错误选项
            wrong_options = melody_service._generate_wrong_options_systematic(correct_melody, request, count=4)
            logger.info(f"Generated {len(wrong_options)} wrong options using systematic method")

            # 确保每个错误选项都是唯一的
            unique_wrong_options = []
            for wrong_melody in wrong_options:
                if melody_service._is_unique_melody(wrong_melody, unique_wrong_options) and melody_service._is_unique_melody(wrong_melody, [correct_melody]):
                    unique_wrong_options.append(wrong_melody)
                if len(unique_wrong_options) == 3:
                    break
            logger.info(f"Found {len(unique_wrong_options)} unique wrong options")

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
                if melody_service._is_unique_melody(basic_wrong, unique_wrong_options) and melody_service._is_unique_melody(basic_wrong, [correct_melody]):
                    unique_wrong_options.append(basic_wrong)
            logger.info(f"Added basic variations, total unique wrong options: {len(unique_wrong_options)}")

            # 随机排列选项
            all_options = [correct_melody] + unique_wrong_options
            random.shuffle(all_options)
            logger.info("Randomized all options")

            # 找出正确答案的位置
            correct_answer = chr(65 + all_options.index(correct_melody))  # A, B, C, or D
            logger.info(f"Correct answer is option {correct_answer}")

            response = MelodyQuestionResponse(
                correct_answer=correct_answer,  # 传入正确的旋律对象
                options=all_options,
                tempo=request.tempo,
                time_signature=request.time_signature,
                measures_count=request.measures_count,
                difficulty=request.difficulty
            )
            logger.info("Successfully created melody question response")
            return response
        except Exception as e:
            logger.error(f"Error generating AI melody question: {str(e)}", exc_info=True)
            raise

    async def _generate_ai_melody(self, request: MelodyQuestionRequest) -> MelodyScorePitch:
        """使用DeepSeek生成旋律"""
        try:
            logger.info("Starting AI melody generation")
            
            # 构建提示词
            prompt = self._build_melody_prompt(request)
            logger.debug(f"Generated prompt: {prompt}")
            
            # 调用DeepSeek API
            response = await self._call_deepseek_api(prompt)
            logger.info("Successfully received response from DeepSeek API")
            
            # 解析响应并转换为MelodyScorePitch对象
            melody = self._parse_ai_response(response, request)
            # melody = self._parse_ai_response({}, request)
            logger.info("Successfully parsed AI response into melody")
            
            return melody
        except Exception as e:
            logger.error(f"Error generating AI melody: {str(e)}", exc_info=True)
            raise

    def _build_melody_prompt(self, request: MelodyQuestionRequest) -> str:
        """构建提示词"""
        logger.debug("Building melody prompt")
        durations_desc = []
        if request.difficulty == RhythmDifficulty.HIGH:
            durations_desc = self.difficulty_durations_desc[request.difficulty]
        elif request.difficulty == RhythmDifficulty.MEDIUM:
            durations_desc = self.difficulty_durations_desc[request.difficulty]
        else:
            durations_desc = self.difficulty_durations_desc[RhythmDifficulty.LOW]

        tonality = melody_service.get_tonality(request.tonality)
        tonality_choice = melody_service.get_tonality_choice(request.tonality_choice)

        prompt = f"""
        请随机生成一个{request.measures_count.value}小节的旋律，要求：
        1. 拍号：{request.time_signature.value}
        2. 速度：{request.tempo.value}bpm
        3. 难度：{request.difficulty.value},仅限包含音符:{durations_desc}
        4. 调性：{tonality.display_value}
        5. 调式：{tonality_choice.display_value}
        
        旋律要求：
        1. 音程关系自然，避免大跳
        2. 节奏型合理，符合{request.time_signature.value}拍号特点
        3. 旋律线条流畅，有音乐性
        4. 适当使用重复音型和模进
        5. 结尾要有终止感
        
        请严格按照以下JSON格式返回，包含每个音符的音高和时值：
        {{
            "measures": [  //measures代表全部小节的旋律， 由{request.measures_count.value}决定
                [
                    {{
                        "notes": [ //notes代表一个小节的旋律，它里面包含小节中的时值、音高等信息 
                            {{
                                "duration": 0.5,  // 时值：0.5表示八分音符，1表示四分音符，0.25表示十六分音符，0.125表示三十二分音符，0.75表示附点八分音符，1.5表示附点四分音符，
                                "is_rest": false,  // 是否为休止符
                                "is_dotted": false,  // 是否为附点音符
                                "tied_to_next": false,  // 是否与下一个音符相连
                                "pitch": "C2",  // 音高名称
                            }}
                        ]
                    }}
                ]
            ]
        }}

        注意事项：
        1. 每个小节的音符时值总和必须等于拍号指定的拍数
        2. 音高范围：根据调性和调式选取对应的音高范围
        3. 音符必须是难度中列举出的音符
        4. 确保返回的JSON格式完全符合上述结构
        5. 所有布尔值使用false而不是"false"
        6. 所有数值不使用引号
        
        """
        logger.debug(f"Generated prompt: {prompt}")
        return prompt

    async def _call_deepseek_api(self, prompt: str) -> Dict[str, Any]:
        """调用DeepSeek API"""
        logger.info("Calling DeepSeek API")
        start_time = time.time()
        headers = {
            "Authorization": f"Bearer {self.deepseek_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.5,
            "max_tokens": 5000,
            "stream": False,
            "top_p": 0.9,
        }
        
        logger.debug(f"API request data: {json.dumps(data, ensure_ascii=False)}")
        
        response = requests.post(
            self.deepseek_api_url,
            headers=headers,
            json=data
        )
        
        if response.status_code != 200:
            logger.error(f"DeepSeek API error: {response.text}")
            raise Exception(f"DeepSeek API error: {response.text}")
            
        logger.info(f"Successfully received response from DeepSeek API. Time cost={time.time()-start_time}")
        return response.json()


    def _parse_ai_response(self, response: Dict[str, Any], request: MelodyQuestionRequest) -> MelodyScorePitch:
        """解析AI响应并转换为MelodyScorePitch对象"""
        try:
            logger.info("Parsing AI response")
            # 解析AI返回的JSON
            content = response["choices"][0]["message"]["content"]
            cleaned_content = content.strip().removeprefix('```json').removesuffix('```').strip()
            melody_data = json.loads(cleaned_content)
#             data = """
# {
#     "measures": [
#         [
#             {
#                 "notes": [
#                     {
#                         "duration": 0.5,
#                         "is_rest": false,
#                         "is_dotted": false,
#                         "tied_to_next": false,
#                         "pitch": "C4"
#                     },
#                     {
#                         "duration": 0.5,
#                         "is_rest": false,
#                         "is_dotted": false,
#                         "tied_to_next": false,
#                         "pitch": "D4"
#                     },
#                     {
#                         "duration": 0.5,
#                         "is_rest": false,
#                         "is_dotted": false,
#                         "tied_to_next": false,
#                         "pitch": "E4"
#                     },
#                     {
#                         "duration": 0.5,
#                         "is_rest": false,
#                         "is_dotted": false,
#                         "tied_to_next": false,
#                         "pitch": "G4"
#                     }
#                 ]
#             }
#         ],
#         [
#             {
#                 "notes": [
#                     {
#                         "duration": 1,
#                         "is_rest": false,
#                         "is_dotted": false,
#                         "tied_to_next": false,
#                         "pitch": "E4"
#                     },
#                     {
#                         "duration": 0.5,
#                         "is_rest": false,
#                         "is_dotted": false,
#                         "tied_to_next": false,
#                         "pitch": "D4"
#                     },
#                     {
#                         "duration": 0.5,
#                         "is_rest": false,
#                         "is_dotted": false,
#                         "tied_to_next": false,
#                         "pitch": "C4"
#                     }
#                 ]
#             }
#         ],
#         [
#             {
#                 "notes": [
#                     {
#                         "duration": 0.5,
#                         "is_rest": false,
#                         "is_dotted": false,
#                         "tied_to_next": false,
#                         "pitch": "E4"
#                     },
#                     {
#                         "duration": 0.5,
#                         "is_rest": false,
#                         "is_dotted": false,
#                         "tied_to_next": false,
#                         "pitch": "G4"
#                     },
#                     {
#                         "duration": 0.5,
#                         "is_rest": false,
#                         "is_dotted": false,
#                         "tied_to_next": false,
#                         "pitch": "A4"
#                     },
#                     {
#                         "duration": 0.5,
#                         "is_rest": false,
#                         "is_dotted": false,
#                         "tied_to_next": false,
#                         "pitch": "G4"
#                     }
#                 ]
#             }
#         ],
#         [
#             {
#                 "notes": [
#                     {
#                         "duration": 1,
#                         "is_rest": false,
#                         "is_dotted": false,
#                         "tied_to_next": false,
#                         "pitch": "E4"
#                     },
#                     {
#                         "duration": 1,
#                         "is_rest": false,
#                         "is_dotted": false,
#                         "tied_to_next": false,
#                         "pitch": "C4"
#                     }
#                 ]
#             }
#         ]
#     ]
# }
#             """
#             melody_data = json.loads(data)
            logger.debug(f"Parsed melody data: {json.dumps(melody_data, ensure_ascii=False)}")
            
            # 转换为MelodyScorePitch对象
            # 创建measures列表
            measures = []
            for measure_group in melody_data["measures"]:
                measures_sub = []
                for measure in measure_group:
                    notes = []
                    for note_data in measure["notes"]:
                        # 创建Pitch对象
                        pitch_name = note_data["pitch"]
                        # 根据音高名称获取pitch_number
                        pitch = pitch_service.get_pitch_by_name(pitch_name)
                        if pitch is None or len(pitch) != 1:
                            logger.error(f"Pitch {pitch_name} not found")
                            continue

                        melody_note = MelodyNotePitch(
                            duration=note_data["duration"],
                            pitch=pitch[0],
                            is_rest=note_data["is_rest"],
                            is_dotted=note_data["is_dotted"],
                            tied_to_next=note_data["tied_to_next"],
                        )
                        notes.append(melody_note)
                    measures_sub.append(MelodyMeasurePitch(notes=notes))
                measures.append(measures_sub)

            # 创建MelodyScorePitch对象
            melody = MelodyScorePitch(
                measures=measures,
                time_signature=request.time_signature,
                tempo=request.tempo,
                is_correct=True
            )

            logger.info("Successfully created MelodyScorePitch object")
            return melody
        except Exception as e:
            logger.error(f"Error parsing AI response: {str(e)}", exc_info=True)
            raise



ai_melody_service = AIMelodyService()