# app/services/pitch_settings_service.py

from typing import List, Optional
from app.models.pitch_setting import *
from app.services.pitch_service import pitch_service


class PitchSettingsService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PitchSettingsService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # 单例模式，避免重复初始化
        if not hasattr(self, '_initialized'):
            self._initialized = True

    async def get_pitch_settings(self) -> PitchSettings:
        #default
        pitch_groups = await pitch_service.get_all_pitchgroups()
        if not pitch_groups:
             raise Exception("No Pitch Groups found")

        default_group = pitch_groups[4] #中央C4
        pitch_range = PitchRange(
            min=default_group.get_min(),
            max=default_group.get_max(),
            list=default_group.pitches
        )

        pitch_setting = PitchSettings(
            pitch_range=pitch_range,
            pitch_black_key= list(PitchBlackKey),
            mode= list(PitchMode),
        )
        return pitch_setting




pitch_settings_service = PitchSettingsService()