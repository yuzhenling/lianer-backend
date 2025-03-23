import os
import traceback
from typing import Optional, List
from urllib.parse import unquote

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field


from app.api.v1.auth_api import get_current_user, get_db
from app.core.i18n import get_language, i18n
from app.core.logger import logger
from app.services.pitch_service import pitch_service
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.pitch import Pitch, Interval, PitchIntervalPair

router = APIRouter()

class PitchResponse(BaseModel):
    id: int
    pitch_number: int
    name: str
    alias: Optional[str] = None
    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "pitch_number": 40,
                "name": "C4",
                "alias": None,
                "url": ""
            }
        }
    }


class PitchGroupResponse(BaseModel):
    index: int
    name: str
    pitches: List[PitchResponse]
    count: int
    model_config = {
        "from_attributes": True,
    }

class PitchIntervalPairResponse(BaseModel):
    first: PitchResponse
    second: PitchResponse
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "first": {
                    "id": 40,
                    "pitch_number": 40,
                    "name": "C4",
                    "alias": None,
                    "url": ""
                },
                "second": {
                    "id": 44,
                    "pitch_number": 44,
                    "name": "E4",
                    "alias": None,
                    "url": ""
                }
            }
        }
    }


class PitchIntervalResponse(BaseModel):
    index: int
    interval: Interval
    semitones: int
    list: List[PitchIntervalPairResponse]
    count: int
    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "example": {
                "index": 4,
                "interval": "major_third",
                "semitones": 4,
                "list": [
                    {
                        "first": {
                            "id": 40,
                            "pitch_number": 40,
                            "name": "C4",
                            "alias": None,
                            "url": ""
                        },
                        "second": {
                            "id": 44,
                            "pitch_number": 44,
                            "name": "E4",
                            "alias": None,
                            "url": ""
                        }
                    }
                ],
                "count": 1
            }
        }
    }


class PitchChordResponse(BaseModel):
    index: int
    value: str
    cn_value: str
    list: List[List[PitchResponse]]
    count: int
    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {

        }
    }

@router.get("/piano/pitch/info", response_model=List[PitchResponse])
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


@router.get("/piano/pitch/info/{pitch_number}", response_model=PitchResponse)
async def get_pitch_by_id(
    pitch_number: int,
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """根据ID获取钢琴音高信息"""
    lang = get_language(request)
    try:
        pitch = await pitch_service.get_pitch_by_number(pitch_number)
        if not pitch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=i18n.get_text("PITCH_NOT_FOUND", lang)
            )
        return pitch
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_pitch_by_id for id {pitch_number}: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
        )

@router.get("/piano/pitch/name/{name}", response_model=PitchResponse)
async def search_pitch_by_name(
    request: Request,
    name: str,
    current_user: User = Depends(get_current_user),
):
    """根据音名或别名搜索钢琴音高信息"""
    lang = get_language(request)
    try:
        name = unquote(name)
        pitches = await pitch_service.get_pitch_by_name(name)
        if not pitches and len(pitches) != 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=i18n.get_text("PITCH_NOT_FOUND", lang)
            )
        return pitches[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in search_pitch_by_name with name={name}: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
        )



@router.get("/piano/pitch/audio/index/{index}")
async def get_wav_by_index(
    request: Request,
    index: int,
    current_user: User = Depends(get_current_user),
):
    lang = get_language(request)
    try:

        pitch = await pitch_service.get_pitch_by_number(index)
        if not pitch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=i18n.get_text("PITCH_NOT_FOUND", lang)
            )

        if not os.path.exists(pitch.url):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=i18n.get_text("FILE_NOT_FOUND", lang)
            )

        return FileResponse(
            pitch.url,
            media_type="audio/wav",
            headers={"Content-Disposition": f"inline; filename={os.path.basename(pitch.name)}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error in search_pitch_by_name with index={index}: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
        )


@router.get("/piano/pitch/audio/name/{name}")
async def get_wav_by_name(
    request: Request,
    name: str,
    current_user: User = Depends(get_current_user),
):
    lang = get_language(request)
    try:
        name = unquote(name)
        pitches = await pitch_service.get_pitch_by_name(name)
        if not pitches and len(pitches) != 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=i18n.get_text("PITCH_NOT_FOUND", lang)
            )
        pitch = pitches[0]

        if not os.path.exists(pitch.url):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=i18n.get_text("FILE_NOT_FOUND", lang)
            )

        return FileResponse(
            pitch.url,
            media_type="audio/wav",
            headers={"Content-Disposition": f"inline; filename={os.path.basename(pitch.name)}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error in search_pitch_by_name with name={name}: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
        )

@router.get("/piano/pitchgroup", response_model=List[PitchGroupResponse])
async def get_all_pitchgroups(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    lang = get_language(request)
    try:
        pitch_groups = await pitch_service.get_all_pitchgroups()
        if not pitch_groups:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=i18n.get_text("PITCH_GROUP_NOT_FOUND", lang)
            )
        return pitch_groups
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error in get_all_pitchgroups: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
        )

@router.get("/piano/pitchinterval", response_model=List[PitchIntervalResponse])
async def get_all_pitchinterval(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    lang = get_language(request)
    try:
        pitch_intervals= await pitch_service.get_all_intervals()
        if not pitch_intervals:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=i18n.get_text("PITCH_INTERVAL_NOT_FOUND", lang)
            )
        return pitch_intervals
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error in get_all_pitchinterval: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
        )

@router.get("/piano/pitchchord", response_model=List[PitchChordResponse])
async def get_all_pitchchord(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    lang = get_language(request)
    try:
        pitch_chords= await pitch_service.get_all_chords()
        if not pitch_chords:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=i18n.get_text("PITCH_CHORD_NOT_FOUND", lang)
            )
        return pitch_chords
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error in get_all_pitchchord: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
        )