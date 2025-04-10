import librosa
import numpy as np
from typing import List, Tuple, Optional
import soundfile as sf
from pathlib import Path
import io


class AudioProcessor:
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        
    def load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        """加载音频文件"""
        y, sr = librosa.load(file_path, sr=self.sample_rate)
        return y, sr
    
    def read_audio_file(self, audio_bytes: bytes) -> Tuple[np.ndarray, int]:
        """读取音频文件数据
        
        Args:
            audio_bytes: 音频文件的字节数据
            
        Returns:
            Tuple[np.ndarray, int]: (音频数据数组, 采样率)
        """
        try:
            # 使用soundfile读取音频数据
            with io.BytesIO(audio_bytes) as audio_file:
                audio_data, sample_rate = sf.read(audio_file)
                
                # 如果是立体声，转换为单声道
                if len(audio_data.shape) > 1:
                    audio_data = np.mean(audio_data, axis=1)
                    
                # 确保数据类型为float32
                audio_data = audio_data.astype(np.float32)
                
                return audio_data, sample_rate
                
        except Exception as e:
            raise ValueError(f"Failed to read audio file: {str(e)}")
    
    def detect_pitch(self, audio_data: np.ndarray, sample_rate: int = None) -> List[float]:
        """检测音频中的基频
        
        Args:
            audio_data: 音频数据
            sample_rate: 采样率，如果为None则使用默认值
            
        Returns:
            List[float]: 检测到的基频列表
        """
        if sample_rate is None:
            sample_rate = self.sample_rate
            
        # 使用librosa的YIN算法检测基频
        pitches, magnitudes = librosa.piptrack(
            y=audio_data,
            sr=sample_rate,
            fmin=librosa.note_to_hz('C0'),  # 最低音高
            fmax=librosa.note_to_hz('C8')   # 最高音高
        )
        
        # 获取有效的基频
        valid_pitches = []
        for i in range(pitches.shape[1]):
            index = magnitudes[:, i].argmax()
            pitch = pitches[index, i]
            if pitch > 0:  # 只保留有效的基频
                valid_pitches.append(pitch)
                
        return valid_pitches
    
    def hz_to_note(self, frequency: float) -> str:
        """将频率转换为音符名称
        
        Args:
            frequency: 频率值
            
        Returns:
            str: 音符名称
        """
        # 使用librosa将频率转换为音符名称
        note = librosa.hz_to_note(frequency)
        return note
    
    def compare_pitch_accuracy(self, target_note: str, recorded_pitch: float) -> float:
        """比较目标音高和实际音高的准确度"""
        target_hz = librosa.note_to_hz(target_note)
        cents_diff = abs(1200 * np.log2(recorded_pitch / target_hz))
        # 将音分差异转换为0-100的准确度分数
        accuracy = max(0, 100 - (cents_diff / 2))  # 50音分内为合格
        return accuracy
    
    def analyze_melody(self, audio: np.ndarray, target_notes: List[str]) -> Tuple[float, float]:
        """分析旋律的音高和节奏准确度"""
        # 检测音高
        pitches = self.detect_pitch(audio)
        
        # 获取音符时间点
        onset_frames = librosa.onset.onset_detect(y=audio, sr=self.sample_rate)
        onset_times = librosa.frames_to_time(onset_frames, sr=self.sample_rate)
        
        # 计算音高准确度
        pitch_accuracies = []
        for i, target_note in enumerate(target_notes):
            if i < len(onset_frames):
                frame_idx = onset_frames[i]
                if frame_idx < len(pitches):
                    detected_pitch = pitches[frame_idx]
                    accuracy = self.compare_pitch_accuracy(target_note, detected_pitch)
                    pitch_accuracies.append(accuracy)
        
        # 计算节奏准确度（基于音符间隔的一致性）
        timing_accuracy = 100.0  # 默认完美
        if len(onset_times) > 1:
            target_intervals = np.diff(np.linspace(0, len(target_notes), len(target_notes)+1)[:-1])
            detected_intervals = np.diff(onset_times)
            if len(detected_intervals) > 0:
                # 归一化间隔并计算差异
                target_intervals = target_intervals / np.mean(target_intervals)
                detected_intervals = detected_intervals / np.mean(detected_intervals)
                timing_accuracy = max(0, 100 - 50 * np.mean(np.abs(target_intervals - detected_intervals[:len(target_intervals)])))
        
        return (
            float(np.mean(pitch_accuracies)) if pitch_accuracies else 0.0,
            float(timing_accuracy)
        )
    
    def save_audio(self, audio: np.ndarray, file_path: str) -> None:
        """保存音频文件"""
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        sf.write(file_path, audio, self.sample_rate)

audio_processor = AudioProcessor()