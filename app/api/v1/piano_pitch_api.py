import os
import traceback
from dataclasses import replace
from typing import Optional, List
from urllib.parse import unquote

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import FileResponse


from app.api.v1.auth_api import get_current_user, get_db
from app.api.v1.schemas.request.pitch_request import PitchSettingRequest, PitchGroupSettingRequest, \
    PitchIntervalSettingRequest
from app.api.v1.schemas.response.pitch_response import PitchSingleSettingResponse, PitchResponse, PitchIntervalResponse, \
    PitchChordResponse, PitchGroupResponse, SinglePitchExamResponse, PitchGroupSettingResponse, GroupPitchExamResponse, \
    PitchIntervalSettingResponse, PitchIntervalExamResponse, PitchChordSettingResponse
from app.core.i18n import get_language, i18n
from app.core.logger import logger
from app.services.pitch_service import pitch_service
from app.models.user import User
from app.services.pitch_settings_service import pitch_settings_service

router = APIRouter()



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
    include_black_key: bool = True,
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
        if not include_black_key:
            pitch_groups = [
                replace(pg, pitches=[p for p in pg.pitch_pairs if not p.isBlackKey()], count=len([p for p in pg.pitch_pairs if not p.isBlackKey()]))
                for pg in pitch_groups
            ]

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


@router.get("/piano/pitch/single/setting", response_model=PitchSingleSettingResponse)
async def get_pitch_single_setting(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    lang = get_language(request)
    try:
        """获取所有信息"""
        pitch_setting = await pitch_settings_service.get_pitch_single_settings()
        if not pitch_setting:
            return None
        return pitch_setting
    except Exception as e:
        logger.error(f"Error in get_all_pitches: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
        )

@router.get("/piano/pitch/group/setting", response_model=PitchGroupSettingResponse)
async def get_pitch_group_settings(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    lang = get_language(request)
    try:
        """获取所有信息"""
        pitch_setting = await pitch_settings_service.get_pitch_group_settings()
        if not pitch_setting:
            return None
        return pitch_setting
    except Exception as e:
        logger.error(f"Error in get_all_pitches: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
        )

@router.post("/piano/pitch/single", response_model=List[PitchResponse])
async def get_pitch_listen_single(
    request: Request,
    pitch_setting: PitchSettingRequest,
    current_user: User = Depends(get_current_user)
):
    lang = get_language(request)
    try:
        min_pitch_number = pitch_setting.pitch_range.pitch_number_min
        max_pitch_number = pitch_setting.pitch_range.pitch_number_max
        # pitch_black_keys = pitch_setting.pitch_black_keys
        # mode_key = pitch_setting.mode_key

        pitches = await pitch_service.get_pitches_by_setting(min_pitch_number, max_pitch_number)
        if not pitches:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=i18n.get_text("PITCH_NOT_FOUND", lang)
            )
        return pitches
    except Exception as e:
        logger.error(f"Error in get_all_pitches: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
        )

@router.post("/piano/pitch/single/exam")
async def get_pitch_listen_single_exam(
    request: Request,
    pitch_setting: PitchSettingRequest,
    current_user: User = Depends(get_current_user)
) -> SinglePitchExamResponse:
    lang = get_language(request)
    try:
        exam = await pitch_service.generate_single_exam(pitch_setting.pitch_range.pitch_number_min, pitch_setting.pitch_range.pitch_number_max, pitch_setting.pitch_black_keys)
        return exam
    except Exception as e:
        logger.error(f"Error in get_pitch_listen_single_exam: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
        )

@router.post("/piano/pitch/group/exam")
async def get_pitch_listen_group_exam(
    request: Request,
    pitch_group_setting: PitchGroupSettingRequest,
    current_user: User = Depends(get_current_user)
) -> GroupPitchExamResponse:
    lang = get_language(request)
    try:
        exam = await pitch_service.generate_group_exam(
            pitch_group_setting.pitch_range.pitch_number_min,
            pitch_group_setting.pitch_range.pitch_number_max,
            pitch_group_setting.pitch_black_keys,
            pitch_group_setting.count
        )
        return exam
    except Exception as e:
        logger.error(f"Error in get_pitch_listen_single_exam: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
        )


@router.get("/piano/pitch/interval/setting")
async def get_pitch_interval_settings(
    request: Request,
    current_user: User = Depends(get_current_user)
)-> PitchIntervalSettingResponse:
    lang = get_language(request)
    try:
        """获取所有信息"""
        pitch_setting = await pitch_settings_service.get_pitch_interval_settings()
        if not pitch_setting:
            return None
        return pitch_setting
    except Exception as e:
        logger.error(f"Error in get_pitch_interval_settings: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
        )

@router.post("/piano/pitch/interval/exam")
async def get_pitch_listen_interval_exam(
    request: Request,
    pitch_interval_setting: PitchIntervalSettingRequest,
    current_user: User = Depends(get_current_user)
) -> PitchIntervalExamResponse:
    lang = get_language(request)
    try:
        exam = await pitch_service.generate_interval_exam(pitch_interval_setting)
        return exam
    except Exception as e:
        logger.error(f"Error in get_pitch_listen_single_exam: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
        )

@router.get("/piano/pitch/chord/setting")
async def get_pitch_chord_settings(
    request: Request,
    current_user: User = Depends(get_current_user)
)-> PitchChordSettingResponse:
    lang = get_language(request)
    try:
        """获取所有信息"""
        chord_setting = await pitch_settings_service.get_pitch_chord_settings()
        if not chord_setting:
            return None
        return chord_setting
    except Exception as e:
        logger.error(f"Error in get_pitch_chord_settings: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
        )