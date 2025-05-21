# app/api/v1/rhythm_api.py
import traceback

from fastapi import APIRouter, Depends, HTTPException,Request
from starlette import status

from app.api.v1.auth_api import get_current_user
from app.api.v1.schemas.request.exam_request import ExamRequest
from app.api.v1.schemas.response.exam_response import ExamSettingResponse, ExamResponse
from app.api.v1.schemas.response.pitch_response import MelodySettingResponse, MelodyQuestionResponse, \
    RhythmSettingResponse
from app.core.i18n import i18n, get_language
from app.models.exam_all import ExamSetting, ExamData
from app.models.melody_settings import Tonality, TonalityChoice
from app.models.user import User
from app.models.rhythm import *
from app.core.logger import logger
from app.services.melody_service import melody_service
from app.services.pitch_service import pitch_service
from app.services.pitch_settings_service import pitch_settings_service
from app.services.rhythm_service import rhythm_service

router = APIRouter(prefix="/exam", tags=["exam"])


@router.post("", response_model=ExamResponse)
async def generate_exam(
        request: Request,
        exam_request: ExamRequest,
        current_user: User = Depends(get_current_user),
):
    """生成节奏听写题"""
    lang = get_language(request)
    try:
        single = pitch_service.generate_single_exam(exam_request.pitch_setting.pitch_range.pitch_number_min,
                                                        exam_request.pitch_setting.pitch_range.pitch_number_max,
                                                        exam_request.pitch_setting.pitch_black_keys,
                                                        5)
        group = pitch_service.generate_group_exam(
            exam_request.pitch_group_setting.pitch_range.pitch_number_min,
            exam_request.pitch_group_setting.pitch_range.pitch_number_max,
            exam_request.pitch_group_setting.pitch_black_keys,
            exam_request.pitch_group_setting.count,
            5
        )

        interval = pitch_service.generate_interval_exam(exam_request.pitch_interval_setting, 5)

        chord = pitch_service.generate_chord_exam(exam_request.pitch_chord_setting, 5)

        rhythm = rhythm_service.generate_rhythm(
            exam_request.rhythm_setting.difficulty,
            exam_request.rhythm_setting.time_signature,
            exam_request.rhythm_setting.measures_count.value,
            exam_request.rhythm_setting.tempo.value
        )

        melody = melody_service.generate_melody(
            exam_request.melody_setting.difficulty,
            exam_request.melody_setting.time_signature,
            exam_request.melody_setting.measures_count.value,
            exam_request.melody_setting.tempo.value,
            exam_request.melody_setting.tonality,
            exam_request.melody_setting.tonality_choice,
        )

        exam = ExamData(
            single=single,
            group=group,
            interval=interval,
            chord=chord,
            rhythm=rhythm,
            melody=melody,
        )

        return exam
    except Exception as e:
        logger.error(
            f"Error in generate_exam : {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
        )



@router.get("/settings", response_model=ExamSettingResponse)
async def get_exam_settings(
        request: Request,
        current_user: User = Depends(get_current_user)
):
    lang = get_language(request)
    try:
        """获取所有信息"""
        single_setting = pitch_settings_service.get_pitch_single_settings()

        group_setting = pitch_settings_service.get_pitch_group_settings()

        interval_setting = pitch_settings_service.get_pitch_interval_settings()

        chord_setting = pitch_settings_service.get_pitch_chord_settings()

        """节奏听写设置选项"""
        rhythm_settings = RhythmSettingResponse(
            difficulties=[d.value for d in RhythmDifficulty],
            measures_counts=[4, 6, 8, 10, 12, 16],
            time_signatures=[ts.value for ts in TimeSignature],
            tempo=[t.value for t in Tempo],
        )

        """节奏+旋律听写设置选项"""
        melody_setting = MelodySettingResponse(
            difficulties=[d.value for d in RhythmDifficulty],
            measures_counts=[4, 6, 8, 10, 12, 16],
            time_signatures=[ts.value for ts in TimeSignature],
            tempo=[t.value for t in Tempo],
            tonality=[t.to_dict() for t in Tonality],
            tonality_choice=[t.to_dict() for t in TonalityChoice]
        )

        exam_setting = ExamSetting(
            pitch_single_setting=single_setting,
            pitch_group_setting=group_setting,
            pitch_interval_setting=interval_setting,
            pitch_chord_setting=chord_setting,
            rhythm_setting=rhythm_settings,
            melody_setting=melody_setting,
        )
        return exam_setting
    except Exception as e:
        logger.error(f"Error in get_all_pitches: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
        )
    return settings