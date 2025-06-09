"""나비 내전 데이터베이스 연결 테스트"""
from database.connection import test_connection, create_tables
from bot.config import Config

def main():
    print("🦋" + "="*50)
    print("🦋 나비 내전 전적 시스템 - 데이터베이스 설정 확인")
    print("🦋" + "="*50)
    print(f"HOST: {Config.DB_HOST}")
    print(f"PORT: {Config.DB_PORT}")
    print(f"DATABASE: {Config.DB_NAME}")
    print(f"USER: {Config.DB_USER}")
    print("🦋" + "-"*50)
    
    if test_connection():
        print("✅ 데이터베이스 연결 성공!")
        print("📊 테이블 생성 시도...")
        create_tables()
        print("🎉 1단계 완료! 나비 내전 시스템 준비됨!")
        
        # MySQL CLI 명령어 안내
        print("\n🦋" + "="*50)
        print("💡 MySQL 직접 접속 명령어:")
        print(f"mysql -h {Config.DB_HOST} -u {Config.DB_USER} -p")
        print("패스워드 입력 후 다음 명령어로 확인:")
        print("USE lol_tournament;")
        print("SHOW TABLES;")
        print("🦋" + "="*50)
    else:
        print("❌ 연결 실패. 설정을 확인해주세요.")

if __name__ == "__main__":
    main()
