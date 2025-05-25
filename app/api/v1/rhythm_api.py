# app/api/v1/rhythm_api.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.auth_api import get_current_user, get_db
from app.api.v1.schemas.request.pitch_request import RhythmSettingRequest
from app.api.v1.schemas.response.pitch_response import RhythmQuestionResponse, RhythmSettingResponse
from app.models.user import User
from app.services.rhythm_service import rhythm_service
from app.models.rhythm import *

router = APIRouter(prefix="/rhythm", tags=["rhythm"])


@router.post("/generate", response_model=RhythmQuestionResponse)
async def generate_rhythm_question(
        request: RhythmSettingRequest,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    生成节奏听写题目接口
    
    根据用户设置的参数生成节奏听写题目，包括难度、拍号、小节数、速度等参数。
    
    Args:
        request: 节奏设置请求体
            - difficulty: 难度级别（easy/medium/hard）
            - time_signature: 拍号（如"4/4", "3/4"等）
            - measures_count: 小节数
            - tempo: 速度（BPM）
        current_user: 当前登录用户对象
        db: 数据库会话依赖
        
    Returns:
        RhythmQuestionResponse: 包含生成的节奏题目数据
            - rhythm: 节奏数据
            - audio_url: 音频文件URL
            
    Raises:
        HTTPException:
            - 400: 请求参数错误
            - 500: 服务器内部错误
            
    Example:
        ```json
        {
            "difficulty": "medium",
            "time_signature": "4/4",
            "measures_count": 4,
            "tempo": 120
        }
        ```
    """
    try:
        response = rhythm_service.generate_question(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/settings", response_model=RhythmSettingResponse)
async def get_rhythm_settings():
    """
    获取节奏听写设置选项接口
    
    返回节奏听写可用的设置选项，包括难度、拍号、小节数、速度等参数。
    
    Args:
        无
        
    Returns:
        RhythmSettingResponse: 节奏听写设置选项
            - difficulties: 可选的难度级别列表
            - measures_counts: 可选的小节数列表
            - time_signatures: 可选的拍号列表
            - tempo: 可选的速度列表
            
    Example Response:
        ```json
        {
            "difficulties": ["easy", "medium", "hard"],
            "measures_counts": [4, 6, 8, 10, 12, 16],
            "time_signatures": ["4/4", "3/4", "2/4"],
            "tempo": [60, 80, 100, 120]
        }
        ```
    """
    settings = RhythmSettingResponse(
        difficulties=[d.value for d in RhythmDifficulty],
        measures_counts= [4, 6, 8, 10, 12, 16],
        time_signatures= [ts.value for ts in TimeSignature],
        tempo = [t.value for t in Tempo],
    )
    return settings