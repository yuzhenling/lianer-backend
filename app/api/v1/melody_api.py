# app/api/v1/rhythm_api.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.auth_api import get_current_user, get_db
from app.api.v1.schemas.request.pitch_request import RhythmQuestionRequest
from app.api.v1.schemas.response.pitch_response import RhythmQuestionResponse, RhythmSettingResponse
from app.models.user import User
from app.services.rhythm_service import rhythm_service
from app.models.rhythm import *

router = APIRouter(prefix="/melody", tags=["melody"])


@router.post("/generate", response_model=RhythmQuestionResponse)
async def generate_melody_question(
        request: RhythmQuestionRequest,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """生成节奏听写题"""
    try:
        response = rhythm_service.generate_question(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/settings", response_model=RhythmSettingResponse)
async def get_melody_settings():
    """节奏听写设置选项"""
    settings = RhythmSettingResponse(
        difficulties=[d.value for d in RhythmDifficulty],
        measures_counts= [4, 6, 8, 10, 12, 16],
         time_signatures= [ts.value for ts in TimeSignature],
         tempo = [t.value for t in Tempo],
    )
    return settings