#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from shared.config import Config
from shared.database import Database
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import uuid
from datetime import datetime

# OAuth 관련 import
from web.auth.discord_oauth import DiscordOAuth

# Flask 앱 초기화
app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False

socketio = SocketIO(app, cors_allowed_origins="*")

# OAuth 초기화
discord_oauth = DiscordOAuth()

# 게임 세션 저장소
game_sessions = {}
game_states = {}

@app.route('/')
def index():
    """메인 페이지"""
    user = session.get('user')
    return render_template('index.html', user=user)

@app.route('/hello')
def hello():
    return "Hello! 라우트가 작동합니다!"

@app.route('/draft-test')
def draft_test_simple():
    return f"<h1>드래프트 테스트</h1><p>현재 시간: {datetime.now()}</p>"


@app.route('/draft/<session_id>')
def draft_page(session_id):
    """밴픽 드래프트 페이지"""
    user = session.get('user')
    
    if not user:
        return redirect(url_for('discord_login', next=request.url))
    
    print(f"✅ 드래프트 페이지 접근: {user.get('display_name', 'Unknown')} -> {session_id}")
    return render_template('draft.html', 
                         session_id=session_id, 
                         user_info=user)

@app.route('/test/draft')
def test_draft():
    """테스트용 드래프트 페이지"""
    user = session.get('user')
    
    if not user:
        return redirect(url_for('discord_login', next=request.url))
    
    import time
    test_session_id = f"test_{int(time.time())}"
    print(f"🧪 테스트 드래프트: {user.get('display_name', 'Unknown')} -> {test_session_id}")
    
    return render_template('draft.html', 
                         session_id=test_session_id, 
                         user_info=user)
@app.route('/banpick/<session_id>')
def banpick(session_id):
    """밴픽 페이지 - OAuth 로그인 필요"""
    user = session.get('user')
    
    if not user:
        print(f"🔒 로그인되지 않은 접근: {session_id}")
        # 로그인 페이지로 리디렉트
        return redirect(url_for('discord_login', next=request.url))
    
    print(f"✅ 로그인된 사용자 접근: {user['display_name']} -> {session_id}")
    return render_template('banpick.html', 
                         session_id=session_id, 
                         user_info=user)

@app.route('/auth/discord')
def discord_login():
    """디스코드 로그인 시작"""
    next_url = request.args.get('next', '/')
    session['next_url'] = next_url
    print(f"🎮 Discord 로그인 시작, 리턴 URL: {next_url}")
    
    auth_url = discord_oauth.get_authorization_url()
    return redirect(auth_url)

@app.route('/auth/discord/callback')
def discord_callback():
    """디스코드 OAuth 콜백"""
    try:
        code = request.args.get('code')
        state = request.args.get('state')
        error = request.args.get('error')
        
        print(f"📥 OAuth 콜백: code={bool(code)}, state={bool(state)}, error={error}")
        
        if error:
            print(f"❌ OAuth 오류: {error}")
            return f"OAuth 오류: {error}", 400
        
        if not code:
            print("❌ 인증 코드 없음")
            return "인증 코드가 없습니다.", 400
        
        # 토큰 및 사용자 정보 획득
        print("🔄 토큰 교환 중...")
        token_data = discord_oauth.get_access_token(code, state)
        
        print("🔄 사용자 정보 가져오는 중...")
        user_info = discord_oauth.get_user_info(token_data['access_token'])
        
        # 세션에 저장
        session['user'] = user_info
        session['access_token'] = token_data['access_token']
        
        print(f"✅ 로그인 성공: {user_info['display_name']}")
        
        # 원래 페이지로 리디렉트
        next_url = session.pop('next_url', '/')
        print(f"🔄 리디렉트: {next_url}")
        return redirect(next_url)
        
    except Exception as e:
        print(f"❌ 로그인 실패: {str(e)}")
        return f"로그인 실패: {str(e)}", 500

@app.route('/auth/logout')
def logout():
    """로그아웃"""
    user = session.get('user', {})
    print(f"👋 로그아웃: {user.get('display_name', 'Unknown')}")
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/user')
def get_current_user():
    """현재 사용자 정보"""
    user = session.get('user')
    if user:
        return jsonify(user)
    else:
        return jsonify({'error': 'Not authenticated'}), 401

@app.route('/api/session/<session_id>')
def get_session(session_id):
    """세션 정보 조회"""
    db = Database()
    
    # 챔피언 데이터 조회
    champions = db.fetch_all("SELECT * FROM champions ORDER BY english_name")
    
    return jsonify({
        'session_id': session_id,
        'champions': champions,
        'status': 'active'
    })

@socketio.on('connect')
def on_connect():
    print(f"🔌 클라이언트 연결: {request.sid}")

@socketio.on('disconnect')
def on_disconnect():
    print(f"🔌 클라이언트 연결 해제: {request.sid}")

@socketio.on('join_session')
def on_join_session(data):
    session_id = data['session_id']
    join_room(session_id)
    
    # 게임 상태 초기화 (없을 경우)
    if session_id not in game_states:
        game_states[session_id] = {
            'phase': 'position_select',
            'teams': {
                'blue': {'TOP': None, 'JUG': None, 'MID': None, 'ADC': None, 'SUP': None},
                'red': {'TOP': None, 'JUG': None, 'MID': None, 'ADC': None, 'SUP': None}
            },
            'draft': {
                'bans': {'blue': [], 'red': []},
                'picks': {'blue': [], 'red': []},
                'currentTurn': 'blue_ban_1',
                'timer': 30
            }
        }
    
    emit('game_state_update', {'game_state': game_states[session_id]})
    print(f"🎮 세션 참가: {session_id}")

@socketio.on('select_position')
def on_select_position(data):
    session_id = data['session_id']
    team = data['team']
    position = data['position']
    user_name = data['user_name']
    
    if session_id in game_states:
        # 먼저 해당 사용자가 다른 포지션에 있는지 확인하고 제거
        for t in ['blue', 'red']:
            for p in ['TOP', 'JUG', 'MID', 'ADC', 'SUP']:
                if game_states[session_id]['teams'][t][p] == user_name:
                    game_states[session_id]['teams'][t][p] = None
                    print(f"🗑️ 기존 포지션 제거: {user_name} from {t} {p}")
                    
                    # 기존 포지션 제거 알림
                    emit('position_selected', {
                        'team': t,
                        'position': p,
                        'user_name': None
                    }, room=session_id)
        
        # 새 포지션이 비어있는지 확인 후 할당
        if game_states[session_id]['teams'][team][position] is None:
            game_states[session_id]['teams'][team][position] = user_name
            
            # 새 포지션 할당 알림
            emit('position_selected', {
                'team': team,
                'position': position,
                'user_name': user_name
            }, room=session_id)
            
            print(f"✅ 포지션 선택: {user_name} -> {team} {position}")
        else:
            print(f"❌ 포지션 이미 선택됨: {team} {position}")

@socketio.on('leave_position')
def on_leave_position(data):
    session_id = data['session_id']
    team = data['team']
    position = data['position']
    
    if session_id in game_states:
        game_states[session_id]['teams'][team][position] = None
        
        emit('position_selected', {
            'team': team,
            'position': position,
            'user_name': None
        }, room=session_id)
        
        print(f"🚪 포지션 나가기: {team} {position}")

@socketio.on('start_draft')
def on_start_draft(data):
    session_id = data['session_id']
    
    if session_id in game_states:
        game_states[session_id]['phase'] = 'draft'
        
        emit('game_state_update', {'game_state': game_states[session_id]}, room=session_id)
        print(f"🚀 드래프트 시작: {session_id}")

@socketio.on('select_champion')
def on_select_champion(data):
    session_id = data['session_id']
    champion = data['champion']
    action = data['action']
    
    if session_id in game_states:
        draft_state = game_states[session_id]['draft']
        current_turn = draft_state['currentTurn']
        
        # 현재 턴에 따라 밴/픽 처리
        if 'blue' in current_turn and action == 'ban':
            draft_state['bans']['blue'].append(champion)
        elif 'red' in current_turn and action == 'ban':
            draft_state['bans']['red'].append(champion)
        elif 'blue' in current_turn and action == 'pick':
            draft_state['picks']['blue'].append(champion)
        elif 'red' in current_turn and action == 'pick':
            draft_state['picks']['red'].append(champion)
        
        # 다음 턴으로 넘어가기
        draft_state['currentTurn'] = get_next_turn(current_turn)
        draft_state['timer'] = 30  # 타이머 리셋
        
        emit('draft_update', {'draft_state': draft_state}, room=session_id)
        print(f"🎮 챔피언 {action}: {champion}")

def get_next_turn(current_turn):
    """다음 턴 계산"""
    turn_order = [
        'blue_ban_1', 'red_ban_1', 'red_ban_2', 'blue_ban_2',
        'blue_pick_1', 'red_pick_1', 'red_pick_2', 'blue_pick_2',
        'blue_ban_3', 'red_ban_3', 'red_ban_4', 'blue_ban_4',
        'red_pick_3', 'blue_pick_3', 'blue_pick_4', 'red_pick_4',
        'red_pick_5', 'blue_pick_5', 'completed'
    ]
    
    try:
        current_index = turn_order.index(current_turn)
        next_index = min(current_index + 1, len(turn_order) - 1)
        return turn_order[next_index]
    except ValueError:
        return 'completed'

def main():
    """웹서버 실행"""
    print("🦋 나비 내전 웹 서버 시작 (OAuth 적용)...")
    print(f"🔑 Discord OAuth 설정:")
    print(f"   Client ID: {discord_oauth.client_id}")
    print(f"   Redirect URI: {discord_oauth.redirect_uri}")
    
    try:
        socketio.run(
            app, 
            host=Config.FLASK_HOST, 
            port=Config.FLASK_PORT, 
            debug=Config.FLASK_DEBUG
        )
    except Exception as e:
        print(f"❌ 웹서버 실행 실패: {e}")

if __name__ == "__main__":
    main()

@app.route('/draft/<session_id>')
def draft_page(session_id):
    """밴픽 드래프트 페이지"""
    user = session.get('user')
    
    if not user:
        return redirect(url_for('discord_login', next=request.url))
    
    return render_template('draft.html', 
                         session_id=session_id, 
                         user_info=user)

@socketio.on('join_draft')
def on_join_draft(data):
    session_id = data['session_id']
    join_room(f"draft_{session_id}")
    
    # 드래프트 상태 초기화 (필요한 경우)
    if session_id not in game_states:
        game_states[session_id] = {
            'phase': 'draft',
            'currentTurn': 'blue_ban_1',
            'timer': 30,
            'bans': {'blue': [], 'red': []},
            'picks': {'blue': [], 'red': []},
            'teams': {
                'blue': {'TOP': None, 'JUG': None, 'MID': None, 'ADC': None, 'SUP': None},
                'red': {'TOP': None, 'JUG': None, 'MID': None, 'ADC': None, 'SUP': None}
            }
        }
    
    emit('draft_state_update', {'draft_state': game_states[session_id]})
    print(f"🎮 드래프트 참가: {session_id}")

@socketio.on('select_champion')
def on_select_champion(data):
    session_id = data['session_id']
    champion_english = data['champion_english']
    champion_korean = data['champion_korean']
    action = data['action']
    team = data['team']
    
    if session_id in game_states:
        # 밴/픽 데이터 저장
        if action == 'ban':
            game_states[session_id]['bans'][team].append(champion_korean)
        elif action == 'pick':
            game_states[session_id]['picks'][team].append(champion_korean)
        
        # 모든 드래프트 참가자에게 업데이트 전송
        emit('champion_selected', {
            'champion_english': champion_english,
            'champion_korean': champion_korean,
            'action': action,
            'team': team
        }, room=f"draft_{session_id}")
        
        print(f"🎯 챔피언 {action}: {team} - {champion_korean}")

@socketio.on('draft_completed')
def on_draft_completed(data):
    session_id = data['session_id']
    final_state = data['final_state']
    
    if session_id in game_states:
        game_states[session_id] = final_state
        
        # 디스코드로 결과 전송 (추후 구현)
        print(f"🎉 드래프트 완료: {session_id}")
        print(f"   블루팀 밴: {final_state['bans']['blue']}")
        print(f"   레드팀 밴: {final_state['bans']['red']}")
        print(f"   블루팀 픽: {final_state['picks']['blue']}")
        print(f"   레드팀 픽: {final_state['picks']['red']}")

@app.route('/test/draft')
def test_draft():
    """테스트용 드래프트 페이지"""
    user = session.get('user')
    
    if not user:
        return redirect(url_for('discord_login', next=request.url))
    
    # 테스트용 세션 ID 생성
    test_session_id = f"test_{int(datetime.now().timestamp())}"
    
    return render_template('draft.html', 
                         session_id=test_session_id, 
                         user_info=user)

# 드래프트 소켓 이벤트들
@socketio.on('join_draft')
def on_join_draft(data):
    session_id = data['session_id']
    join_room(f"draft_{session_id}")
    
    print(f"🎮 드래프트 참가: {session_id}")
    emit('draft_joined', {'session_id': session_id})

@socketio.on('select_champion')
def on_select_champion_draft(data):
    session_id = data['session_id']
    champion_english = data['champion_english']
    champion_korean = data['champion_korean']
    action = data['action']
    team = data['team']
    turn = data['turn']
    
    # 모든 드래프트 참가자에게 선택 알림
    emit('champion_selected', {
        'champion_english': champion_english,
        'champion_korean': champion_korean,
        'action': action,
        'team': team,
        'turn': turn
    }, room=f"draft_{session_id}")
    
    print(f"🎯 드래프트 - {action}: {team} {champion_korean}")
