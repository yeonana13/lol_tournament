"""나비 내전 시스템 공통 상수"""

# 참가자 관련 상수
MAX_PARTICIPANTS = 10

# 티어 순서 (높은 티어부터 낮은 순서)
TIER_ORDER = {
    'c': 1,   # 챌린저
    'gm': 2,  # 그랜드마스터  
    'm': 3,   # 마스터
    'd': 4,   # 다이아몬드
    'e': 5,   # 에메랄드
    'p': 6,   # 플래티넘
    'g': 7,   # 골드
    's': 8,   # 실버
    'b': 9,   # 브론즈
    'i': 10   # 아이언
}

# 티어 전체 이름 매핑
TIER_NAMES = {
    'c': '챌린저',
    'gm': '그랜드마스터',
    'm': '마스터',
    'd': '다이아몬드',
    'e': '에메랄드',
    'p': '플래티넘',
    'g': '골드',
    's': '실버',
    'b': '브론즈',
    'i': '아이언'
}

# 게임 관련 상수
POSITIONS = ['TOP', 'JUG', 'MID', 'ADC', 'SUP']
TEAMS = ['BLUE', 'RED']

# 밴픽 관련 상수
DRAFT_PHASES = {
    'BAN_PHASE_1': {'bans_per_team': 3, 'order': ['BLUE', 'RED'] * 3},
    'PICK_PHASE_1': {'picks': 3, 'order': ['BLUE', 'RED', 'RED', 'BLUE', 'BLUE', 'RED']},
    'BAN_PHASE_2': {'bans_per_team': 2, 'order': ['BLUE', 'RED'] * 2},
    'PICK_PHASE_2': {'picks': 2, 'order': ['RED', 'BLUE', 'BLUE', 'RED']}
}

# 나비 서버 메시지 템플릿
RANDOM_MESSAGES = [
    "🦋 랏 {}! 나비 내전하자하자 🎮",
    "🦋 남은 자리 {}명! 얼른 오세요! 🚀",
    "🦋 나비 내전 ㄱㄱㄱㄱ! {}명 남음 제발여! 💪"
]
