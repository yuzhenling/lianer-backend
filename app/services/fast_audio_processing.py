import numpy as np
import librosa
import vamp
import time
import logging
from typing import List, Tuple, Optional
import soundfile as sf
import io
import aubio

logger = logging.getLogger(__name__)

class FastAudioProcessor:
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.min_frequency = 16.35  # C0的频率
        self.max_frequency = 4186.01  # C8的频率
        
    def read_audio_file(self, audio_bytes: bytes) -> Tuple[np.ndarray, int]:
        """快速读取音频文件数据
        
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
                
                # 如果采样率不是44100，进行重采样
                if sample_rate != self.sample_rate:
                    audio_data = librosa.resample(
                        audio_data,
                        orig_sr=sample_rate,
                        target_sr=self.sample_rate
                    )
                    sample_rate = self.sample_rate
                
                return audio_data, sample_rate
                
        except Exception as e:
            logger.error(f"Failed to read audio file: {str(e)}")
            raise ValueError(f"Failed to read audio file: {str(e)}")
    
    def detect_pitch_fast(self, audio_data: np.ndarray, sample_rate: int = None) -> List[float]:
        """使用aubio的YINFFT算法实现快速音高检测
        
        Args:
            audio_data: 音频数据
            sample_rate: 采样率
            
        Returns:
            List[float]: 检测到的基频列表
        """
        if sample_rate is None:
            sample_rate = self.sample_rate
            
        try:
            # 确保输入数据是float32类型
            audio_data = audio_data.astype(np.float32)
            
            # 1. 音频预处理
            # 应用高通滤波器去除直流分量，但保留低频信息
            audio_data = librosa.effects.preemphasis(audio_data, coef=0.3)  # 降低预加重系数以保留更多低频信息
            
            # 2. 应用汉宁窗减少频谱泄漏
            window = np.hanning(len(audio_data)).astype(np.float32)
            audio_data = audio_data * window
            
            # 3. 对于低音区，增加帧长度并降低采样率
            if len(audio_data) > 16384:
                audio_data = librosa.resample(audio_data, orig_sr=sample_rate, target_sr=sample_rate//2)
                sample_rate = sample_rate//2
                audio_data = audio_data.astype(np.float32)
            
            # 4. 使用aubio的YINFFT算法
            fmin = 16.35  # C0的频率
            fmax = self.max_frequency
            frame_length = 2048  # 增加帧长度以提高低音区准确性
            hop_length = 512  # 使用1/4重叠
            
            # 创建pitch检测器
            pitch_o = aubio.pitch(
                "yinfft",  # 使用YINFFT算法，对低音区更准确
                frame_length,
                hop_length,
                sample_rate
            )
            pitch_o.set_unit("Hz")
            pitch_o.set_tolerance(0.6)  # 降低容差以提高低音区准确性
            pitch_o.set_silence(-40)  # 降低静音阈值以检测更弱的信号
            
            # 处理音频数据
            frequencies = []
            total_frames = 0
            for i in range(0, len(audio_data) - frame_length, hop_length):
                frame = audio_data[i:i + frame_length]
                frame = frame.astype(np.float32)
                freq = pitch_o(frame)[0]
                if freq > 0 and fmin <= freq <= fmax:
                    frequencies.append(freq)
                total_frames += 1
            
            if not frequencies:
                return []
            
            # 5. 后处理
            frequencies_array = np.array(frequencies)
            
            # 对低音区进行特殊处理
            if frequencies_array.size > 0:
                # 计算频率的直方图
                hist, bin_edges = np.histogram(frequencies_array, bins=50)
                # 找到最频繁的频率范围
                most_frequent_bin = np.argmax(hist)
                # 获取该范围内的所有频率
                bin_frequencies = frequencies_array[
                    (frequencies_array >= bin_edges[most_frequent_bin]) &
                    (frequencies_array < bin_edges[most_frequent_bin + 1])
                ]
                
                if bin_frequencies.size > 0:
                    median_freq = np.median(bin_frequencies)
                    
                    # 检查是否是倍频错误
                    if median_freq < 65.41:  # C2的频率
                        possible_freqs = [median_freq * 2, median_freq / 2]
                        for freq in possible_freqs:
                            if self.min_frequency <= freq <= self.max_frequency:
                                frequencies.append(freq)
                    
                    # 使用加权中位数，给予低频更多权重
                    frequencies_array = np.array(frequencies)
                    weights = np.where(frequencies_array < 65.41, 1.0, 0.5)
                    weighted_frequencies = np.repeat(frequencies_array, weights.astype(int))
                    
                    if weighted_frequencies.size > 0:
                        weighted_median = np.median(weighted_frequencies)
                        
                        # 确保返回值不是NaN或无穷大
                        if not np.isnan(weighted_median) and not np.isinf(weighted_median):
                            return [float(weighted_median)]
            
            return []
            
        except Exception as e:
            logger.error(f"Error in detect_pitch_fast: {str(e)}")
            return []
    
    def hz_to_note(self, frequency: float) -> str:
        """将频率转换为音符名称
        
        Args:
            frequency: 频率
            
        Returns:
            str: 音符名称
        """
        if frequency <= 0:
            return ""
            
        # 计算与A4(440Hz)的半音距离
        n = 12 * np.log2(frequency / 440.0)
        # 四舍五入到最近的半音
        n = round(n)
        # 计算音符名称
        notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        note = notes[n % 12]
        # 计算八度
        octave = 4 + (n + 9) // 12
        return f"{note}{octave}"
    
    def note_to_hz(self, note: str) -> float:
        """将音符名称转换为频率
        
        Args:
            note: 音符名称
            
        Returns:
            float: 频率
        """
        if not note:
            return 0.0
            
        # 解析音符名称
        note_name = note[0]
        if len(note) > 1 and note[1] == "#":
            note_name += "#"
            octave = int(note[2:])
        else:
            octave = int(note[1:])
            
        # 计算与A4(440Hz)的半音距离
        notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        n = notes.index(note_name) - 9  # A4是第9个音符
        n += 12 * (octave - 4)
        
        # 计算频率
        return 440.0 * (2.0 ** (n / 12.0))


fast_audio_processor = FastAudioProcessor() 