"""나비 내전 웹 서버 메인 (향상된 버전)"""
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from bot.config import Config
from bot.utils.session_manager import session_manager
from web.api.champion_api import champion_bp
from web.api.session_api import session_bp
import os

# Flask 앱 생성
app = Flask(__name__)
app.config['SECRET_KEY'] = getattr(Config, 'SECRET_KEY', 'butterfly_nabi_secret')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# 블루프린트 등록
app.register_blueprint(champion_bp)
app.register_blueprint(session_bp)

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/draft/<session_id>')
def draft_page(session_id):
    """향상된 밴픽 페이지"""
    session = session_manager.get_session(session_id)
    if not session:
        return "세션을 찾을 수 없습니다.", 404
    
    return render_template('draft_enhanced.html', 
                         session_id=session_id,
                         title=session.title,
                         participants=len(session.participants))

@app.route('/profile/<player_name>')
def profile_page(player_name):
    """플레이어 프로필 페이지"""
    return render_template('profile.html', player_name=player_name)

# WebSocket 이벤트 (실시간 밴픽용)
@socketio.on('join_draft')
def on_join_draft(data):
    session_id = data['session_id']
    join_room(session_id)
    emit('user_joined', {'message': f'🦋 사용자가 밴픽방에 입장했습니다.'}, room=session_id)

@socketio.on('leave_draft')
def on_leave_draft(data):
    session_id = data['session_id']
    leave_room(session_id)
    emit('user_left', {'message': f'🦋 사용자가 밴픽방을 나갔습니다.'}, room=session_id)

@socketio.on('ban_champion')
def on_ban_champion(data):
    """챔피언 밴"""
    session_id = data['session_id']
    champion = data['champion']
    champion_english = data.get('champion_english', '')
    team = data['team']
    
    emit('champion_banned', {
        'champion': champion,
        'champion_english': champion_english,
        'team': team,
        'message': f'{team} 팀이 {champion}을(를) 밴했습니다.'
    }, room=session_id)

@socketio.on('pick_champion')
def on_pick_champion(data):
    """챔피언 픽"""
    session_id = data['session_id']
    champion = data['champion']
    champion_english = data.get('champion_english', '')
    team = data['team']
    position = data['position']
    
    emit('champion_picked', {
        'champion': champion,
        'champion_english': champion_english,
        'team': team,
        'position': position,
        'message': f'{team} 팀이 {position} 포지션으로 {champion}을(를) 픽했습니다.'
    }, room=session_id)

def create_app():
    """앱 팩토리"""
    return app

if __name__ == '__main__':
    socketio.run(app, 
                host=Config.FLASK_HOST, 
                port=Config.FLASK_PORT, 
                debug=getattr(Config, 'FLASK_DEBUG', True))
