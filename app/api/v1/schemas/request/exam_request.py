from pydantic import BaseModel

from app.api.v1.schemas.request.pitch_request import PitchSettingRequest, PitchGroupSettingRequest, \
    PitchIntervalSettingRequest, PitchChordSettingRequest, RhythmSettingRequest, MelodySettingRequest


class ExamRequest(BaseModel):
    pitch_setting: PitchSettingRequest
    pitch_group_setting: PitchGroupSettingRequest
    pitch_interval_setting: PitchIntervalSettingRequest
    pitch_chord_setting: PitchChordSettingRequest
    rhythm_setting: RhythmSettingRequest
    melody_setting: MelodySettingRequest

