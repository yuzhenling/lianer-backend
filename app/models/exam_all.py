from dataclasses import dataclass

from app.api.v1.schemas.response.pitch_response import RhythmSettingResponse, MelodySettingResponse, RhythmScore, \
    MelodyScorePitch
from app.models.exam import SinglePitchExam, PitchIntervalExam, GroupPitchExam, PitchChordExam
from app.models.pitch_setting import PitchChordSetting, PitchIntervalSetting, PitchGroupSetting, PitchSingleSetting


@dataclass
class ExamSetting:
    pitch_single_setting: PitchSingleSetting
    pitch_group_setting: PitchGroupSetting
    pitch_interval_setting: PitchIntervalSetting
    pitch_chord_setting: PitchChordSetting
    rhythm_setting: RhythmSettingResponse
    melody_setting: MelodySettingResponse

@dataclass
class ExamData:
    single: SinglePitchExam
    group: GroupPitchExam
    interval: PitchIntervalExam
    chord: PitchChordExam
    rhythm: RhythmScore
    melody: MelodyScorePitch