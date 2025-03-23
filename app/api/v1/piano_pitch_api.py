import traceback
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field
from app.api.v1.auth_api import get_current_user, get_db
from app.core.i18n import get_language, i18n
from app.core.logger import logger
from app.services.pitch_service import pitch_service
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.pitch import Pitch

router = APIRouter()

class PitchResponse(BaseModel):
    id: int
    pitch_number: int
    name: str
    alias: Optional[str] = None
    file_path: str
    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True
    }

@router.get("/piano/pitch", response_model=List[PitchResponse])
async def get_all_pitches(
        request: Request,
        current_user: User = Depends(get_current_user)
):
    lang = get_language(request)
    try:
        """获取所有信息"""
        pitches = await pitch_service.get_all_pitch()
        if not pitches:
            return []
        return [PitchResponse.model_validate(pitch) for pitch in pitches]
    except Exception as e:
        logger.error(f"Error in get_all_pitches: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
        )

@router.get("/piano/pitch/{pitch_id}")
async def get_pitch_by_id(
    pitch_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """根据ID获取钢琴音高信息"""
    lang = get_language(request)
    try:
        pitch = db.query(Pitch).filter(Pitch.id == pitch_id).first()
        
        if not pitch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=i18n.get_text("PITCH_NOT_FOUND", lang)
            )
        
        return {
            "id": pitch.id,
            "pitch_number": pitch.pitch_number,
            "name": pitch.name,
            "alias": pitch.alias,
            "file_path": pitch.file_path
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_pitch_by_id for id {pitch_id}: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
        )

@router.get("/piano/pitch/search")
async def search_pitch_by_name(
    request: Request,
    name: Optional[str] = None,
    alias: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """根据音名或别名搜索钢琴音高信息"""
    lang = get_language(request)
    try:
        if not name and not alias:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=i18n.get_text("SEARCH_PARAM_REQUIRED", lang)
            )
        
        query = db.query(Pitch)
        
        # 构建查询条件
        if name:
            query = query.filter(Pitch.name.ilike(f"%{name}%"))
        if alias:
            query = query.filter(Pitch.alias.ilike(f"%{alias}%"))
        
        pitches = query.all()
        
        if not pitches:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=i18n.get_text("PITCH_NOT_FOUND", lang)
            )
        
        return {
            "total": len(pitches),
            "pitches": [
                {
                    "id": pitch.id,
                    "pitch_number": pitch.pitch_number,
                    "name": pitch.name,
                    "alias": pitch.alias,
                    "file_path": pitch.file_path
                }
                for pitch in pitches
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in search_pitch_by_name with name={name}, alias={alias}: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
        )

