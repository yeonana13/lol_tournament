"""나비 내전 시스템 전체 실행 스크립트"""
import subprocess
import sys
import time
import os
from multiprocessing import Process

def run_bot():
    """디스코드 봇 실행"""
    print("🦋 나비 내전 디스코드 봇 시작...")
    os.system("python bot/main.py")

def run_web_server():
    """웹 서버 실행"""
    print("🦋 나비 내전 웹 서버 시작...")
    os.system("python web/app_enhanced.py")

def main():
    print("🦋" + "="*60)
    print("🦋 나비 내전 시스템 통합 실행")
    print("🦋" + "="*60)
    
    # 챔피언 데이터 로드 확인
    if not os.path.exists("name.csv"):
        print("❌ name.csv 파일이 없습니다. 챔피언 데이터를 먼저 업로드해주세요.")
        return
    
    # 챔피언 데이터 로드
    print("🦋 챔피언 데이터 로딩...")
    try:
        subprocess.run([sys.executable, "scripts/load_champions.py"], check=True)
    except subprocess.CalledProcessError:
        print("❌ 챔피언 데이터 로드 실패")
        return
    
    print("\n🦋 시스템 시작 중...")
    print("🦋 Ctrl+C로 종료할 수 있습니다.")
    print("🦋" + "="*60)
    
    try:
        # 봇과 웹서버를 별도 프로세스로 실행
        bot_process = Process(target=run_bot)
        web_process = Process(target=run_web_server)
        
        bot_process.start()
        time.sleep(2)  # 봇이 먼저 시작되도록 대기
        web_process.start()
        
        print("🦋 디스코드 봇과 웹 서버가 실행되었습니다!")
        print("🦋 디스코드에서 !내전1 명령어로 테스트해보세요!")
        
        # 프로세스 대기
        bot_process.join()
        web_process.join()
        
    except KeyboardInterrupt:
        print("\n🦋 나비 내전 시스템을 종료합니다...")
        bot_process.terminate()
        web_process.terminate()
        bot_process.join()
        web_process.join()
        print("🦋 시스템이 정상적으로 종료되었습니다.")

if __name__ == "__main__":
    main()
