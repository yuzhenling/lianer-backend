from typing import Dict, Any, List, Optional, Tuple

import librosa

from app.services.fast_audio_processing import FastAudioProcessor, fast_audio_processor
from app.services.pitch_service import pitch_service
import logging
import io
import numpy as np
import soundfile as sf
from aubio import pitch

logger = logging.getLogger(__name__)

class FastTunerService:
    def __init__(self):
        self.audio_processor = fast_audio_processor
        
    def analyze_pitch(self, audio_data: np.ndarray, sample_rate: int) -> Tuple[Optional[str], float, float]:
        """快速分析音频的音高
        
        Args:
            audio_data: 音频数据
            sample_rate: 采样率
            
        Returns:
            Tuple[Optional[str], float, float]: (最接近的音符名称, 频率, 音分偏差)
        """
        try:
            # 检测基频
            pitches = self.audio_processor.detect_pitch_fast(audio_data, sample_rate)
            if len(pitches) == 0:
                return None, 0.0, 0.0
                
            # 获取检测到的主频率
            main_frequency = pitches[0]
            
            # 转换为音符名称
            note_name = self.audio_processor.hz_to_note(main_frequency)
            
            # 获取最接近的钢琴音高
            nearest_pitch, min_cents_diff = self.get_nearest_piano_pitch(main_frequency)
            
            # 计算音分偏差
            target_hz = self.audio_processor.note_to_hz(nearest_pitch.name)
            cents_diff = 1200 * np.log2(main_frequency / target_hz)
            
            return note_name, main_frequency, cents_diff
            
        except Exception as e:
            logger.error(f"Error in analyze_pitch: {str(e)}")
            return None, 0.0, 0.0
    
    def get_nearest_piano_pitch(self, frequency: float) -> Tuple[Any, float]:
        """获取最接近的钢琴音高
        
        Args:
            frequency: 频率
            
        Returns:
            Tuple[Any, float]: (最接近的钢琴音高, 最小音分偏差)
        """
        # 获取所有钢琴音高
        pitches = pitch_service.get_all_pitch()
        
        # 计算与每个音高的音分偏差
        min_cents_diff = float('inf')
        nearest_pitch = None
        
        for pitch in pitches:
            target_hz = self.audio_processor.note_to_hz(pitch.name)
            cents_diff = abs(1200 * np.log2(frequency / target_hz))
            
            if cents_diff < min_cents_diff:
                min_cents_diff = cents_diff
                nearest_pitch = pitch
        
        return nearest_pitch, min_cents_diff
    
    def get_tuning_status(self, frequency: float) -> str:
        """获取调音状态
        
        Args:
            frequency: 频率
            
        Returns:
            str: 调音状态
        """
        _, min_cents_diff = self.get_nearest_piano_pitch(frequency)
        
        if min_cents_diff <= 5:
            return "perfect"
        elif min_cents_diff <= 10:
            return "good"
        elif min_cents_diff <= 20:
            return "fair"
        else:
            return "poor"
    
    def get_tuning_direction(self, frequency: float) -> str:
        """获取调音方向
        
        Args:
            frequency: 频率
            
        Returns:
            str: 调音方向
        """
        nearest_pitch, _ = self.get_nearest_piano_pitch(frequency)
        target_hz = self.audio_processor.note_to_hz(nearest_pitch.name)
        
        if frequency > target_hz:
            return "higher"
        elif frequency < target_hz:
            return "lower"
        else:
            return "in_tune"




    # 音高频率到音名的映射
    def freq_to_note_name(self, frequency):
        if frequency <= 0:
            return "Unknown"

        A4 = 440.0
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        semitones_from_A4 = round(12 * np.log2(frequency / A4))
        note_index = (semitones_from_A4 + 9) % 12  # A=0 -> C=9
        octave = 4 + ((semitones_from_A4 + 9) // 12)
        return f"{note_names[note_index]}{octave}"

    # Service 方法
    def analyze_pitch_from_bytes(self, file_bytes):
        # 读取 bytes，转为 numpy 数组
        audio_data, samplerate = librosa.load(io.BytesIO(file_bytes), sr=44100)
        audio_data, _ = librosa.effects.trim(audio_data, top_db=30)

        # 如果是立体声，取第一个通道
        if len(audio_data.shape) > 1:
            audio_data = audio_data[:, 0]

        win_s = 4096  # FFT窗口大小
        hop_s = 2048  # 步进
        pitch_detector = pitch("yin", win_s, hop_s, samplerate)
        pitch_detector.set_unit("Hz")
        pitch_detector.set_silence(-40)

        detected_notes = []
        total_frames = len(audio_data)

        frequencies = []
        for i in range(0, len(audio_data) - hop_s, hop_s):
            frame = audio_data[i:i + hop_s].astype(np.float32)
            freq = pitch_detector(frame)[0]
            if freq > 0:
                frequencies.append(freq)

        if not frequencies:
            return "Unknown", 0.0, 0.0

        avg_freq = np.median(frequencies)
        note_name = self.freq_to_note_name(avg_freq)
        cents_diff = 1200 * np.log2(avg_freq / 440.0) if avg_freq > 0 else 0.0

        return note_name, avg_freq, cents_diff





fast_tuner_service = FastTunerService() 