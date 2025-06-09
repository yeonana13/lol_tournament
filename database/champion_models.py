"""챔피언 데이터 모델"""
from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Champion(Base):
    __tablename__ = 'champions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    english_name = Column(String(50), unique=True, nullable=False)
    korean_name = Column(String(50), nullable=False)
    image_url = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 인덱스
    __table_args__ = (
        Index('idx_english_name', 'english_name'),
        Index('idx_korean_name', 'korean_name'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'english_name': self.english_name,
            'korean_name': self.korean_name,
            'image_url': self.image_url
        }
