"""닉네임 파싱 유틸리티"""
from shared.constants import TIER_ORDER, TIER_NAMES

def parse_tier_from_nickname(nickname: str) -> str:
    """닉네임에서 티어 정보 추출"""
    try:
        tier_part = nickname.split('/')[1].lower()
        if tier_part.startswith('gm'):
            return 'gm'
        tier = tier_part[0].lower()
        if tier in TIER_ORDER:
            return tier
        else:
            return 'unknown'
    except (IndexError, AttributeError):
        return 'unknown'

def get_tier_sort_key(nickname: str) -> int:
    """티어 정렬을 위한 키 반환"""
    tier = parse_tier_from_nickname(nickname)
    return TIER_ORDER.get(tier, float('inf'))

def get_tier_display_name(tier: str) -> str:
    """티어 약자를 전체 이름으로 변환"""
    return TIER_NAMES.get(tier.lower(), '알 수 없음')

def validate_tier(tier: str) -> bool:
    """유효한 티어인지 확인"""
    return tier.lower() in TIER_ORDER
