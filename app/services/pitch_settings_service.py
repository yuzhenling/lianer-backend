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

    async def get_pitch_single_settings(self) -> PitchSingleSetting:
        #default
        pitch_groups = await pitch_service.get_all_pitchgroups()
        if not pitch_groups:
             raise Exception("No Pitch Groups found")

        default_group = pitch_groups[4] #中央C4
        pitch_range = PitchRange(
            min=default_group.get_min(),
            max=default_group.get_max(),
            list=default_group.pitch_pairs
        )

        pitch_black_keys = [
            {
                "key": pbk._value,
                "display_value": pbk.display_value
            }
            for pbk in PitchBlackKey  # 或 PitchBlackKey.__members__.values()
        ]
        mode = [
            {
                "key": pm._value,
                "display_value": pm.display_value
            }
            for pm in PitchMode  # 或 PitchBlackKey.__members__.values()
        ]


        pitch_setting = PitchSingleSetting(
            pitch_range=pitch_range,
            pitch_black_key= pitch_black_keys,
            mode= mode
        )
        return pitch_setting

    async def get_pitch_group_settings(self) -> PitchGroupSetting:
        #default
        pitch_groups = await pitch_service.get_all_pitchgroups()
        if not pitch_groups:
             raise Exception("No Pitch Groups found")

        default_group = pitch_groups[4] #中央C4

        pitch_range = PitchRange(
            min=default_group.get_min(),
            max=default_group.get_max(),
            list=default_group.pitch_pairs
        )

        pitch_black_keys = [
            {
                "key": pbk._value,
                "display_value": pbk.display_value
            }
            for pbk in PitchBlackKey  # 或 PitchBlackKey.__members__.values()
        ]

        count = [2,4,6,8,10]
        tempo = [50,60,70,80,90,100,110,120]


        pitch_setting = PitchGroupSetting(
            pitch_range=pitch_range,
            pitch_black_key= pitch_black_keys,
            count= count,
            tempo= tempo,
        )
        return pitch_setting

    async def get_pitch_interval_settings(self) -> PitchIntervalSetting:
        #default
        answer_mode = [AnswerMode.CONCORDANCE.to_dict(),AnswerMode.QUALITY.to_dict(),AnswerMode.PITCH.to_dict()]
        concordance_choice = [ConcordanceChoice.CONCORDANCE.to_dict(),ConcordanceChoice.CONCORDANCE_PART.to_dict(),ConcordanceChoice.CONCORDANCE_NO.to_dict()]
        play_mode = [PlayMode.HARMONY.to_dict(),PlayMode.UP.to_dict(),PlayMode.DOWN.to_dict(),PlayMode.UP_DOWN.to_dict(),]
        fix_mode = [FixMode.ROOT_FIX.to_dict(),FixMode.TOP_FIX.to_dict(),FixMode.RANDOM.to_dict()]

        intervals = await pitch_service.get_all_intervals()
        interval_list: List[dict[int, str]] = []
        for interval in intervals:
            interval_dict = {"id":interval.id,"name":interval.name,"type_id":interval.type_id,"type_name": interval.type_name,"semitone_number":interval.semitone_number}
            interval_list.append(interval_dict)

        fix_mode_vals = ["Do","Re","Mi","Fa","Sol","La","Ti"]

        pitch_interval_setting = PitchIntervalSetting(
            answer_mode=answer_mode,
            concordance_choice=concordance_choice,
            quality_choice=interval_list,
            play_mode=play_mode,
            interval_list=interval_list,
            fix_mode_enabled=False,
            fix_mode=fix_mode,
            fix_mode_vals=fix_mode_vals,

        )
        return pitch_interval_setting



pitch_settings_service = PitchSettingsService()