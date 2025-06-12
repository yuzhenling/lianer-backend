import os
import traceback
from dataclasses import replace
from typing import Optional, List
from urllib.parse import unquote

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import FileResponse


from app.api.v1.auth_api import get_current_user, get_db, get_current_user_vip
from app.api.v1.order_api import order_service
from app.api.v1.schemas.request.pitch_request import PitchSettingRequest, PitchGroupSettingRequest, \
    PitchIntervalSettingRequest, PitchChordSettingRequest
from app.api.v1.schemas.response.pitch_response import PitchSingleSettingResponse, PitchResponse, \
    PitchChordResponse, PitchGroupResponse, SinglePitchExamResponse, PitchGroupSettingResponse, GroupPitchExamResponse, \
    PitchIntervalSettingResponse, PitchIntervalExamResponse, PitchChordSettingResponse, PitchChordExamResponse, \
    PitchIntervalWithPitchesResponse
from app.core.i18n import get_language, i18n
from app.core.logger import logger
from app.services.pitch_service import pitch_service
from app.models.user import User, CombineUser
from app.services.pitch_settings_service import pitch_settings_service
from app.utils.UserChecker import check_year_vip_level

router = APIRouter(prefix="/piano", tags=["piano"])



@router.get("/pitch/info", response_model=List[PitchResponse])
async def get_all_pitches(
        request: Request,
        current_user: User = Depends(get_current_user)
):
    """
    获取所有钢琴音高信息接口
    
    返回系统中所有可用的钢琴音高信息，包括音高名称、频率、MIDI音符号等。
    
    Args:
        request: FastAPI请求对象
        current_user: 当前登录用户对象
        
    Returns:
        List[PitchResponse]: 钢琴音高信息列表
            - name: 音高名称（如"C4", "D#4"等）
            - frequency: 频率（Hz）
            - midi_number: MIDI音符号
            - url: 音频文件URL
            
    Raises:
        HTTPException:
            - 500: 服务器内部错误
            

    """
    lang = get_language(request)
    try:
        """获取所有信息"""
        pitches = pitch_service.get_all_pitch()
        if not pitches:
            return []
        return [PitchResponse.model_validate(pitch) for pitch in pitches]
    except Exception as e:
        logger.error(f"Error in get_all_pitches: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
        )


@router.get("/pitch/info/{pitch_number}", response_model=PitchResponse)
async def get_pitch_by_id(
    pitch_number: int,
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """
    获取pitch_number对应的钢琴音高信息接口

    返回钢琴音高信息，包括音高id,音高号，音高名称、音高别名。

    Args:
        request: FastAPI请求对象
        current_user: 当前登录用户对象

    Returns:
        List[PitchResponse]: 钢琴音高信息列表
            - id: 音高id
            - pitch_number: 音高number 1-88
            - name: 音高名称（如"C4"等）
            - alias: 音高名称（如 "D#4"等）

    Raises:
        HTTPException:
            - 500: 服务器内部错误


    """
    lang = get_language(request)
    try:
        pitch = pitch_service.get_pitch_by_number(pitch_number)
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

@router.get("/pitch/name/{name}", response_model=PitchResponse)
async def search_pitch_by_name(
    request: Request,
    name: str,
    current_user: User = Depends(get_current_user),
):
    """
    根据音名或别名搜索钢琴音高信息

    返回钢琴音高信息，包括音高id,音高号，音高名称、音高别名。

    Args:
        request: FastAPI请求对象
        current_user: 当前登录用户对象

    Returns:
        List[PitchResponse]: 钢琴音高信息列表
            - id: 音高id
            - pitch_number: 音高number 1-88
            - name: 音高名称（如"C4"等）
            - alias: 音高名称（如 "D#4"等）

    Raises:
        HTTPException:
            - 500: 服务器内部错误


    """
    lang = get_language(request)
    try:
        name = unquote(name)
        pitches = pitch_service.get_pitch_by_name(name)
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



@router.get("/pitch/audio/index/{index}")
async def get_wav_by_index(
    request: Request,
    index: int,
):
    """
    通过MIDI音符号获取钢琴音高音频文件接口
    
    根据MIDI音符号返回对应的钢琴音高音频文件。
    
    Args:
        request: FastAPI请求对象
        index: pitch_num
        current_user: 当前登录用户对象
        
    Returns:
        FileResponse: 音频文件响应
            - Content-Type: audio/wav
            - Content-Disposition: inline
            
    Raises:
        HTTPException:
            - 404: 音高不存在或音频文件不存在
            - 500: 服务器内部错误
    """
    lang = get_language(request)
    try:

        pitch = pitch_service.get_pitch_by_number(index)
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


@router.get("/pitch/audio/name/{name}")
async def get_wav_by_name(
    request: Request,
    name: str,
):
    """
    通过音高名称获取钢琴音高音频文件接口
    
    根据音高名称（如"C4", "D#4"等）返回对应的钢琴音高音频文件。
    
    Args:
        request: FastAPI请求对象
        name: 音高名称（URL编码）
        current_user: 当前登录用户对象
        
    Returns:
        FileResponse: 音频文件响应
            - Content-Type: audio/wav
            - Content-Disposition: inline
            
    Raises:
        HTTPException:
            - 404: 音高不存在或音频文件不存在
            - 500: 服务器内部错误
    """
    lang = get_language(request)
    try:
        name = unquote(name)
        pitches = pitch_service.get_pitch_by_name(name)
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

@router.get("/pitchgroup", response_model=List[PitchGroupResponse])
async def get_all_pitchgroups(
    request: Request,
    include_black_key: bool = True,
    current_user: User = Depends(get_current_user),
):
    """
    获取所有音组信息接口

    返回系统中所有可用的音组信息。

    Args:
        request: FastAPI请求对象
        current_user: 当前登录用户对象

    Returns:
        List[PitchGroupResponse]: 音程信息列表

    Raises:
        HTTPException:
            - 404: 未找到音程信息
            - 500: 服务器内部错误


    """
    lang = get_language(request)
    try:
        pitch_groups = pitch_service.get_all_pitchgroups()
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

@router.get("/pitchinterval", response_model=List[PitchIntervalWithPitchesResponse])
async def get_all_pitchinterval(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """
    获取所有音程信息接口
    
    返回系统中所有可用的音程信息，包括音程类型、音程名称、起始音高等。
    
    Args:
        request: FastAPI请求对象
        current_user: 当前登录用户对象
        
    Returns:
        List[PitchIntervalWithPitchesResponse]: 音程信息列表

    Raises:
        HTTPException:
            - 404: 未找到音程信息
            - 500: 服务器内部错误
            

    """
    lang = get_language(request)
    try:
        pitch_intervals= pitch_service.get_all_intervals()
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

@router.get("/pitchchord", response_model=List[PitchChordResponse])
async def get_all_pitchchord(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """
    获取所有和弦信息接口
    
    返回系统中所有可用的和弦信息，包括和弦类型、和弦名称、组成音高等。
    
    Args:
        request: FastAPI请求对象
        current_user: 当前登录用户对象
        
    Returns:
        List[PitchChordResponse]: 和弦信息列表

    Raises:
        HTTPException:
            - 404: 未找到和弦信息
            - 500: 服务器内部错误
            
    """
    lang = get_language(request)
    try:
        pitch_chords= pitch_service.get_all_chords()
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


@router.get("/pitch/single/setting", response_model=PitchSingleSettingResponse)
async def get_pitch_single_setting(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
        获取单独音高测验设置接口

        Args:
            request: FastAPI请求对象
            current_user: 当前登录用户对象

        Returns:
            PitchSingleSettingResponse: 单独音高测验设置

        Raises:
            HTTPException:
                - 404: 未找到和弦信息
                - 500: 服务器内部错误

    """
    lang = get_language(request)
    try:
        """获取所有信息"""
        pitch_setting = pitch_settings_service.get_pitch_single_settings()
        if not pitch_setting:
            return None
        return pitch_setting
    except Exception as e:
        logger.error(f"Error in get_all_pitches: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
        )

@router.get("/pitch/group/setting", response_model=PitchGroupSettingResponse)
async def get_pitch_group_settings(
    request: Request
):
    """
        获取音高组测验设置接口

        Args:
            request: FastAPI请求对象
            current_user: 当前登录用户对象

        Returns:
            PitchGroupSettingResponse: 音高组测验设置

        Raises:
            HTTPException:
                - 404: 未找到和弦信息
                - 500: 服务器内部错误

    """
    lang = get_language(request)
    try:
        """获取所有信息"""
        pitch_setting = pitch_settings_service.get_pitch_group_settings()
        if not pitch_setting:
            return None
        return pitch_setting
    except Exception as e:
        logger.error(f"Error in get_all_pitches: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
        )

@router.post("/pitch/single", response_model=List[PitchResponse])
async def get_pitch_listen_single(
    request: Request,
    pitch_setting: PitchSettingRequest,#pitch_black_keys作废
    current_user: User = Depends(get_current_user)
):
    """
        获取区间音高测验接口

        Args:
            request: FastAPI请求对象
            pitch_setting：设置
            current_user: 当前登录用户对象

        Returns:
            PitchResponse: 区间音高列表

        Raises:
            HTTPException:
                - 404: 未找到和弦信息
                - 500: 服务器内部错误

    """
    lang = get_language(request)
    try:
        min_pitch_number = pitch_setting.pitch_range.pitch_number_min
        max_pitch_number = pitch_setting.pitch_range.pitch_number_max
        # pitch_black_keys = pitch_setting.pitch_black_keys
        # mode_key = pitch_setting.mode_key

        pitches = pitch_service.get_pitches_by_setting(min_pitch_number, max_pitch_number)
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

@router.post("/pitch/single/exam")
async def get_pitch_listen_single_exam(
    request: Request,
    pitch_setting: PitchSettingRequest,
    current_user: CombineUser = Depends(get_current_user_vip)
) -> SinglePitchExamResponse:
    """
    生成单音听写题目接口
    
    根据用户设置的参数生成单音听写题目，包括音高范围、是否包含黑键等参数。
    
    Args:
        request: FastAPI请求对象
        pitch_setting: 单音设置请求体
            - pitch_range: 音高范围
                - pitch_number_min: 最小MIDI音符号
                - pitch_number_max: 最大MIDI音符号
            - pitch_black_keys: 是否包含黑键
        current_user: 当前登录用户对象
        
    Returns:
        SinglePitchExamResponse: 包含生成的单音题目数据

    Raises:
        HTTPException:
            - 500: 服务器内部错误
            
    """
    lang = get_language(request)
    try:
        vv = check_year_vip_level(current_user)
        if not vv:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=i18n.get_text("USER_VIP_NOT_YEAR", lang)
            )
        exam = pitch_service.generate_single_exam(pitch_setting.pitch_range.pitch_number_min, pitch_setting.pitch_range.pitch_number_max, pitch_setting.pitch_black_keys)
        return exam
    except HTTPException as e:
        logger.error(f"Error in get_pitch_listen_single_exam: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise e
    except Exception as e:
        logger.error(f"Error in get_pitch_listen_single_exam: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
        )

@router.post("/pitch/group/exam")
async def get_pitch_listen_group_exam(
    request: Request,
    pitch_group_setting: PitchGroupSettingRequest,
    current_user: CombineUser = Depends(get_current_user_vip)
) -> GroupPitchExamResponse:
    """
    生成音组听写题目接口

    根据用户设置的参数生成音组听写题目，包括音高范围、是否包含黑键等参数。

    Args:
        request: FastAPI请求对象
        pitch_setting: 单音设置请求体
            - pitch_range: 音高范围
                - pitch_number_min: 最小MIDI音符号
                - pitch_number_max: 最大MIDI音符号
            - pitch_black_keys: 是否包含黑键
            - count: 数量
        current_user: 当前登录用户对象

    Returns:
        SinglePitchExamResponse: 包含生成的音组题目数据

    Raises:
        HTTPException:
            - 500: 服务器内部错误

    """
    lang = get_language(request)
    try:
        vv = check_year_vip_level(current_user)
        if not vv:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=i18n.get_text("USER_VIP_NOT_YEAR", lang)
            )
        exam = pitch_service.generate_group_exam(
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


@router.get("/pitch/interval/setting")
async def get_pitch_interval_settings(
    request: Request,
    current_user: User = Depends(get_current_user)
)-> PitchIntervalSettingResponse:
    """
        获取音程测验设置接口

        Args:
            request: FastAPI请求对象
            current_user: 当前登录用户对象

        Returns:
            PitchGroupSettingResponse: 音程测验设置

        Raises:
            HTTPException:
                - 404: 未找到和弦信息
                - 500: 服务器内部错误

    """
    lang = get_language(request)
    try:
        """获取所有信息"""
        pitch_setting = pitch_settings_service.get_pitch_interval_settings()
        if not pitch_setting:
            return None
        return pitch_setting
    except Exception as e:
        logger.error(f"Error in get_pitch_interval_settings: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
        )

@router.post("/pitch/interval/exam")
async def get_pitch_listen_interval_exam(
    request: Request,
    pitch_interval_setting: PitchIntervalSettingRequest,
    current_user: CombineUser = Depends(get_current_user_vip)
) -> PitchIntervalExamResponse:
    """
    生成音程听写题目接口

    根据用户设置的参数生成音程听写题目。

    Args:
        request: FastAPI请求对象
        pitch_interval_setting: 音程设置请求体
        current_user: 当前登录用户对象

    Returns:
        SinglePitchExamResponse: 包含生成的音程题目数据

    Raises:
        HTTPException:
            - 500: 服务器内部错误

    """
    lang = get_language(request)
    try:
        vv = check_year_vip_level(current_user)
        if not vv:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=i18n.get_text("USER_VIP_NOT_YEAR", lang)
            )
        exam = pitch_service.generate_interval_exam(pitch_interval_setting)
        return exam
    except Exception as e:
        logger.error(f"Error in get_pitch_listen_single_exam: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
        )

@router.get("/pitch/chord/setting")
async def get_pitch_chord_settings(
    request: Request,
    current_user: User = Depends(get_current_user)
)-> PitchChordSettingResponse:
    """
        获取和弦测验设置接口

        Args:
            request: FastAPI请求对象
            current_user: 当前登录用户对象

        Returns:
            PitchChordSettingResponse: 和弦测验设置

        Raises:
            HTTPException:
                - 404: 未找到和弦信息
                - 500: 服务器内部错误

    """
    lang = get_language(request)
    try:
        """获取所有信息"""
        chord_setting = pitch_settings_service.get_pitch_chord_settings()
        if not chord_setting:
            return None
        return chord_setting
    except Exception as e:
        logger.error(f"Error in get_pitch_chord_settings: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
        )

@router.post("/pitch/chord/exam")
async def get_pitch_listen_chord_exam(
    request: Request,
    pitch_chord_setting: PitchChordSettingRequest,
    current_user: CombineUser = Depends(get_current_user_vip)
) -> PitchChordExamResponse:
    """
    生成和弦听写题目接口

    根据用户设置的参数生成和弦听写题目。

    Args:
        request: FastAPI请求对象
        pitch_chord_setting: 和弦设置请求体
        current_user: 当前登录用户对象

    Returns:
        PitchChordExamResponse: 包含生成的和弦题目数据

    Raises:
        HTTPException:
            - 500: 服务器内部错误

    """
    lang = get_language(request)
    try:
        vv = check_year_vip_level(current_user)
        if not vv:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=i18n.get_text("USER_VIP_NOT_YEAR", lang)
            )
        exam = pitch_service.generate_chord_exam(pitch_chord_setting)
        return exam
    except Exception as e:
        logger.error(f"Error in get_pitch_listen_chord_exam: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
        )