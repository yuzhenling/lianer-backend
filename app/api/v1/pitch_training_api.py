# from fastapi import APIRouter, HTTPException, status, Request, Depends
# from fastapi.responses import JSONResponse
# from sqlalchemy.orm import Session
# import random
# import logging
# import traceback
# from typing import List, Optional
# from datetime import datetime
#
# from app.api.v1.auth_api import get_current_user, get_db
# from app.models.pitch import (
#     PitchName, Interval, ChordType, PitchTest, PracticeSession, PitchType,
#     PITCH_GROUPS, INTERVALS, CHORDS
# )
# from app.models.user import User
# from app.core.i18n import i18n, get_language
#
# router = APIRouter()
# logger = logging.getLogger(__name__)
#
# # 辅助函数：生成随机音高
# def get_random_pitch(octave_range: List[int] = [4]) -> PitchName:
#     """生成指定八度范围内的随机音高"""
#     available_pitches = [p for p in PitchName if any(str(o) in p.value for o in octave_range)]
#     return random.choice(available_pitches)
#
# # 辅助函数：生成随机音程
# def get_random_interval() -> dict:
#     """生成随机音程及其组成音"""
#     interval = random.choice(INTERVALS)
#     base_pitch = get_random_pitch([4])  # 从第4个八度选择基础音
#     return {
#         "interval": interval,
#         "pitches": interval.example  # 使用预定义的示例音程
#     }
#
# # 辅助函数：生成随机和弦
# def get_random_chord() -> dict:
#     """生成随机和弦及其组成音"""
#     chord = random.choice(CHORDS)
#     return {
#         "chord": chord,
#         "root": chord.root,
#         "type": chord.type,
#         "notes": chord.notes
#     }
#
# @router.post("/training/pitch/start")
# async def start_pitch_training(
#     request: Request,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """开始音高识别训练"""
#     lang = get_language(request)
#     try:
#         # 创建新的练习会话
#         session = PracticeSession(
#             user_id=current_user.id,
#             type=PitchType.SINGLE_NOTE,
#             duration=0,
#             notes_practiced=0,
#             average_accuracy=0.0
#         )
#         db.add(session)
#         db.commit()
#
#         # 生成随机音高
#         pitch = get_random_pitch([4])  # 默认使用第4个八度
#
#         return {
#             "session_id": session.id,
#             "pitch": pitch.value,
#             "message": i18n.get_text("TRAINING_STARTED", lang)
#         }
#     except Exception as e:
#         logger.error(f"Error in start_pitch_training: {str(e)}\nTraceback: {traceback.format_exc()}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
#         )
#
# @router.post("/training/interval/start")
# async def start_interval_training(
#     request: Request,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """开始音程训练"""
#     lang = get_language(request)
#     try:
#         # 创建新的练习会话
#         session = PracticeSession(
#             user_id=current_user.id,
#             type=PitchType.INTERVAL,
#             duration=0,
#             notes_practiced=0,
#             average_accuracy=0.0
#         )
#         db.add(session)
#         db.commit()
#
#         # 生成随机音程
#         interval_data = get_random_interval()
#
#         return {
#             "session_id": session.id,
#             "interval": {
#                 "name": interval_data["interval"].name.value,
#                 "description": interval_data["interval"].description,
#                 "pitches": [p.value for p in interval_data["pitches"]]
#             },
#             "message": i18n.get_text("TRAINING_STARTED", lang)
#         }
#     except Exception as e:
#         logger.error(f"Error in start_interval_training: {str(e)}\nTraceback: {traceback.format_exc()}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
#         )
#
# @router.post("/training/chord/start")
# async def start_chord_training(
#     request: Request,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """开始和弦训练"""
#     lang = get_language(request)
#     try:
#         # 创建新的练习会话
#         session = PracticeSession(
#             user_id=current_user.id,
#             type=PitchType.CHORD,
#             duration=0,
#             notes_practiced=0,
#             average_accuracy=0.0
#         )
#         db.add(session)
#         db.commit()
#
#         # 生成随机和弦
#         chord_data = get_random_chord()
#
#         return {
#             "session_id": session.id,
#             "chord": {
#                 "root": chord_data["root"].value,
#                 "type": chord_data["type"].value,
#                 "description": chord_data["chord"].description,
#                 "notes": [note.value for note in chord_data["notes"]]
#             },
#             "message": i18n.get_text("TRAINING_STARTED", lang)
#         }
#     except Exception as e:
#         logger.error(f"Error in start_chord_training: {str(e)}\nTraceback: {traceback.format_exc()}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
#         )
#
# @router.post("/training/scale/start")
# async def start_scale_training(
#     request: Request,
#     scale_type: str = "major",  # major 或 minor
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """开始音阶练习"""
#     lang = get_language(request)
#     try:
#         # 创建新的练习会话
#         session = PracticeSession(
#             user_id=current_user.id,
#             type=PitchType.MELODY,
#             duration=0,
#             notes_practiced=0,
#             average_accuracy=0.0
#         )
#         db.add(session)
#         db.commit()
#
#         # 选择一个随机的起始音（根音）
#         root = get_random_pitch([4])
#
#         # 根据音阶类型生成音阶
#         scale_notes = []
#         root_index = list(PitchName).index(root)
#
#         if scale_type == "major":
#             # 大调音阶的半音间隔：2-2-1-2-2-2-1
#             intervals = [2, 2, 1, 2, 2, 2, 1]
#             description = f"{root.value}大调音阶"
#         else:  # minor
#             # 自然小调音阶的半音间隔：2-1-2-2-1-2-2
#             intervals = [2, 1, 2, 2, 1, 2, 2]
#             description = f"{root.value}自然小调音阶"
#
#         current_index = root_index
#         scale_notes.append(list(PitchName)[current_index])
#
#         for interval in intervals[:-1]:  # 不包括最后一个音程，因为已经到达八度
#             current_index += interval
#             if current_index < len(PitchName):
#                 scale_notes.append(list(PitchName)[current_index])
#
#         return {
#             "session_id": session.id,
#             "scale": {
#                 "root": root.value,
#                 "type": scale_type,
#                 "description": description,
#                 "notes": [note.value for note in scale_notes]
#             },
#             "message": i18n.get_text("TRAINING_STARTED", lang)
#         }
#     except Exception as e:
#         logger.error(f"Error in start_scale_training: {str(e)}\nTraceback: {traceback.format_exc()}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
#         )
#
# @router.post("/training/{session_id}/submit")
# async def submit_training_result(
#     request: Request,
#     session_id: int,
#     user_recording: str,
#     pitch_accuracy: float,
#     timing_accuracy: Optional[float] = None,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """提交训练结果"""
#     lang = get_language(request)
#     try:
#         # 获取练习会话
#         session = db.query(PracticeSession).filter(
#             PracticeSession.id == session_id,
#             PracticeSession.user_id == current_user.id
#         ).first()
#
#         if not session:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail=i18n.get_text("SESSION_NOT_FOUND", lang)
#             )
#
#         # 创建测试记录
#         test = PitchTest(
#             user_id=current_user.id,
#             type=session.type,
#             user_recording=user_recording,
#             pitch_accuracy=pitch_accuracy,
#             timing_accuracy=timing_accuracy if timing_accuracy is not None else 0.0
#         )
#         db.add(test)
#
#         # 更新会话统计信息
#         session.notes_practiced += 1
#         session.average_accuracy = (
#             (session.average_accuracy * (session.notes_practiced - 1) + pitch_accuracy)
#             / session.notes_practiced
#         )
#
#         db.commit()
#
#         # 根据练习类型生成下一个练习内容
#         next_exercise = None
#         if session.type == PitchType.SINGLE_NOTE:
#             next_exercise = {"pitch": get_random_pitch([4]).value}
#         elif session.type == PitchType.INTERVAL:
#             interval_data = get_random_interval()
#             next_exercise = {
#                 "interval": {
#                     "name": interval_data["interval"].name.value,
#                     "description": interval_data["interval"].description,
#                     "pitches": [p.value for p in interval_data["pitches"]]
#                 }
#             }
#         elif session.type == PitchType.CHORD:
#             chord_data = get_random_chord()
#             next_exercise = {
#                 "chord": {
#                     "root": chord_data["root"].value,
#                     "type": chord_data["type"].value,
#                     "description": chord_data["chord"].description,
#                     "notes": [note.value for note in chord_data["notes"]]
#                 }
#             }
#
#         return {
#             "session_id": session_id,
#             "accuracy": pitch_accuracy,
#             "average_accuracy": session.average_accuracy,
#             "notes_practiced": session.notes_practiced,
#             "next_exercise": next_exercise,
#             "message": i18n.get_text("RESULT_SUBMITTED", lang)
#         }
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error in submit_training_result: {str(e)}\nTraceback: {traceback.format_exc()}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
#         )
#
# @router.post("/training/{session_id}/end")
# async def end_training_session(
#     request: Request,
#     session_id: int,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """结束训练会话"""
#     lang = get_language(request)
#     try:
#         session = db.query(PracticeSession).filter(
#             PracticeSession.id == session_id,
#             PracticeSession.user_id == current_user.id
#         ).first()
#
#         if not session:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail=i18n.get_text("SESSION_NOT_FOUND", lang)
#             )
#
#         # 计算练习时长（秒）
#         duration = int((datetime.utcnow() - session.created_at).total_seconds())
#         session.duration = duration
#
#         db.commit()
#
#         return {
#             "session_id": session_id,
#             "duration": duration,
#             "notes_practiced": session.notes_practiced,
#             "average_accuracy": session.average_accuracy,
#             "message": i18n.get_text("SESSION_ENDED", lang)
#         }
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error in end_training_session: {str(e)}\nTraceback: {traceback.format_exc()}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=i18n.get_text("INTERNAL_SERVER_ERROR", lang)
#         )