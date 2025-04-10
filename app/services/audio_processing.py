import librosa
import numpy as np
from typing import List, Tuple, Optional
import soundfile as sf
from pathlib import Path
import io
from scipy.signal import find_peaks


class AudioProcessor:
    def __init__(self):
        self.sample_rate = 44100  # 默认采样率
        self.min_frequency = 16.35  # C0的频率
        self.max_frequency = 4186.01  # C8的频率
        
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
            
        # 预处理音频数据
        # 1. 应用高通滤波器去除直流分量
        audio_data = librosa.effects.preemphasis(audio_data)
        
        # 2. 应用汉宁窗减少频谱泄漏
        # 确保窗口大小与音频数据长度匹配
        window = np.hanning(len(audio_data))
        audio_data = audio_data * window
        
        # 使用多种方法检测基频
        pitches = []
        
        # 方法1：使用改进的YIN算法
        # 对于低音区，增加帧长度和降低fmin
        try:
            f0_yin, voiced_flag, voiced_probs = librosa.pyin(
                audio_data,
                fmin=16.35,  # C0的频率
                fmax=4186.01,  # C8的频率
                sr=sample_rate,
                frame_length=min(8192, len(audio_data)),  # 确保帧长度不超过音频长度
                hop_length=1024,
                fill_na=np.nan,
                center=True,
                pad_mode='reflect'
            )
            valid_pitches = f0_yin[~np.isnan(f0_yin)]
            if len(valid_pitches) > 0:
                pitches.extend(valid_pitches)
        except Exception as e:
            print(f"YIN algorithm failed: {str(e)}")
        
        # 方法2：使用自相关函数（针对低音区优化）
        try:
            # 增加自相关窗口长度
            autocorr = np.correlate(audio_data, audio_data, mode='full')
            autocorr = autocorr[len(autocorr)//2:]
            
            # 使用改进的峰值检测
            peaks, _ = find_peaks(
                autocorr,
                distance=int(sample_rate/self.max_frequency),
                prominence=0.1*np.max(autocorr)
            )
            
            if len(peaks) > 0:
                # 计算基频
                peak = peaks[0]
                if peak > 0:
                    freq = sample_rate / peak
                    if self.min_frequency <= freq <= self.max_frequency:
                        pitches.append(freq)
        except Exception as e:
            print(f"Autocorrelation failed: {str(e)}")
        
        # 方法3：使用改进的频谱分析
        try:
            # 增加FFT点数以提高频率分辨率
            n_fft = min(16384, len(audio_data))  # 确保FFT点数不超过音频长度
            D = librosa.stft(audio_data, n_fft=n_fft, hop_length=1024)
            S = np.abs(D)
            
            # 计算频率轴
            freqs = librosa.fft_frequencies(sr=sample_rate, n_fft=n_fft)
            
            # 使用谐波积谱（HPS）方法
            # 修正HPS计算，确保数组形状匹配
            hps = np.ones_like(S[0])
            for i in range(1, 6):  # 考虑前5个谐波
                # 对每个谐波进行下采样
                downsampled = S[::i, :].mean(axis=1)
                # 确保形状匹配
                if len(downsampled) == len(hps):
                    hps *= downsampled
            
            # 找到HPS中的峰值
            peak_idx = np.argmax(hps)
            peak_freq = freqs[peak_idx]
            if self.min_frequency <= peak_freq <= self.max_frequency:
                pitches.append(peak_freq)
        except Exception as e:
            print(f"Spectral analysis failed: {str(e)}")
        
        # 方法4：使用倒谱分析（cepstral analysis）
        try:
            # 这种方法对基频检测特别有效
            cepstrum = np.fft.ifft(np.log(np.abs(D) + 1e-10))
            cepstrum = np.abs(cepstrum)
            
            # 在倒谱中找到峰值
            quefrency = np.arange(len(cepstrum)) / sample_rate
            valid_quefrency = (quefrency > 1/self.max_frequency) & (quefrency < 1/self.min_frequency)
            peak_idx = np.argmax(cepstrum[valid_quefrency])
            cepstral_freq = 1 / quefrency[valid_quefrency][peak_idx]
            if self.min_frequency <= cepstral_freq <= self.max_frequency:
                pitches.append(cepstral_freq)
        except Exception as e:
            print(f"Cepstral analysis failed: {str(e)}")
        
        # 对检测到的频率进行后处理
        if pitches:
            # 去除异常值
            pitches = np.array(pitches)
            mean_pitch = np.mean(pitches)
            std_pitch = np.std(pitches)
            valid_pitches = pitches[(pitches > mean_pitch - 2*std_pitch) & 
                                  (pitches < mean_pitch + 2*std_pitch)]
            
            if len(valid_pitches) > 0:
                # 使用中位数而不是平均值，以减少异常值的影响
                return [np.median(valid_pitches)]
        
        return []
    
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
        """比较目标音符和录制音高的准确度
        
        Args:
            target_note: 目标音符名称
            recorded_pitch: 录制的音高频率
            
        Returns:
            float: 音分偏差
        """
        target_hz = librosa.note_to_hz(target_note)
        cents_diff = 1200 * np.log2(recorded_pitch / target_hz)
        return cents_diff
    
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