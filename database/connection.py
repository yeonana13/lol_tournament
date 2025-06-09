"""나비 내전 데이터베이스 연결"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from bot.config import Config
from database.models import Base
import pymysql

pymysql.install_as_MySQLdb()

# 간단한 연결 설정 (SSL 없이)
connect_args = {
    "charset": "utf8mb4",
    "use_unicode": True,
    "autocommit": False
}

engine = create_engine(
    Config.get_database_url(),
    echo=True,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
        print("🦋 나비 내전 데이터베이스 테이블이 성공적으로 생성되었습니다!")
    except Exception as e:
        print(f"❌ 테이블 생성 중 오류 발생: {e}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    try:
        with engine.connect() as connection:
            # SQLAlchemy 2.0 방식으로 수정
            result = connection.execute(text("SELECT 1"))
            row = result.fetchone()
            print("🦋 나비 내전 MySQL 데이터베이스 연결 성공!")
            print(f"🦋 테스트 쿼리 결과: {row[0]}")
            return True
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")
        return False
