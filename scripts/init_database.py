#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
데이터베이스 테이블 초기화 스크립트
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

def create_tables():
    """데이터베이스 테이블들 생성"""
    
    db = Database()
    
    # 테이블 생성 쿼리들
    tables = {
        'champions': """
        CREATE TABLE IF NOT EXISTS champions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            champion_key VARCHAR(50) UNIQUE NOT NULL,
            name_en VARCHAR(100) NOT NULL,
            name_kr VARCHAR(100) NOT NULL,
            image_url VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_champion_key (champion_key),
            INDEX idx_name_en (name_en),
            INDEX idx_name_kr (name_kr)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        'players': """
        CREATE TABLE IF NOT EXISTS players (
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
        CREATE TABLE IF NOT EXISTS game_sessions (
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
        CREATE TABLE IF NOT EXISTS games (
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
        """,
        
        'ban_picks': """
        CREATE TABLE IF NOT EXISTS ban_picks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            game_id INT NOT NULL,
            session_id VARCHAR(50) NOT NULL,
            champion_key VARCHAR(50) NOT NULL,
            team ENUM('blue', 'red') NOT NULL,
            action ENUM('ban', 'pick') NOT NULL,
            position ENUM('TOP', 'JUG', 'MID', 'ADC', 'SUP') NULL,
            order_num INT NOT NULL,
            player_discord_id VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_game_id (game_id),
            INDEX idx_session_id (session_id),
            INDEX idx_champion_key (champion_key),
            FOREIGN KEY (champion_key) REFERENCES champions(champion_key) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        'player_stats': """
        CREATE TABLE IF NOT EXISTS player_stats (
            id INT AUTO_INCREMENT PRIMARY KEY,
            player_discord_id VARCHAR(20) NOT NULL,
            game_id INT NOT NULL,
            champion_key VARCHAR(50) NOT NULL,
            position ENUM('TOP', 'JUG', 'MID', 'ADC', 'SUP') NOT NULL,
            team ENUM('blue', 'red') NOT NULL,
            is_winner BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_player_discord_id (player_discord_id),
            INDEX idx_game_id (game_id),
            INDEX idx_champion_key (champion_key),
            FOREIGN KEY (champion_key) REFERENCES champions(champion_key) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    }
    
    print("🗃️ 데이터베이스 테이블 생성 중...")
    
    for table_name, create_query in tables.items():
        try:
            print(f"   📋 {table_name} 테이블 생성 중...")
            db.execute_query(create_query)
            print(f"   ✅ {table_name} 테이블 생성 완료")
        except Exception as e:
            print(f"   ❌ {table_name} 테이블 생성 실패: {e}")
            return False
    
    print("🎉 모든 테이블 생성 완료!")
    return True

def main():
    """메인 실행 함수"""
    print("🦋 데이터베이스 초기화 시작")
    print("=" * 50)
    
    if create_tables():
        print("✅ 데이터베이스 초기화 성공!")
    else:
        print("❌ 데이터베이스 초기화 실패!")
        sys.exit(1)

if __name__ == "__main__":
    main()
