#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
데이터베이스 테이블 구조 수정 스크립트
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from shared.config import Config
    from shared.database import Database
    print("🦋 모듈 임포트 성공!")
except ImportError as e:
    print(f"❌ 모듈 임포트 실패: {e}")
    sys.exit(1)

def fix_tables():
    """기존 코드에 맞게 테이블 구조 수정"""
    
    db = Database()
    
    print("🗑️ 기존 테이블 삭제 중...")
    
    # 기존 테이블들 삭제 (외래키 때문에 순서 중요)
    drop_tables = [
        "DROP TABLE IF EXISTS player_stats",
        "DROP TABLE IF EXISTS ban_picks", 
        "DROP TABLE IF EXISTS games",
        "DROP TABLE IF EXISTS game_sessions",
        "DROP TABLE IF EXISTS players",
        "DROP TABLE IF EXISTS champions"
    ]
    
    for drop_query in drop_tables:
        try:
            db.execute_query(drop_query)
            print(f"   ✅ {drop_query.split()[-1]} 삭제 완료")
        except Exception as e:
            print(f"   ⚠️ {drop_query.split()[-1]} 삭제 중 오류 (무시): {e}")
    
    print("\n📋 새 테이블 생성 중...")
    
    # 기존 코드에 맞는 테이블 구조로 재생성
    tables = {
        'champions': """
        CREATE TABLE champions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            english_name VARCHAR(100) NOT NULL,
            korean_name VARCHAR(100) NOT NULL,
            image_url VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY unique_english_name (english_name),
            INDEX idx_english_name (english_name),
            INDEX idx_korean_name (korean_name)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        'players': """
        CREATE TABLE players (
            id INT AUTO_INCREMENT PRIMARY KEY,
            discord_id VARCHAR(20) UNIQUE NOT NULL,
            discord_name VARCHAR(100) NOT NULL,
            summoner_name VARCHAR(100),
            wins INT DEFAULT 0,
            losses INT DEFAULT 0,
            rating INT DEFAULT 1000,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_discord_id (discord_id),
            INDEX idx_rating (rating)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        'game_sessions': """
        CREATE TABLE game_sessions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            session_id VARCHAR(50) UNIQUE NOT NULL,
            channel_id VARCHAR(20) NOT NULL,
            status ENUM('recruiting', 'lobby', 'drafting', 'completed', 'cancelled') DEFAULT 'recruiting',
            blue_team JSON,
            red_team JSON,
            ban_pick_data JSON,
            winner_team ENUM('blue', 'red', 'none') DEFAULT 'none',
            game_duration INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_session_id (session_id),
            INDEX idx_channel_id (channel_id),
            INDEX idx_status (status)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        'games': """
        CREATE TABLE games (
            id INT AUTO_INCREMENT PRIMARY KEY,
            session_id VARCHAR(50) NOT NULL,
            blue_team_players JSON NOT NULL,
            red_team_players JSON NOT NULL,
            blue_team_bans JSON,
            red_team_bans JSON,
            blue_team_picks JSON,
            red_team_picks JSON,
            winner_team ENUM('blue', 'red') NOT NULL,
            game_duration INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_session_id (session_id),
            INDEX idx_winner_team (winner_team)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    }
    
    for table_name, create_query in tables.items():
        try:
            print(f"   📋 {table_name} 테이블 생성 중...")
            db.execute_query(create_query)
            print(f"   ✅ {table_name} 테이블 생성 완료")
        except Exception as e:
            print(f"   ❌ {table_name} 테이블 생성 실패: {e}")
            return False
    
    print("🎉 테이블 구조 수정 완료!")
    return True

def main():
    """메인 실행 함수"""
    print("🦋 데이터베이스 구조 수정 시작")
    print("=" * 50)
    
    if fix_tables():
        print("✅ 데이터베이스 구조 수정 성공!")
    else:
        print("❌ 데이터베이스 구조 수정 실패!")
        sys.exit(1)

if __name__ == "__main__":
    main()
