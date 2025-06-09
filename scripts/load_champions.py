#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
챔피언 데이터를 CSV에서 읽어 데이터베이스에 로드하는 스크립트 (수정된 테이블 구조용)
"""

import sys
import os
import csv
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
    print("💡 shared 모듈들이 있는지 확인해주세요.")
    sys.exit(1)

def load_champions_from_csv():
    """CSV 파일에서 챔피언 데이터를 읽어 데이터베이스에 저장"""
    
    # CSV 파일 경로 확인
    csv_path = project_root / 'name.csv'
    if not csv_path.exists():
        print(f"❌ CSV 파일을 찾을 수 없습니다: {csv_path}")
        print("💡 name.csv 파일을 프로젝트 루트에 업로드해주세요.")
        return False
    
    try:
        print(f"📁 CSV 파일 로드 중: {csv_path}")
        
        # CSV 파일 읽기 (한글 인코딩 처리)
        champions_data = []
        encodings = ['utf-8', 'cp949', 'euc-kr']
        
        for encoding in encodings:
            try:
                with open(csv_path, 'r', encoding=encoding) as file:
                    reader = csv.reader(file)
                    champions_data = list(reader)
                    break
            except UnicodeDecodeError:
                continue
        
        if not champions_data:
            print("❌ CSV 파일을 읽을 수 없습니다.")
            return False
        
        # 헤더와 데이터 분리
        headers = champions_data[0] if champions_data else []
        data_rows = champions_data[1:] if len(champions_data) > 1 else []
        
        print(f"📊 총 {len(data_rows)}개의 챔피언 데이터 발견")
        print(f"🔍 컬럼: {headers}")
        
        # 데이터베이스 연결
        db = Database()
        
        # 기존 챔피언 데이터 삭제 (선택적)
        print("🗑️ 기존 챔피언 데이터 정리 중...")
        db.execute_query("DELETE FROM champions")
        
        # 챔피언 데이터 삽입
        success_count = 0
        error_count = 0
        
        for index, row in enumerate(data_rows):
            try:
                # 첫 번째 컬럼을 영어명, 두 번째 컬럼을 한글명으로 가정
                english_name = row[0].strip() if len(row) > 0 else f"Champion_{index}"
                korean_name = row[1].strip() if len(row) > 1 else english_name
                
                # 이미지 URL (Riot Games CDN 사용)
                champion_key = english_name.lower().replace(' ', '').replace("'", "").replace('.', '')
                image_url = f"https://ddragon.leagueoflegends.com/cdn/14.1.1/img/champion/{champion_key.capitalize()}.png"
                
                # 챔피언 데이터 삽입 (수정된 컬럼명 사용)
                query = """
                INSERT INTO champions (english_name, korean_name, image_url) 
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                korean_name = VALUES(korean_name),
                image_url = VALUES(image_url)
                """
                
                db.execute_query(query, (english_name, korean_name, image_url))
                success_count += 1
                
            except Exception as e:
                print(f"❌ 챔피언 데이터 삽입 실패 [{index}]: {e}")
                error_count += 1
                continue
        
        print(f"✅ 챔피언 데이터 로드 완료!")
        print(f"   - 성공: {success_count}개")
        print(f"   - 실패: {error_count}개")
        
        return success_count > 0
        
    except Exception as e:
        print(f"❌ CSV 파일 처리 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    print("🦋 챔피언 데이터 로더 시작 (수정된 구조)")
    print("=" * 50)
    
    if load_champions_from_csv():
        print("🎉 챔피언 데이터 로드 성공!")
    else:
        print("💥 챔피언 데이터 로드 실패!")
        sys.exit(1)

if __name__ == "__main__":
    main()
