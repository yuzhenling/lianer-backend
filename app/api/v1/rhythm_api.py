# app/api/v1/rhythm_api.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.auth_api import get_current_user, get_db
from app.models.user import User
from app.services.rhythm_service import rhythm_service
from app.models.rhythm import *

router = APIRouter(prefix="/rhythm", tags=["rhythm"])


@router.post("/generate", response_model=RhythmQuestionResponse)
async def generate_rhythm_question(
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


@router.get("/settings", response_model=dict)
async def get_rhythm_settings():
    """节奏听写设置选项"""
    return {
        "difficulties": [d.value for d in RhythmDifficulty],
        "measures_counts": [4, 6, 8, 10, 12, 16],
        "time_signatures": [ts.value for ts in TimeSignature],
        "tempo": [t.value for t in Tempo],
    }