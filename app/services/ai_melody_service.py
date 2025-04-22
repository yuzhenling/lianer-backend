from typing import List, Optional, Dict, Any
import random
import logging

from app.api.v1.schemas.request.pitch_request import MelodyQuestionRequest
from app.api.v1.schemas.response.pitch_response import MelodyQuestionResponse, MelodyScorePitch
from app.models.pitch import Pitch
from app.models.rhythm_settings import RhythmDifficulty
from app.services.melody_service import MelodyService, melody_service
from app.core.config import settings
import requests
import json

logger = logging.getLogger(__name__)

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

    async def generate_melody_question(self, request: MelodyQuestionRequest) -> MelodyQuestionResponse:
        """生成旋律听写题，使用AI生成主旋律"""
        try:
            # 1. 使用DeepSeek生成主旋律
            correct_melody = await self._generate_ai_melody(request)

            # 使用系统化方法生成错误选项
            wrong_options = melody_service._generate_wrong_options_systematic(correct_melody, request, count=4)

            # 确保每个错误选项都是唯一的
            unique_wrong_options = []
            for wrong_melody in wrong_options:
                if self._is_unique_melody(wrong_melody, unique_wrong_options) and self._is_unique_melody(wrong_melody, [
                    correct_melody]):
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
                if self._is_unique_melody(basic_wrong, unique_wrong_options) and self._is_unique_melody(basic_wrong, [
                    correct_melody]):
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
        except Exception as e:
            logger.error(f"Error generating AI melody question: {str(e)}")
            raise

    async def _generate_ai_melody(self, request: MelodyQuestionRequest) -> MelodyScorePitch:
        """使用DeepSeek生成旋律"""
        try:
            # 构建提示词
            prompt = self._build_melody_prompt(request)
            
            # 调用DeepSeek API
            response = await self._call_deepseek_api(prompt)
            
            # 解析响应并转换为MelodyScorePitch对象
            melody = self._parse_ai_response(response, request)
            
            return melody
        except Exception as e:
            logger.error(f"Error generating AI melody: {str(e)}")
            raise

    def _build_melody_prompt(self, request: MelodyQuestionRequest) -> str:
        durations_desc = []
        if request.difficulty == RhythmDifficulty.HIGH:
            durations_desc = self.difficulty_durations[request.difficulty]
        elif request.difficulty == RhythmDifficulty.MEDIUM:
            durations_desc = self.difficulty_durations[request.difficulty]
        else:
            durations_desc = self.difficulty_durations[RhythmDifficulty.LOW]

        tonality = melody_service.get_tonality(request.tonality)
        tonality_choice = melody_service.get_tonality_choice(request.tonality_choice)

        """构建提示词"""
        return f"""
        请生成一个{request.measures_count}小节的旋律，要求：
        1. 拍号：{request.time_signature}
        2. 速度：{request.tempo}
        3. 难度：{request.difficulty},包含音符为:{durations_desc}
        4. 调性：{tonality.display_value}
        5. 调式：{tonality_choice.display_value}
        
        旋律要求：
        1. 音程关系自然，避免大跳
        2. 节奏型合理，符合{request.time_signature}拍号特点
        3. 旋律线条流畅，有音乐性
        4. 适当使用重复音型和模进
        5. 结尾要有终止感
        
        请以JSON格式返回，包含每个音符的音高和时值。
        """

    async def _call_deepseek_api(self, prompt: str) -> Dict[str, Any]:
        """调用DeepSeek API"""
        headers = {
            "Authorization": f"Bearer {self.deepseek_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.4,
            "max_tokens": 2000,
            "stream": False,
        }
        
        response = requests.post(
            self.deepseek_api_url,
            headers=headers,
            json=data
        )
        
        if response.status_code != 200:
            raise Exception(f"DeepSeek API error: {response.text}")
            
        return response.json()

    def _parse_ai_response(self, response: Dict[str, Any], request: MelodyQuestionRequest) -> MelodyScorePitch:
        """解析AI响应并转换为MelodyScorePitch对象"""
        try:
            # 解析AI返回的JSON
            melody_data = json.loads(response["choices"][0]["message"]["content"])
            
            # 转换为MelodyScorePitch对象
            measures = []
            for measure_data in melody_data["measures"]:
                measure = []
                for note_data in measure_data["notes"]:
                    pitch = Pitch(
                        id=note_data["pitch"]["id"],
                        pitch_number=note_data["pitch"]["pitch_number"],
                        name=note_data["pitch"]["name"],
                        alias=note_data["pitch"]["alias"]
                    )
                    measure.append({
                        "duration": note_data["duration"],
                        "is_rest": note_data["is_rest"],
                        "is_dotted": note_data["is_dotted"],
                        "tied_to_next": note_data["tied_to_next"],
                        "pitch": pitch
                    })
                measures.append([measure])
            
            return MelodyScorePitch(
                measures=measures,
                time_signature=request.time_signature,
                tempo=request.tempo
            )
        except Exception as e:
            logger.error(f"Error parsing AI response: {str(e)}")
            raise


ai_melody_service = AIMelodyService()