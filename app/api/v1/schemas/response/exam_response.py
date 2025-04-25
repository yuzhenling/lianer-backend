from typing import List

from pydantic import BaseModel

from app.api.v1.schemas.response.pitch_response import MelodySettingResponse, RhythmSettingResponse, \
    PitchSingleSettingResponse, PitchGroupSettingResponse, PitchIntervalSettingResponse, PitchChordSettingResponse, \
    RhythmQuestionResponse, MelodyQuestionResponse
from app.models.exam import SinglePitchExam, PitchIntervalExam
from app.models.pitch_setting import PitchSingleSetting, PitchGroupSetting, PitchIntervalSetting, \
    PitchChordSetting



class ExamSettingResponse(BaseModel):
    pitch_single_setting: PitchSingleSettingResponse
    pitch_group_setting: PitchGroupSettingResponse
    pitch_interval_setting: PitchIntervalSettingResponse
    pitch_chord_setting: PitchChordSettingResponse
    rhythm_setting: RhythmSettingResponse
    melody_setting: MelodySettingResponse

class ExamResponse(BaseModel):
    single: SinglePitchExam
    group: SinglePitchExam
    interval: PitchIntervalExam
    chord: PitchIntervalExam
    rhythm: RhythmQuestionResponse
    melody: MelodyQuestionResponse