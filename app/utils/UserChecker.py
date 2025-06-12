from sqlalchemy import Boolean

from app.models.user import CombineUser
from app.models.vip import VipLevel


def check_normal_vip_level(combine_user:CombineUser) -> Boolean:
    if combine_user.vip_level == VipLevel.NORMAL:
        return True
    elif combine_user.vip_level == VipLevel.HALF_YEAR:
        return True
    elif combine_user.vip_level == VipLevel.ONE_YEAR:
        return True
    else:
        return False

def check_year_vip_level(combine_user:CombineUser) -> Boolean:
    if combine_user.vip_level == VipLevel.HALF_YEAR:
        return True
    elif combine_user.vip_level == VipLevel.ONE_YEAR:
        return True
    else:
        return False



