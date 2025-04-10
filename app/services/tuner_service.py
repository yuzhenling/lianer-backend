import numpy as np
import librosa
from typing import Optional, Tuple, List, Callable, Dict, Any
from app.services.audio_processing import AudioProcessor
from app.models.pitch import Pitch
from app.services.pitch_service import pitch_service
import queue
import threading
import time
import json

class UserAnalysisContext:
    def __init__(self, user_id: str, callback: Callable[[Dict[str, Any]], None]):
        self.user_id = user_id
        self.callback = callback
        self.audio_queue = queue.Queue()
        self.is_analyzing = False
        self.analysis_thread = None
        self.buffer = []

class TunerService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TunerService, cls).__new__(cls)
            cls._instance.audio_processor = AudioProcessor()
            cls._instance.user_contexts = {}  # 存储用户分析上下文
        return cls._instance
    
    def register_callback(self, user_id: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        """注册用户特定的分析结果回调函数
        
        Args:
            user_id: 用户ID
            callback: 回调函数，接收分析结果字典作为参数
        """
        if user_id not in self.user_contexts:
            self.user_contexts[user_id] = UserAnalysisContext(user_id, callback)
    
    def unregister_callback(self, user_id: str) -> None:
        """取消注册用户特定的回调函数
        
        Args:
            user_id: 用户ID
        """
        if user_id in self.user_contexts:
            context = self.user_contexts[user_id]
            if context.is_analyzing:
                self.stop_user_analysis(user_id)
            del self.user_contexts[user_id]
    
    def start_user_analysis(self, user_id: str, sample_rate: int = 44100, frame_length: int = 2048) -> None:
        """开始特定用户的实时音频分析
        
        Args:
            user_id: 用户ID
            sample_rate: 采样率
            frame_length: 每帧的采样数
        """
        if user_id not in self.user_contexts:
            return
            
        context = self.user_contexts[user_id]
        if context.is_analyzing:
            return
            
        context.is_analyzing = True
        context.analysis_thread = threading.Thread(
            target=self._user_analysis_loop,
            args=(user_id, sample_rate, frame_length),
            daemon=True
        )
        context.analysis_thread.start()
    
    def stop_user_analysis(self, user_id: str) -> None:
        """停止特定用户的实时音频分析
        
        Args:
            user_id: 用户ID
        """
        if user_id not in self.user_contexts:
            return
            
        context = self.user_contexts[user_id]
        context.is_analyzing = False
        if context.analysis_thread:
            context.analysis_thread.join()
            context.analysis_thread = None
    
    def add_user_audio_data(self, user_id: str, audio_data: bytes) -> None:
        """添加特定用户的音频数据到分析队列
        
        Args:
            user_id: 用户ID
            audio_data: 音频数据
        """
        if user_id in self.user_contexts:
            self.user_contexts[user_id].audio_queue.put(audio_data)
    
    def _user_analysis_loop(self, user_id: str, sample_rate: int, frame_length: int) -> None:
        """特定用户的实时分析循环
        
        Args:
            user_id: 用户ID
            sample_rate: 采样率
            frame_length: 每帧的采样数
        """
        context = self.user_contexts[user_id]
        
        while context.is_analyzing:
            try:
                # 从队列获取音频数据
                audio_data = context.audio_queue.get(timeout=0.1)
                context.buffer.extend(audio_data)
                
                # 当缓冲区足够大时进行分析
                if len(context.buffer) >= frame_length:
                    # 转换为numpy数组
                    audio_array = np.frombuffer(bytes(context.buffer[:frame_length]), dtype=np.float32)
                    context.buffer = context.buffer[frame_length:]
                    
                    # 分析音高
                    note_name, frequency, cents_diff = self.analyze_pitch(audio_array, sample_rate)
                    
                    if note_name is not None:
                        # 获取最接近的钢琴音高
                        nearest_pitch, min_cents_diff = self.get_nearest_piano_pitch(frequency)
                        
                        # 获取调音状态和方向
                        tuning_status = self.get_tuning_status(frequency)
                        tuning_direction = self.get_tuning_direction(frequency)
                        
                        # 构建分析结果
                        result = {
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
                        
                        # 调用用户特定的回调
                        try:
                            context.callback(result)
                        except Exception as e:
                            print(f"Callback error for user {user_id}: {e}")
                            self.unregister_callback(user_id)
                            break
                        
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Analysis error for user {user_id}: {e}")
                continue
    
    def analyze_pitch(self, audio_data: np.ndarray, sample_rate: int) -> Tuple[Optional[str], float, float]:
        """分析音频的音高
        
        Args:
            audio_data: 音频数据
            sample_rate: 采样率
            
        Returns:
            Tuple[Optional[str], float, float]: (最接近的音符名称, 频率, 音分偏差)
        """
        # 检测基频
        pitches = self.audio_processor.detect_pitch(audio_data, sample_rate)
        if len(pitches) == 0:
            return None, 0.0, 0.0
            
        # 获取检测到的主频率
        main_frequency = pitches[0]
        
        # 获取最接近的钢琴音高
        nearest_pitch, min_cents_diff = self.get_nearest_piano_pitch(main_frequency)
        
        # 计算与最接近钢琴音高的音分偏差
        target_hz = librosa.note_to_hz(nearest_pitch.name)
        cents_diff = 1200 * np.log2(main_frequency / target_hz)
        
        # 对于低音区（C1及以下），使用更严格的判断标准
        if nearest_pitch.pitch_number <= 3:  # C1及以下
            # 检查是否是倍频错误
            possible_octaves = [-1, 0, 1]  # 可能的八度偏移
            best_cents_diff = abs(cents_diff)
            best_pitch = nearest_pitch
            
            for octave_offset in possible_octaves:
                # 计算可能的正确音高
                possible_pitch_number = nearest_pitch.pitch_number + (12 * octave_offset)
                if 0 <= possible_pitch_number <= 88:  # 确保在钢琴音域内
                    possible_pitch = pitch_service.get_pitch_by_number(possible_pitch_number)
                    if possible_pitch:
                        possible_target_hz = librosa.note_to_hz(possible_pitch.name)
                        possible_cents_diff = 1200 * np.log2(main_frequency / possible_target_hz)
                        
                        # 如果这个音高更接近，更新最佳匹配
                        if abs(possible_cents_diff) < best_cents_diff:
                            best_cents_diff = abs(possible_cents_diff)
                            best_pitch = possible_pitch
                            cents_diff = possible_cents_diff
        
        return best_pitch.name, main_frequency, cents_diff
    
    def get_nearest_piano_pitch(self, frequency: float) -> Tuple[Pitch, float]:
        """获取最接近的钢琴音高
        
        Args:
            frequency: 输入频率
            
        Returns:
            Tuple[Pitch, float]: (最接近的钢琴音高对象, 音分偏差)
        """
        # 获取所有钢琴音高
        piano_pitches = pitch_service.get_all_pitch()
        
        min_cents_diff = float('inf')
        nearest_pitch = None
        
        for pitch in piano_pitches:
            # 获取目标频率
            target_frequency = librosa.note_to_hz(pitch.name)
            
            # 计算音分偏差
            cents_diff = abs(1200 * np.log2(frequency / target_frequency))
            
            if cents_diff < min_cents_diff:
                min_cents_diff = cents_diff
                nearest_pitch = pitch
                
        return nearest_pitch, min_cents_diff
    
    def get_tuning_status(self, frequency: float) -> str:
        """获取调音状态
        
        Args:
            frequency: 输入频率
            
        Returns:
            str: 调音状态描述
        """
        nearest_pitch, cents_diff = self.get_nearest_piano_pitch(frequency)
        
        if cents_diff < 5:  # 5音分以内认为是准确的
            return "perfect"
        elif cents_diff < 20:  # 20音分以内认为是接近的
            return "close"
        else:
            return "far"
    
    def get_tuning_direction(self, frequency: float) -> str:
        """获取调音方向
        
        Args:
            frequency: 输入频率
            
        Returns:
            str: 调音方向描述
        """
        nearest_pitch, cents_diff = self.get_nearest_piano_pitch(frequency)
        target_frequency = librosa.note_to_hz(nearest_pitch.name)
        
        if frequency > target_frequency:
            return "higher"
        else:
            return "lower"


tuner_service = TunerService()