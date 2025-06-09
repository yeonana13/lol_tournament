# 🦋 나비 내전 시스템

나비처럼 아름다운 리그 오브 레전드 내전 시스템입니다.

## 📋 기능

- 🎮 디스코드 봇을 통한 내전 모집
- 🌐 웹 기반 실시간 밴픽 시스템
- 📊 플레이어 전적 관리
- 🏆 랭킹 시스템
- 🦋 나비 테마 UI/UX

## 🚀 설치 및 실행

### 1. 환경 설정
```bash
# 가상환경 활성화
source venv/bin/activate

# 패키지 설치 확인
pip install -r requirements.txt
```

### 2. 챔피언 데이터 로드
```bash
# name.csv 파일이 프로젝트 루트에 있는지 확인
python scripts/load_champions.py
```

### 3. 시스템 테스트
```bash
# 전체 시스템 테스트
python test_complete_system.py
```

### 4. 시스템 실행
```bash
# 통합 실행 (봇 + 웹서버)
python run_nabi_system.py

# 또는 개별 실행
python bot/main.py          # 디스코드 봇
python web/app_enhanced.py  # 웹 서버
```

## 📖 사용법

1. 디스코드에서 `!내전1` ~ `!내전5` 명령어로 내전 모집
2. 10명 모집 완료 시 밴픽 페이지 링크 제공
3. 웹 페이지에서 실시간 밴픽 진행
4. 게임 완료 후 결과 입력

## 🛠️ 주요 명령어

- `!내전1` ~ `!내전5`: 내전 모집 시작
- `!주사위`: 랜덤 주사위
- `!나비`: 시스템 정보

## 📁 프로젝트 구조

```
lol_tournament/
├── bot/                 # 디스코드 봇
├── web/                 # 웹 서버
├── database/            # 데이터베이스
├── shared/              # 공통 모듈
├── scripts/             # 유틸리티 스크립트
└── name.csv            # 챔피언 데이터
```

## 🔧 설정

`.env` 파일에서 다음 설정을 확인하세요:
- `DISCORD_BOT_TOKEN`: 디스코드 봇 토큰
- `DB_HOST`: MySQL 데이터베이스 호스트
- `DB_USER`, `DB_PASSWORD`: 데이터베이스 인증정보

## 🐛 문제 해결

### 챔피언 데이터가 로드되지 않는 경우
```bash
python scripts/load_champions.py
```

### 데이터베이스 연결 오류
```bash
python test_db_connection.py
```

### 웹 서버 접속 불가
- 방화벽에서 5000 포트 확인
- `Config.FLASK_HOST` 설정 확인

## 📝 라이선스

MIT License

## 👥 기여

이슈나 개선사항이 있으시면 언제든 연락주세요! 🦋
