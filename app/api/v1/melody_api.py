# app/api/v1/rhythm_api.py
import traceback

from fastapi import APIRouter, Depends, HTTPException,Request
from sqlalchemy.orm import Session
from starlette import status

from app.api.v1.auth_api import get_current_user, get_db
from app.api.v1.schemas.request.pitch_request import MelodyQuestionRequest
from app.api.v1.schemas.response.pitch_response import MelodySettingResponse, MelodyQuestionResponse
from app.core.i18n import i18n, get_language
from app.models.melody_settings import Tonality, TonalityChoice
from app.models.user import User
from app.services.ai_melody_service import ai_melody_service
from app.services.melody_service import melody_service
from app.models.rhythm import *
from app.core.logger import logger
router = APIRouter(prefix="/melody", tags=["melody"])


@router.post("/generate", response_model=MelodyQuestionResponse)
async def generate_melody_question(
        request: Request,
        melody_question_request: MelodyQuestionRequest,
        current_user: User = Depends(get_current_user),
):
    """生成节奏听写题"""
    lang = get_language(request)
    try:
        response = melody_service.generate_question(melody_question_request)
        return response
    except Exception as e:
        logger.error(
            f"Error in generate_melody_question : {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
        )


@router.post("/generate/ai", response_model=MelodyQuestionResponse)
async def generate_ai_melody_question(
    request: Request,
    melody_question_request: MelodyQuestionRequest,
    current_user: User = Depends(get_current_user)
):
    lang = get_language(request)
    try:
        return await ai_melody_service.generate_melody_question(melody_question_request)
        return response
    except Exception as e:
        logger.error(
            f"Error in generate_ai_melody_question : {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
        )


@router.get("/settings", response_model=MelodySettingResponse)
async def get_melody_settings():
    """节奏听写设置选项"""
    settings = MelodySettingResponse(
        difficulties=[d.value for d in RhythmDifficulty],
        measures_counts= [4, 6, 8, 10, 12, 16],
        time_signatures= [ts.value for ts in TimeSignature],
        tempo = [t.value for t in Tempo],
        tonality=[t.to_dict() for t in Tonality],
        tonality_choice=[t.to_dict() for t in TonalityChoice]
    )
    return settings