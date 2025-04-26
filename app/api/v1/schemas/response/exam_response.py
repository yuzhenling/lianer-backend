from dataclasses import dataclass

from pydantic import BaseModel

from app.api.v1.schemas.response.pitch_response import MelodySettingResponse, RhythmSettingResponse, \
    PitchSingleSettingResponse, PitchGroupSettingResponse, PitchIntervalSettingResponse, PitchChordSettingResponse, \
    RhythmScore, MelodyScorePitch, SinglePitchExamResponse, PitchIntervalExamResponse, GroupPitchExamResponse, \
    PitchChordExamResponse
from app.models.exam import SinglePitchExam, PitchIntervalExam



class ExamSettingResponse(BaseModel):
    pitch_single_setting: PitchSingleSettingResponse
    pitch_group_setting: PitchGroupSettingResponse
    pitch_interval_setting: PitchIntervalSettingResponse
    pitch_chord_setting: PitchChordSettingResponse
    rhythm_setting: RhythmSettingResponse
    melody_setting: MelodySettingResponse



class ExamResponse(BaseModel):
    single: SinglePitchExamResponse
    group: GroupPitchExamResponse
    interval: PitchIntervalExamResponse
    chord: PitchChordExamResponse
    rhythm: RhythmScore
    melody: MelodyScorePitch