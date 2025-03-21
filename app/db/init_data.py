from sqlalchemy.orm import Session

from app.core.logger import logger
from app.models.vip import Vip, VipLevel


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