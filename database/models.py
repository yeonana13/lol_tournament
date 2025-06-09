"""나비 내전 데이터베이스 모델"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Index, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Player(Base):
    __tablename__ = 'players'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    discord_id = Column(String(50), unique=True, nullable=False, index=True)
    nickname = Column(String(100), nullable=False)
    current_tier = Column(String(20), nullable=True)
    highest_tier = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_game_at = Column(DateTime, nullable=True)
    
    game_participants = relationship("GameParticipant", back_populates="player")
    player_stats = relationship("PlayerStats", back_populates="player", uselist=False)
    
    __table_args__ = (
        Index('idx_discord_id', 'discord_id'),
        Index('idx_nickname', 'nickname'),
        Index('idx_current_tier', 'current_tier'),
        Index('idx_last_game_at', 'last_game_at'),
    )

class Game(Base):
    __tablename__ = 'games'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(100), nullable=False)
    host_discord_id = Column(String(50), nullable=False)
    status = Column(String(20), default='waiting')
    winner_team = Column(String(10), nullable=True)
    game_duration = Column(Integer, nullable=True)
    draft_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    participants = relationship("GameParticipant", back_populates="game")
    
    __table_args__ = (
        Index('idx_session_id', 'session_id'),
        Index('idx_status', 'status'),
        Index('idx_host_discord_id', 'host_discord_id'),
        Index('idx_created_at', 'created_at'),
        Index('idx_completed_at', 'completed_at'),
        Index('idx_winner_team', 'winner_team'),
    )

class GameParticipant(Base):
    __tablename__ = 'game_participants'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(Integer, ForeignKey('games.id', ondelete='CASCADE'), nullable=False)
    player_id = Column(Integer, ForeignKey('players.id', ondelete='CASCADE'), nullable=False)
    team = Column(String(10), nullable=True)
    position = Column(String(10), nullable=True)
    champion = Column(String(50), nullable=True)
    is_winner = Column(Boolean, nullable=True)
    
    game = relationship("Game", back_populates="participants")
    player = relationship("Player", back_populates="game_participants")
    
    __table_args__ = (
        Index('idx_game_id', 'game_id'),
        Index('idx_player_id', 'player_id'),
        Index('idx_team', 'team'),
        Index('idx_position', 'position'),
        Index('idx_champion', 'champion'),
        Index('idx_is_winner', 'is_winner'),
        Index('idx_player_position', 'player_id', 'position'),
        Index('idx_player_champion', 'player_id', 'champion'),
    )

class PlayerStats(Base):
    __tablename__ = 'player_stats'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey('players.id', ondelete='CASCADE'), unique=True, nullable=False)
    
    total_games = Column(Integer, default=0)
    total_wins = Column(Integer, default=0)
    total_losses = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    
    current_streak = Column(Integer, default=0)
    max_win_streak = Column(Integer, default=0)
    max_loss_streak = Column(Integer, default=0)
    
    position_stats = Column(JSON, nullable=True)
    champion_stats = Column(JSON, nullable=True)
    monthly_stats = Column(JSON, nullable=True)
    recent_games = Column(JSON, nullable=True)
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    player = relationship("Player", back_populates="player_stats")
    
    __table_args__ = (
        Index('idx_player_id', 'player_id'),
        Index('idx_win_rate', 'win_rate'),
        Index('idx_total_games', 'total_games'),
    )
