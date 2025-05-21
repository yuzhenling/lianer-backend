from typing import Optional, Dict, List
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.vip import Vip, VipLevel
from app.core.logger import logger


class VipService:
    _instance = None
    _vip_cache: Dict[int, Vip] = {}  # ID -> Vip对象的缓存
    _vip_level_cache: Dict[VipLevel, Vip] = {}  # VipLevel -> Vip对象的缓存

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VipService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # 单例模式，避免重复初始化
        if not hasattr(self, '_initialized'):
            self._initialized = True

    async def load_vip_cache(self, db: Session) -> None:
        """从数据库加载所有VIP数据到缓存"""
        try:
            vips = await db.query(Vip).all()
            # 清空现有缓存
            self._vip_cache.clear()
            self._vip_level_cache.clear()
            
            # 更新缓存
            for vip in vips:
                self._vip_cache[vip.id] = vip
                self._vip_level_cache[vip.level] = vip

            logger.info(f"Successfully loaded {len(vips)} VIP levels into cache")
        except Exception as e:
            logger.error("Failed to load VIP cache", exc_info=True)
            raise e

    def get_vip_by_id(self, vip_id: int) -> Optional[Vip]:
        """通过ID获取VIP信息（从缓存）"""
        return self._vip_cache.get(vip_id)

    def get_vip_by_level(self, vip_level: VipLevel) -> Optional[Vip]:
        """通过等级获取VIP信息（从缓存）"""
        return self._vip_level_cache.get(vip_level)

    async def get_all_vips(self) -> List[Vip]:
        """获取所有VIP信息（从缓存）"""
        if not self._vip_cache:
            db = await get_db()
            logger.info("Initializing database data during get_all_vips...")
            await self.load_vip_cache(db)
        return list(self._vip_cache.values())

    async def contains_vip(self, vip_ip: int) -> bool:
        if not self._vip_cache:
            db = await get_db()
            logger.info("Initializing database data during get_all_vips...")
            await self.load_vip_cache(db)

        if self._vip_cache[vip_ip]:
            return True
        return False

    async def create_vip(self, db: Session, vip_level: VipLevel, vip_describe: str, vip_price: float, vip_discount: float) -> Optional[Vip]:
        """创建新的VIP等级"""
        try:
            # 检查是否已存在
            if vip_level in self._vip_level_cache:
                logger.error(f"VIP level {vip_level} already exists")
                return None


            # 创建新VIP
            vip = Vip(
                level=vip_level,
                describe=vip_describe,
                price=vip_price,
                discount=vip_discount
            )
            db.add(vip)
            await db.commit()
            await db.refresh(vip)

            # 更新缓存
            self._vip_cache[vip.id] = vip
            self._vip_level_cache[vip_level] = vip

            logger.info(f"Successfully created VIP level: {vip_level}")
            return vip

        except Exception as e:
            logger.error(f"Failed to create VIP level: {str(e)}", exc_info=True)
            await db.rollback()
            return None

    async def update_vip(
        self, 
        db: Session, 
        vip_id: int, 
        update_data: dict
    ) -> Optional[Vip]:
        """更新VIP信息"""
        try:
            vip = await db.query(Vip).filter(Vip.id == vip_id).first()
            if not vip:
                logger.error(f"VIP id {vip_id} not found")
                return None

            # 更新描述
            vip.describe = update_data.get("describe")
            vip.price = update_data.get("price")
            vip.discount = update_data.get("discount")
            db.add(vip)
            await db.commit()
            await db.refresh(vip)

            # 更新缓存
            self._vip_cache[vip.id] = vip
            self._vip_level_cache[vip.level] = vip

            logger.info(f"Successfully updated VIP id: {vip_id}")
            return vip

        except Exception as e:
            logger.error(f"Failed to update VIP: {str(e)}", exc_info=True)
            await db.rollback()
            return None

    async def delete_vip(self, db: Session, vip_id: int) -> bool:
        """删除VIP等级"""
        try:
            vip = await db.query(Vip).filter(Vip.id == vip_id).first()
            if not vip:
                logger.error(f"VIP id {vip_id} not found")
                return False

            # 从数据库删除
            await db.delete(vip)
            await db.commit()

            # 从缓存中删除
            self._vip_cache.pop(vip.id, None)
            self._vip_level_cache.pop(vip.level, None)

            logger.info(f"Successfully deleted VIP id: {vip_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete VIP: {str(e)}", exc_info=True)
            await db.rollback()
            return False

    def refresh_cache(self, db: Session) -> bool:
        """手动刷新VIP缓存"""
        try:
            self.load_vip_cache(db)
            return True
        except Exception:
            return False

    def getDaysByLevel(self, vip_level: VipLevel) -> int:
        if vip_level == VipLevel.FREE:
            return 0
        if vip_level == VipLevel.NORMAL:
            return 0
        if vip_level == VipLevel.HALF_YEAR:
            return 183
        if vip_level == VipLevel.ONE_YEAR:
            return 365

    def getDaysById(self, id: int) -> int:
        vip = self._vip_cache.get(id, None)
        if vip:
            return self.getDaysByLevel(vip.level)
        return 0

# 创建全局VIP服务实例
vip_service = VipService()


