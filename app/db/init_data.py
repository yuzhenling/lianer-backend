import os
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.logger import logger
from app.models.pitch import Pitch, PitchIntervalType, PitchInterval, PitchConcordanceType
from app.models.vip import Vip, VipLevel
from app.constants.constant import PIANO_KEYS_MAPPING


def init_vip_levels(db: Session):
    """初始化VIP等级数据"""
    try:
        # 检查是否已经存在数据
        existing_levels = db.query(Vip).all()
        if existing_levels:
            logger.info("VIP levels already initialized, skipping...")
            return

        # VIP等级描述
        vip_descriptions = {
            VipLevel.FREE: "普通用户: *****************",
            VipLevel.NORMAL: "普通会员: 旋律听写, 节奏练习, 节奏听写",
            VipLevel.HALF_YEAR: "半年VIP会员: ***********",
            VipLevel.ONE_YEAR: "一年VIP会员: ************"
        }

        vip_price = {
            VipLevel.FREE: 0,
            VipLevel.NORMAL: 0,
            VipLevel.HALF_YEAR: 9,
            VipLevel.ONE_YEAR: 99
        }

        vip_discount = {
            VipLevel.FREE: 0,
            VipLevel.NORMAL: 0,
            VipLevel.HALF_YEAR: 0,
            VipLevel.ONE_YEAR: 0
        }

        # 插入VIP等级数据
        for level in VipLevel:
            try:
                vip = Vip(
                    level=level,
                    describe=vip_descriptions[level],
                    price=vip_price[level],
                    discount=vip_discount[level],
                )
                db.add(vip)
                db.flush()  # 立即刷新以检查是否有问题
            except Exception as e:
                logger.error(f"Failed to insert VIP level {level}: {str(e)}")
                raise e

        db.commit()
        logger.info("Successfully initialized VIP levels")

    except Exception as e:
        logger.error("Failed to initialize VIP levels", exc_info=True)
        db.rollback()
        raise e

def init_pitches(db: Session):
    """初始化音高数据"""
    try:
        # 检查是否已经有数据
        pitches = db.query(Pitch).all()
        if pitches:
            logger.info("Pitch already initialized, skipping...")
            return

        # 获取音频文件目录的绝对路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        audio_dir = os.path.join(current_dir, "..", "static", "audio")
        # audio_dir = "/static/audio/"

        # 遍历PIANO_KEYS中的所有音高
        for number, note_name in PIANO_KEYS_MAPPING.items():
            # 分割主音名和别名
            if "_" in note_name:
                name, alias = note_name.split("_")
            else:
                name = note_name
                alias = None

            # 构建文件路径
            file_name = f"tone_{number}_{note_name}.wav"
            url = f"{audio_dir}/{file_name}"

            # 创建Pitch实例
            pitch = Pitch(
                pitch_number=number,
                name=name,
                alias=alias,
                url=url,
            )
            db.add(pitch)

        db.commit()
        print("Successfully initialized pitch data")

    except Exception as e:
        db.rollback()
        print(f"Error initializing pitch data: {str(e)}")
        raise


def init_intervals(db: Session):
    """初始化音程数据"""
    try:
        # type
        init_interval_type(db)
        init_concordance_type(db)

        intervals = db.query(PitchInterval).all()
        if intervals:
            logger.info("PitchInterval already initialized, skipping...")
            return
        type_datas = db.query(PitchIntervalType).all()
        single_id: int = None;
        double_id: int = None;
        for type in type_datas:
            if type.name == "单音程":
                single_id = type.id
            elif type.name == "复音程":
                double_id = type.id


        #
        interval_single = {
            1: "小二度",
            2: "大二度",
            3: "小三度",
            4: "大三度",
            5: "纯四度",
            6: "增四度",
            7: "减五度",
            8: "纯五度",
            9: "小六度",
            10: "大六度",
            11: "小七度",
            12: "大七度",
            13: "纯八度",
        }

        interval_double = {
            14: "小九度",
            15: "大九度",
            16: "小十度",
            17: "大十度",
            18: "纯十一度",
            19: "增十一度",
            20: "减十二度",
            21: "纯十二度",
            22: "小十三度",
            23: "大十三度",
            24: "小十四度",
            25: "大十四度",
            26: "纯十五度"
        }

        # 音程与半音数的映射
        interval_semitones = [
            # 单音程
            1,  # 小二度
            2,  # 大二度
            3,  # 小三度
            4,  # 大三度
            5,  # 纯四度
            6,  # 增四度/减五度
            6,
            7,  # 纯五度
            8,  # 小六度
            9,  # 大六度
            10,  # 小七度
            11,  # 大七度
            12,  # 纯八度
            # 复音程
            13,  # 小九度
            14,  # 大九度
            15,  # 小十度
            16,  # 大十度
            17,  # 纯十一度
            18,  # 增十一度/减十二
            18,
            19,  # 纯十二度
            20,  # 小十三度
            21,  # 大十三度
            22,  # 小十四度
            23,  # 大十四度
            24,  # 纯十五度
        ]

        ii = 0
        for index, (key, value) in enumerate(interval_single.items()):
            ii += 1
            pitch_interval = PitchInterval(
                id=key,
                name=value,
                semitone_number=interval_semitones[index],
                type_id=single_id,
                black=True if interval_semitones[index] == 6 else False,
            )
            db.add(pitch_interval)

        for index, (key, value) in enumerate(interval_double.items()):
            pitch_interval = PitchInterval(
                id=key,
                name=value,
                semitone_number=interval_semitones[index+ii],
                type_id=double_id,
                black=True if interval_semitones[index+ii] == 18 else False,
            )
            db.add(pitch_interval)

        db.commit()
        print("Successfully initialized pitch data")

    except Exception as e:
        db.rollback()
        print(f"Error initializing pitch data: {str(e)}")
        raise

def init_interval_type(db: Session):
    types = db.query(PitchIntervalType).all()
    if types:
        logger.info("PitchIntervalType already initialized, skipping...")
        return

    types_data = {1: "单音程", 2: "复音程"}
    for key, value in types_data.items():
        type = PitchIntervalType(
            id=key,
            name=value,
        )
        db.add(type)

    db.commit()

def init_concordance_type(db: Session):
    types = db.query(PitchConcordanceType).all()
    if types:
        logger.info("PitchConcordanceType already initialized, skipping...")
        return

    types_data = {1: "协和", 2: "不完全协和", 3: "不协和"}
    for key, value in types_data.items():
        type = PitchConcordanceType(
            id=key,
            name=value,
        )
        db.add(type)

    db.commit()