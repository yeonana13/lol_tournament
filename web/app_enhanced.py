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
    return "Hello! 사이버펑크 시스템이 작동합니다!"

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

@app.route('/api/session/create', methods=['POST'])
def create_session():
    """디스코드 봇에서 세션 생성 요청"""
    try:
        data = request.get_json()
        session_id = data['session_id']
        
        # 세션 데이터 저장
        game_sessions[session_id] = {
            'participants': data['participants'],
            'channel_id': data['channel_id'],
            'guild_id': data['guild_id'],
            'created_by': data['created_by'],
            'created_at': data['created_at'],
            'title': data.get('title', '나비내전'),
            'phase': 'lobby'
        }
        
        # 게임 상태 초기화
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
            },
            'participants': data['participants']
        }
        
        print(f"✅ 세션 생성: {session_id} ({len(data['participants'])}명)")
        return jsonify({'success': True, 'session_id': session_id})
    
    except Exception as e:
        print(f"❌ 세션 생성 실패: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/session/<session_id>')
def get_session(session_id):
    """세션 정보 조회"""
    try:
        db = Database()
        champions = db.fetch_all("SELECT * FROM champions ORDER BY english_name")
        
        return jsonify({
            'session_id': session_id,
            'champions': champions,
            'status': 'active'
        })
    except Exception as e:
        # 데이터베이스 연결 실패 시 더미 데이터 반환
        dummy_champions = [
            {
                'english_name': 'Aatrox',
                'korean_name': '아트록스',
                'image_url': 'https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/Aatrox.png'
            },
            {
                'english_name': 'Ahri',
                'korean_name': '아리',
                'image_url': 'https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/Ahri.png'
            }
        ]
        
        return jsonify({
            'session_id': session_id,
            'champions': dummy_champions,
            'status': 'active'
        })

@app.route('/api/session/<session_id>/users')
def get_session_users(session_id):
    """세션의 유저 정보 반환"""
    if session_id not in game_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    session_data = game_sessions[session_id]
    game_state = game_states.get(session_id, {})
    
    return jsonify({
        'participants': session_data['participants'],
        'teams': game_state.get('teams', {}),
        'phase': game_state.get('phase', 'lobby')
    })

@app.route('/cyber_test')
def cyber_test():
    """사이버 테스트 페이지"""
    return '''
    <html>
    <head>
        <title>🤖 사이버펑크 드래프트</title>
        <style>
            body {
                background: linear-gradient(45deg, #000000, #001100);
                color: #00FF88;
                font-family: 'Courier New', monospace;
                padding: 50px;
                text-align: center;
            }
            .matrix {
                border: 2px solid #00FF88;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 0 30px rgba(0,255,136,0.5);
                max-width: 600px;
                margin: 0 auto;
            }
            a {
                color: #00FF88;
                text-decoration: none;
                font-size: 20px;
                border: 1px solid #00FF88;
                padding: 15px 30px;
                display: inline-block;
                margin: 20px;
                transition: all 0.3s;
            }
            a:hover {
                background: #00FF88;
                color: #000000;
                box-shadow: 0 0 20px #00FF88;
            }
        </style>
    </head>
    <body>
        <div class="matrix">
            <h1>🤖 CYBER DRAFT SYSTEM</h1>
            <p>>>> ACCESSING MAINFRAME <<<</p>
            <p>>>> LOADING NEURAL INTERFACE <<<</p>
            <a href="/draft_cyber/cyber_test_123">🚀 ENTER THE MATRIX</a>
        </div>
    </body>
    </html>
    '''

@app.route('/draft_cyber/<session_id>')
def draft_cyber_page(session_id):
    """사이버펑크 드래프트 페이지"""
    user = session.get('user')
    
    if not user:
        return redirect(url_for('discord_login', next=request.url))
    
    # 세션 데이터가 없으면 테스트용 더미 데이터 생성
    if session_id not in game_sessions:
        print(f"🧪 사이버 테스트용 세션 데이터 생성: {session_id}")
        
        # 현재 로그인된 유저 정보
        current_user_info = {
            'discord_id': user.get('id', 'current_user'),
            'username': user.get('username', 'CurrentUser'),
            'display_name': user.get('display_name', 'Current User'),
            'avatar_url': user.get('avatar_url', 'https://cdn.discordapp.com/embed/avatars/0.png'),
            'discriminator': user.get('discriminator', '0000')
        }
        
        # 더미 참가자 데이터 (10명)
        dummy_participants = [current_user_info]
        for i in range(1, 10):
            dummy_participants.append({
                'discord_id': f'cyber_{i}',
                'username': f'CyberUser{i}',
                'display_name': f'사이버유저{i}',
                'avatar_url': f'https://cdn.discordapp.com/embed/avatars/{i % 6}.png',
                'discriminator': f'{2000 + i:04d}'
            })
        
        # 세션 데이터 저장
        game_sessions[session_id] = {
            'participants': dummy_participants,
            'channel_id': 'cyber_channel',
            'guild_id': 'cyber_guild',
            'created_by': current_user_info,
            'created_at': datetime.now().isoformat(),
            'title': '🤖 사이버 나비내전',
            'phase': 'draft'
        }
        
        # 게임 상태 초기화
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
            },
            'participants': dummy_participants
        }
    
    print(f"✅ 사이버 드래프트 접근: {user.get('display_name', 'Unknown')} -> {session_id}")
    return render_template('draft_cyber.html', session_id=session_id, user_info=user)

# 웹소켓 이벤트
@socketio.on('connect')
def on_connect():
    print(f"🔌 클라이언트 연결: {request.sid}")

@socketio.on('disconnect')
def on_disconnect():
    print(f"🔌 클라이언트 연결 해제: {request.sid}")

@socketio.on('join_session')
def on_join_session(data):
    session_id = data['session_id']
    discord_id = data.get('discord_id')
    
    join_room(session_id)
    
    # 현재 상태 전송
    if session_id in game_sessions:
        session_data = game_sessions[session_id]
        game_state = game_states.get(session_id, {})
        
        emit('game_state_update', {
            'game_state': game_state,
            'participants': session_data.get('participants', []),
            'current_user_discord_id': discord_id
        })
    
    print(f"🎮 세션 참가: {discord_id} -> {session_id}")

def main():
    """웹서버 실행"""
    print("🤖 사이버펑크 나비 내전 웹 서버 시작...")
    print(f"🔑 Discord OAuth 설정:")
    print(f"   Client ID: {discord_oauth.client_id}")
    print(f"   Redirect URI: {discord_oauth.redirect_uri}")
    print(f"🌐 테스트 URL: http://{Config.FLASK_HOST}:{Config.FLASK_PORT}/cyber_test")
    
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

@app.route('/draft_result/<session_id>')
def draft_result_page(session_id):
    """드래프트 결과 확인 페이지"""
    user = session.get('user')
    
    if not user:
        return redirect(url_for('discord_login', next=request.url))
    
    # 세션 확인
    if session_id not in game_sessions:
        return "세션을 찾을 수 없습니다.", 404
    
    print(f"✅ 드래프트 결과 페이지 접근: {user.get('display_name', 'Unknown')} -> {session_id}")
    return render_template('draft_result.html', session_id=session_id, user_info=user)

@app.route('/api/session/<session_id>/result')
def get_draft_result(session_id):
    """드래프트 결과 데이터 조회"""
    if session_id not in game_sessions or session_id not in game_states:
        return jsonify({'error': 'Session not found'}), 404
    
    session_data = game_sessions[session_id]
    game_state = game_states[session_id]
    
    # 결과 데이터 구성
    result_data = {
        'teams': game_state.get('teams', {}),
        'bans': game_state.get('draft', {}).get('bans', {}),
        'picks': game_state.get('draft', {}).get('picks', {}),
        'participants': session_data.get('participants', [])
    }
    
    return jsonify(result_data)

# 웹소켓 이벤트 추가
@socketio.on('join_result_session')
def on_join_result_session(data):
    session_id = data['session_id']
    join_room(f"result_{session_id}")
    
    print(f"🎉 결과 세션 참가: {session_id}")

@socketio.on('confirm_draft_results')
def on_confirm_draft_results(data):
    session_id = data['session_id']
    final_data = data['final_data']
    
    print(f"✅ 드래프트 결과 확정: {session_id}")
    
    # 실제로는 디스코드로 결과 전송
    # TODO: 디스코드 봇에 결과 전송 로직 추가
    
    emit('results_confirmed', {'success': True}, room=f"result_{session_id}")

@socketio.on('save_draft_adjustments')
def on_save_adjustments(data):
    session_id = data['session_id']
    adjustments = data['adjustments']
    
    # 게임 상태 업데이트
    if session_id in game_states:
        game_states[session_id].update(adjustments)
    
    print(f"💾 드래프트 수정사항 저장: {session_id}")
    
    emit('adjustments_saved', {'success': True}, room=f"result_{session_id}")
