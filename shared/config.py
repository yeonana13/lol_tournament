import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Config:
    # 디스코드 봇 설정
    DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    
    # 데이터베이스 설정
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'lol_tournament')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    
    # Flask 설정
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # 세션 설정
    SECRET_KEY = os.getenv('SECRET_KEY', 'nabi-tournament-secret-key')
    
    # 챔피언 이미지 CDN
    CHAMPION_IMAGE_CDN = "https://ddragon.leagueoflegends.com/cdn/14.1.1/img/champion/"

    # 서버 호스트 설정
    SERVER_HOST = os.getenv('SERVER_HOST', 'localhost')
    
    @classmethod
    def get_base_url(cls):
        """기본 URL 반환"""
        if cls.SERVER_HOST == 'localhost':
            return f"http://localhost:{cls.FLASK_PORT}"
        else:
            return f"http://{cls.SERVER_HOST}:{cls.FLASK_PORT}"
