"""나비 내전 봇 설정"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Discord 설정
    DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    GUILD_ID = int(os.getenv('GUILD_ID', 0))
    
    # 음성 채널 설정
    VOICE_CHANNELS = {
        "내전1": int(os.getenv('VOICE_CHANNEL_1')),
        "내전2": int(os.getenv('VOICE_CHANNEL_2')),
        "내전3": int(os.getenv('VOICE_CHANNEL_3')),
        "내전4": int(os.getenv('VOICE_CHANNEL_4')),
        "내전5": int(os.getenv('VOICE_CHANNEL_5'))
    }
    
    # 웹 서버 설정 (AWS EC2용)
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    
    # MySQL 데이터베이스 설정 (SSL 없이)
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_NAME = os.getenv('DB_NAME', 'lol_tournament')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    @classmethod
    def get_database_url(cls):
        if cls.DATABASE_URL:
            return cls.DATABASE_URL
        return f"mysql+pymysql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
