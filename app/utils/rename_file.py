import os

class ToneRenamer:


    @staticmethod
    def rename_files(directory):
        # 音名映射表（根据数字映射到音名）
        PIANO_KEYS = {
            1: "A0",
            2: "A#0_Bb0",
            3: "B0",
            4: "C1",
            5: "C#1_Db1",
            6: "D1",
            7: "D#1_Eb1",
            8: "E1",
            9: "F1",
            10: "F#1_Gb1",
            11: "G1",
            12: "G#1_Ab1",
            13: "A1",
            14: "A#1_Bb1",
            15: "B1",
            16: "C2",
            17: "C#2_Db2",
            18: "D2",
            19: "D#2_Eb2",
            20: "E2",
            21: "F2",
            22: "F#2_Gb2",
            23: "G2",
            24: "G#2_Ab2",
            25: "A2",
            26: "A#2_Bb2",
            27: "B2",
            28: "C3",
            29: "C#3_Db3",
            30: "D3",
            31: "D#3_Eb3",
            32: "E3",
            33: "F3",
            34: "F#3_Gb3",
            35: "G3",
            36: "G#3_Ab3",
            37: "A3",
            38: "A#3_Bb3",
            39: "B3",
            40: "C4",
            41: "C#4_Db4",
            42: "D4",
            43: "D#4_Eb4",
            44: "E4",
            45: "F4",
            46: "F#4_Gb4",
            47: "G4",
            48: "G#4_Ab4",
            49: "A4",
            50: "A#4_Bb4",
            51: "B4",
            52: "C5",
            53: "C#5_Db5",
            54: "D5",
            55: "D#5_Eb5",
            56: "E5",
            57: "F5",
            58: "F#5_Gb5",
            59: "G5",
            60: "G#5_Ab5",
            61: "A5",
            62: "A#5_Bb5",
            63: "B5",
            64: "C6",
            65: "C#6_Db6",
            66: "D6",
            67: "D#6_Eb6",
            68: "E6",
            69: "F6",
            70: "F#6_Gb6",
            71: "G6",
            72: "G#6_Ab6",
            73: "A6",
            74: "A#6_Bb6",
            75: "B6",
            76: "C7",
            77: "C#7_Db7",
            78: "D7",
            79: "D#7_Eb7",
            80: "E7",
            81: "F7",
            82: "F#7_Gb7",
            83: "G7",
            84: "G#7_Ab7",
            85: "A7",
            86: "A#7_Bb7",
            87: "B7",
            88: "C8"
        }
        """
        重命名目录中的文件
        :param directory: 包含wav文件的目录路径
        """
        # 遍历目录中的所有文件
        number=0

        for filename in os.listdir(directory):
            # 检查文件是否是wav文件且符合命名规则
            if filename.startswith("tone") and filename.endswith(".wav"):
                # 提取文件中的数字
                try:
                    number = int(filename.split("(")[1].split(")")[0].strip())
                    print(f"-->: {filename}   ++++  {number}")
                    if 1 <= number <= 88:
                        # 生成新的文件名
                        new_name = f"tone_{number}_{PIANO_KEYS.get(number)}.wav"
                        # 重命名文件
                        old_path = os.path.join(directory, filename)
                        new_path = os.path.join(directory, new_name)
                        os.rename(old_path, new_path)
                        print(f"Renamed: {filename} -> {new_name}")
                    else:
                        print(f"Skipped: {filename} (number out of range)")
                except ValueError:
                    print(f"Skipped: {filename} (invalid number format)")
            else:
                print(f"Skipped: {filename} (not a tone file)")



# 使用示例
if __name__ == "__main__":
    # 设置包含wav文件的目录路径
    directory = "/home/yu/gitdev/shengyibaodian/app/static/audio"
    # 调用工具类重命名文件
    ToneRenamer.rename_files(directory)