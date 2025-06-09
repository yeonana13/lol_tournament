"""나비 내전 시스템 완전성 테스트"""
import os
import sys
from database.connection import test_connection
from bot.config import Config

def test_files_exist():
    """필수 파일 존재 확인"""
    required_files = [
        'bot/main.py',
        'web/app_enhanced.py',
        'database/models.py',
        'database/champion_models.py',
        'scripts/load_champions.py',
        'name.csv'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    return missing_files

def test_champion_data():
    """챔피언 데이터 확인"""
    try:
        from database.connection import SessionLocal
        from database.champion_models import Champion
        
        db = SessionLocal()
        champion_count = db.query(Champion).count()
        db.close()
        
        return champion_count
    except Exception as e:
        return f"오류: {e}"

def main():
    print("🦋" + "="*60)
    print("🦋 나비 내전 시스템 완전성 테스트")
    print("🦋" + "="*60)
    
    # 1. 필수 파일 확인
    print("1. 필수 파일 확인...")
    missing_files = test_files_exist()
    if missing_files:
        print(f"❌ 누락된 파일들: {missing_files}")
        return False
    else:
        print("✅ 모든 필수 파일 존재")
    
    # 2. 데이터베이스 연결 확인
    print("\n2. 데이터베이스 연결 확인...")
    if test_connection():
        print("✅ 데이터베이스 연결 성공")
    else:
        print("❌ 데이터베이스 연결 실패")
        return False
    
    # 3. 봇 설정 확인
    print("\n3. 봇 설정 확인...")
    if Config.DISCORD_BOT_TOKEN:
        print("✅ 디스코드 봇 토큰 설정됨")
    else:
        print("❌ 디스코드 봇 토큰 없음")
        return False
    
    # 4. 챔피언 데이터 확인
    print("\n4. 챔피언 데이터 확인...")
    champion_count = test_champion_data()
    if isinstance(champion_count, int):
        if champion_count > 0:
            print(f"✅ 챔피언 데이터: {champion_count}개")
        else:
            print("⚠️ 챔피언 데이터가 비어있습니다. scripts/load_champions.py를 실행하세요.")
    else:
        print(f"❌ 챔피언 데이터 확인 실패: {champion_count}")
    
    print("\n🦋" + "="*60)
    print("🦋 시스템 준비 완료! 실행 명령어:")
    print("🦋 python run_nabi_system.py")
    print("🦋" + "="*60)
    
    return True

if __name__ == "__main__":
    main()
