import traceback
import time
from fastapi import APIRouter, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect, Depends

from app.api.v1.auth_api import get_current_user
from app.api.v1.schemas.response.pitch_response import PitchAnalysisResult
from app.core.logger import logger
from app.services.tuner_service import TunerService, tuner_service
from app.services.audio_processing import AudioProcessor, audio_processor
from typing import Dict, Any, List, Callable, Optional
import json

from app.models.user import User
from app.services.fast_tuner_service import fast_tuner_service
from app.services.fast_audio_processing import fast_audio_processor

router = APIRouter(prefix="/tuner", tags=["tuner"])

# 存储用户ID和WebSocket连接的映射
user_connections: Dict[str, WebSocket] = {}

class UserWebSocketCallback:
    def __init__(self, user_id: str, websocket: WebSocket):
        self.user_id = user_id
        self.websocket = websocket
    
    async def __call__(self, result: Dict[str, Any]) -> None:
        """发送分析结果到对应的用户
        
        Args:
            result: 分析结果字典
        """
        try:
            await self.websocket.send_text(json.dumps(result))
        except Exception as e:
            logger.error(f"Error sending result to user {self.user_id}: {e}")
            # 如果发送失败，移除连接
            if self.user_id in user_connections:
                del user_connections[self.user_id]
                tuner_service.unregister_callback(self.user_id)

@router.post("/analyze")
async def analyze_pitch(file: UploadFile = File(...), current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """分析上传的音频文件的音高
    
    Args:
        file: 上传的音频文件
        
    Returns:
        Dict[str, Any]: 包含分析结果的字典
    """
    try:
        # 读取音频文件
        audio_data, sample_rate = audio_processor.read_audio_file(await file.read())
        
        # 分析音高
        note_name, frequency, cents_diff = tuner_service.analyze_pitch(audio_data, sample_rate)
        
        if note_name is None:
            raise HTTPException(status_code=400, detail="无法检测到音高")
            
        # 获取最接近的钢琴音高
        nearest_pitch, min_cents_diff = tuner_service.get_nearest_piano_pitch(frequency)
        
        # 获取调音状态和方向
        tuning_status = tuner_service.get_tuning_status(frequency)
        tuning_direction = tuner_service.get_tuning_direction(frequency)
        
        return {
            "timestamp": time.time(),
            "detected_note": note_name,
            "frequency": float(frequency),
            "cents_difference": float(cents_diff),
            "nearest_piano_pitch": {
                "name": nearest_pitch.name,
                "alias": nearest_pitch.alias,
                "pitch_number": nearest_pitch.pitch_number,
                "url": nearest_pitch.url
            },
            "tuning_status": tuning_status,
            "tuning_direction": tuning_direction
        }
        
    except Exception as e:
        logger.error(f"Error in analyze_pitch: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze/c")
async def analyze_pitch_c(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
) -> PitchAnalysisResult:
    """快速音高检测API
    
    使用pYIN C++绑定进行快速音高检测，适合实时应用。
    
    Args:
        file: 音频文件
        current_user: 当前用户
        
    Returns:
        PitchAnalysisResult: 包含检测结果的字典
    """
    try:
        # 分析音高
        note_name, frequency, cents_diff = fast_tuner_service.analyze_pitch_from_bytes(await file.read())
        
        if note_name is None:
            return {
                "code": 1,
                "message": "No pitch detected",
                "timestamp": time.time()
            }
            
        # 获取最接近的钢琴音高
        nearest_pitch, min_cents_diff = fast_tuner_service.get_nearest_piano_pitch(frequency)
        
        # 获取调音状态和方向
        tuning_status = fast_tuner_service.get_tuning_status(frequency)
        tuning_direction = fast_tuner_service.get_tuning_direction(frequency)
        
        return PitchAnalysisResult(
            frequency=float(frequency),
            note=note_name,
            cents_difference=float(cents_diff),
            nearest_piano_pitch= nearest_pitch,
            tuning_status=tuning_status,
            tuning_direction=tuning_direction
        )
    except Exception as e:
        logger.error(f"Error in analyze_pitch_c: {str(e)}\nTraceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/ws/analyze")
async def websocket_endpoint(websocket: WebSocket, user: User = Depends(get_current_user)):
    """WebSocket端点用于实时音频分析
    
    Args:
        websocket: WebSocket连接
        user: 当前用户
    """
    user_id = str(user.id)
    
    # 如果用户已经有连接，先关闭旧连接
    if user_id in user_connections:
        old_websocket = user_connections[user_id]
        try:
            await old_websocket.close()
        except Exception as e:
            pass
        tuner_service.unregister_callback(user_id)
    
    # 接受新连接
    await websocket.accept()
    user_connections[user_id] = websocket
    
    try:
        # 创建用户特定的回调
        user_ws_callback = UserWebSocketCallback(user_id, websocket)
        
        # 注册回调
        tuner_service.register_callback(user_id, user_ws_callback)
        
        # 开始该用户的实时分析
        tuner_service.start_user_analysis(user_id)
        
        while True:
            # 接收音频数据
            audio_data = await websocket.receive_bytes()
            
            # 添加到该用户的分析队列
            tuner_service.add_user_audio_data(user_id, audio_data)
            
    except WebSocketDisconnect:
        # 清理连接和回调
        if user_id in user_connections:
            del user_connections[user_id]
        tuner_service.unregister_callback(user_id)
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        # 清理连接和回调
        if user_id in user_connections:
            del user_connections[user_id]
        tuner_service.unregister_callback(user_id) 