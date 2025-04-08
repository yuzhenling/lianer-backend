class ChordInversion:
    @staticmethod
    def root_position(pitches):
        """原位和弦（根位），直接返回原顺序"""
        return pitches

    @staticmethod
    def first_inversion(pitches):
        """第一转位：将第一个音（根音）移到最上面"""
        if len(pitches) < 2:
            return pitches
        return pitches[1:] + [pitches[0]]

    @staticmethod
    def second_inversion(pitches):
        """第二转位：将前两个音移到最上面"""
        if len(pitches) < 3:
            return pitches
        return pitches[2:] + pitches[:2]

    @staticmethod
    def third_inversion(pitches):
        """第三转位：将前三个音移到最上面（适用于七和弦）"""
        if len(pitches) < 4:
            return pitches
        return pitches[3:] + pitches[:3]

    @staticmethod
    def invert(pitches, transfer_set=1):
        """通用的转位方法
        :param pitches: 和弦音高列表（按根位顺序）
        :param transfer_set: 转位级别 0=原位, 1=第一转位, 2=第二转位, 3=第三转位
        :return: 转位后的音高列表
        """
        if transfer_set == 1:
            return ChordInversion.root_position(pitches)
        elif transfer_set == 2:
            return ChordInversion.first_inversion(pitches)
        elif transfer_set == 3:
            return ChordInversion.second_inversion(pitches)
        elif transfer_set == 4:
            return ChordInversion.third_inversion(pitches)
        else:
            raise ValueError("Inversion level must be between 0 and 3")