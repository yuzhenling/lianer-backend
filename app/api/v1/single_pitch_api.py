# from fastapi import APIRouter, HTTPException, status, Request
# from fastapi.responses import FileResponse, JSONResponse
# from typing import Dict, List
# import traceback
# from pathlib import Path
#
# from app.core.logger import logger
# from app.models.pitch import (
#     PitchName, Interval, ChordType, Pitch, PitchGroup,
#     IntervalModel, ChordEnum, PITCH_GROUPS, INTERVALS, CHORDS
# )
# from app.core.i18n import i18n, get_language
#
# router = APIRouter()
#
# @router.get("/pitches/all")
# async def get_all_pitches(request: Request):
#     """获取所有单音音频文件信息"""
#     lang = get_language(request)
#     try:
#         result = []
#         for pitch_name, file_path in PITCH_FILE_MAPPING.items():
#             # 获取音频文件的基本信息
#             file = Path(file_path)
#             if file.exists():
#                 result.append({
#                     "name": pitch_name.value,
#                     "file_path": f"/static/audio/mp3/{file.name}",
#                     "size": file.stat().st_size
#                 })
#         return JSONResponse(content={"pitches": result})
#     except Exception as e:
#         logger.error(f"Error in get_all_pitches: {str(e)}\nTraceback: {traceback.format_exc()}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
#         )
#
# @router.get("/pitches/{pitch_name}")
# async def get_pitch_audio(pitch_name: str, request: Request):
#     """获取指定音高的音频文件"""
#     lang = get_language(request)
#     try:
#         # 将输入的音名转换为枚举（例如：'C#4' -> 'CS4'）
#         enum_name = pitch_name.replace("#", "S")
#         pitch_enum = PitchName[enum_name]
#
#         if pitch_enum not in PITCH_FILE_MAPPING:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail=i18n.get_text("PITCH_NOT_FOUND", lang)
#             )
#
#         file_path = PITCH_FILE_MAPPING[pitch_enum]
#         return FileResponse(
#             file_path,
#             media_type="audio/mpeg",
#             filename=f"{pitch_name}.mp3"
#         )
#     except KeyError:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=i18n.get_text("INVALID_PITCH_NAME", lang)
#         )
#     except Exception as e:
#         logger.error(f"Error in get_pitch_audio for {pitch_name}: {str(e)}\nTraceback: {traceback.format_exc()}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
#         )
#
# @router.get("/pitch-groups")
# async def get_pitch_groups(request: Request):
#     """获取所有预定义的音组列表"""
#     lang = get_language(request)
#     try:
#         return {"groups": PITCH_GROUPS}
#     except Exception as e:
#         logger.error(f"Error in get_pitch_groups: {str(e)}\nTraceback: {traceback.format_exc()}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
#         )
#
# @router.get("/intervals")
# async def get_intervals(request: Request):
#     """获取所有音程列表"""
#     lang = get_language(request)
#     try:
#         return {"intervals": INTERVALS}
#     except Exception as e:
#         logger.error(f"Error in get_intervals: {str(e)}\nTraceback: {traceback.format_exc()}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
#         )
#
# @router.get("/chords")
# async def get_chords(request: Request):
#     """获取所有和弦列表"""
#     lang = get_language(request)
#     try:
#         return {"chords": CHORDS}
#     except Exception as e:
#         logger.error(f"Error in get_chords: {str(e)}\nTraceback: {traceback.format_exc()}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
#         )
