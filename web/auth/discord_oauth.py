import requests
import secrets
from flask import session
from urllib.parse import urlencode
import os

class DiscordOAuth:
    def __init__(self):
        self.client_id = os.getenv('DISCORD_CLIENT_ID')
        self.client_secret = os.getenv('DISCORD_CLIENT_SECRET')
        self.redirect_uri = os.getenv('DISCORD_REDIRECT_URI')
        self.auth_url = "https://discord.com/api/oauth2/authorize"
        self.token_url = "https://discord.com/api/oauth2/token"
        self.api_base = "https://discord.com/api/v10"
        
        # 봇이 속한 서버 ID (내전이 진행되는 서버)
        self.guild_id = os.getenv('DISCORD_GUILD_ID')  # .env에 추가 필요
    
    def get_authorization_url(self, state=None):
        """OAuth 인증 URL 생성 - 서버 정보도 가져오도록 scope 확장"""
        if not state:
            state = secrets.token_urlsafe(32)
            session['oauth_state'] = state
        
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': 'identify guilds guilds.members.read',  # 서버 멤버 정보 권한 추가
            'state': state
        }
        
        return f"{self.auth_url}?{urlencode(params)}"
    
    def get_access_token(self, code, state):
        """인증 코드로 액세스 토큰 획득"""
        if session.get('oauth_state') != state:
            raise ValueError("Invalid OAuth state")
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri,
        }
        
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(self.token_url, data=data, headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    def get_user_info(self, access_token):
        """사용자 정보 및 서버 닉네임 가져오기"""
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # 기본 사용자 정보
        response = requests.get(f"{self.api_base}/users/@me", headers=headers)
        response.raise_for_status()
        user_data = response.json()
        
        # 서버 닉네임 가져오기 (봇 토큰 필요)
        server_nickname = self.get_server_nickname(user_data['id'])
        
        # 디스코드 새 사용자명 시스템 처리
        if user_data.get('discriminator') == '0':
            # 새 시스템: @username
            display_name = f"@{user_data['username']}"
        else:
            # 기존 시스템: username#discriminator
            display_name = f"{user_data['username']}#{user_data['discriminator']}"
        
        # 서버 닉네임이 있으면 우선 사용
        final_display_name = server_nickname if server_nickname else display_name
        
        avatar_url = self.get_avatar_url(user_data['id'], user_data.get('avatar'))
        
        return {
            'id': user_data['id'],
            'username': user_data['username'],
            'discriminator': user_data.get('discriminator', '0'),
            'display_name': display_name,  # 기본 디스코드 이름
            'server_nickname': server_nickname,  # 서버 닉네임
            'final_name': final_display_name,  # 최종 표시될 이름
            'avatar': user_data.get('avatar'),
            'avatar_url': avatar_url
        }
    
    def get_server_nickname(self, user_id):
        """봇 토큰으로 서버에서의 닉네임 가져오기"""
        if not self.guild_id:
            return None
            
        try:
            # 봇 토큰 사용 (OAuth 토큰이 아닌)
            bot_token = os.getenv('DISCORD_BOT_TOKEN')
            if not bot_token:
                return None
                
            headers = {'Authorization': f'Bot {bot_token}'}
            
            # 서버 멤버 정보 가져오기
            response = requests.get(
                f"{self.api_base}/guilds/{self.guild_id}/members/{user_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                member_data = response.json()
                # 서버 닉네임이 있으면 반환, 없으면 None
                return member_data.get('nick')
            else:
                print(f"서버 멤버 정보 가져오기 실패: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"서버 닉네임 가져오기 오류: {e}")
            return None
    
    def get_avatar_url(self, user_id, avatar_hash):
        """아바타 URL 생성"""
        if avatar_hash:
            return f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.png"
        else:
            # 기본 아바타
            discriminator = int(user_id) % 5
            return f"https://cdn.discordapp.com/embed/avatars/{discriminator}.png"
