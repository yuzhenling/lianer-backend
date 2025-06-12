# app/api/v1/rhythm_api.py
import traceback

from fastapi import APIRouter, Depends, HTTPException,Request
from sqlalchemy.orm import Session
from starlette import status

from app.api.v1.auth_api import get_current_user, get_db, get_current_user_vip
from app.api.v1.schemas.request.pitch_request import MelodySettingRequest
from app.api.v1.schemas.response.pitch_response import MelodySettingResponse, MelodyQuestionResponse
from app.core.i18n import i18n, get_language
from app.models.melody_settings import Tonality, TonalityChoice
from app.models.user import User, CombineUser
from app.services.ai_melody_service import ai_melody_service
from app.services.melody_service import melody_service
from app.models.rhythm import *
from app.core.logger import logger
from app.utils.UserChecker import check_normal_vip_level

router = APIRouter(prefix="/melody", tags=["melody"])


@router.post("/generate", response_model=MelodyQuestionResponse)
async def generate_melody_question(
        request: Request,
        melody_question_request: MelodySettingRequest,
        current_user: CombineUser = Depends(get_current_user_vip),
):
    """
    生成旋律听写题目接口
    
    根据用户设置的参数生成旋律听写题目，包括难度、拍号、小节数、速度等参数。
    
    Args:
        request: FastAPI请求对象
        melody_question_request: 旋律设置请求体
            - difficulty: 难度级别
            - time_signature: 拍号
            - measures_count: 小节数
            - tempo: 速度
            - tonality: 调性
            - tonality_choice: 调性选择（大调/小调）
        current_user: 当前登录用户对象
        
    Returns:
        MelodyQuestionResponse: 包含生成的旋律题目数据
            - melody: 旋律数据
            - audio_url: 音频文件URL
            
    Raises:
        HTTPException:
            - 500: 服务器内部错误
            
    """
    lang = get_language(request)
    try:
        vv = check_normal_vip_level(current_user)
        if not vv:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=i18n.get_text("USER_VIP_NOT_NORMAL", lang)
            )
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
    melody_question_request: MelodySettingRequest,
    current_user: CombineUser = Depends(get_current_user_vip),
):
    """
    使用AI生成旋律听写题目接口
    
    使用AI模型根据用户设置的参数生成旋律听写题目，可以生成更自然和富有创意的旋律。
    
    Args:
        request: FastAPI请求对象
        melody_question_request: 旋律设置请求体
            - difficulty: 难度级别
            - time_signature: 拍号
            - measures_count: 小节数
            - tempo: 速度
            - tonality: 调性
            - tonality_choice: 调性选择（大调/小调）
        current_user: 当前登录用户对象
        
    Returns:
        MelodyQuestionResponse: 包含AI生成的旋律题目数据
            - melody: 旋律数据
            - audio_url: 音频文件URL
            
    Raises:
        HTTPException:
            - 500: 服务器内部错误
            
    """
    lang = get_language(request)
    try:
        vv = check_normal_vip_level(current_user)
        if not vv:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=i18n.get_text("USER_VIP_NOT_NORMAL", lang)
            )
        return await ai_melody_service.generate_melody_question(melody_question_request)
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