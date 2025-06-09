import mysql.connector
from mysql.connector import Error
from .config import Config

class Database:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        """데이터베이스 연결"""
        try:
            self.connection = mysql.connector.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci'
            )
            if self.connection.is_connected():
                print(f"✅ 데이터베이스 연결 성공: {Config.DB_HOST}:{Config.DB_PORT}")
                return True
        except Error as e:
            print(f"❌ 데이터베이스 연결 실패: {e}")
            return False
    
    def execute_query(self, query, params=None):
        """쿼리 실행"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            
            if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
                self.connection.commit()
                return cursor.lastrowid
            else:
                return cursor.fetchall()
                
        except Error as e:
            print(f"❌ 쿼리 실행 실패: {e}")
            print(f"   쿼리: {query}")
            if params:
                print(f"   파라미터: {params}")
            return None
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def fetch_one(self, query, params=None):
        """단일 결과 조회"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            result = cursor.fetchone()
            return result
            
        except Error as e:
            print(f"❌ 단일 조회 실패: {e}")
            return None
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def fetch_all(self, query, params=None):
        """전체 결과 조회"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            result = cursor.fetchall()
            return result
            
        except Error as e:
            print(f"❌ 전체 조회 실패: {e}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def close(self):
        """연결 종료"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✅ 데이터베이스 연결 종료")
