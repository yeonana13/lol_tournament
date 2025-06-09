"""나비 내전 봇 테스트"""
from bot.config import Config

def test_bot_config():
    print("🦋" + "="*50)
    print("🦋 나비 내전 봇 설정 확인")
    print("🦋" + "="*50)
    print(f"봇 토큰: {'설정됨' if Config.DISCORD_BOT_TOKEN else '❌ 없음'}")
    print(f"길드 ID: {Config.GUILD_ID}")
    print(f"내전 채널 수: {len(Config.VOICE_CHANNELS)}")
    print(f"웹 서버: {Config.FLASK_HOST}:{Config.FLASK_PORT}")
    print("🦋" + "="*50)
    
    if Config.DISCORD_BOT_TOKEN:
        print("✅ 봇 설정 완료!")
        print("🦋 봇 실행 명령어: python bot/main.py")
        return True
    else:
        print("❌ 봇 토큰이 설정되지 않았습니다.")
        return False

if __name__ == "__main__":
    test_bot_config()
