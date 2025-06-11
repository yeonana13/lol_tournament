"""나비 내전 게임 관련 명령어"""
import discord
from discord.ext import commands
from bot.views.participant_view import ParticipantView
import requests
import json
import uuid
from datetime import datetime

def format_user_info(user):
    """디스코드 유저 정보를 포맷팅"""
    return {
        'discord_id': str(user.id),
        'username': user.name,
        'display_name': user.display_name or user.name,
        'avatar_url': str(user.avatar.url) if user.avatar else str(user.default_avatar.url),
        'discriminator': user.discriminator if hasattr(user, 'discriminator') else '0000'
    }

async def start_match(ctx, title):
    embed = discord.Embed(
        title=f"🦋 {title}",
        description="나비 내전이 시작되었습니다! 참가하려면 아래 버튼을 클릭하세요.",
        color=0x06ffa5
    )
    embed.set_footer(text="🦋 참가자 및 대기자 명단은 실시간으로 업데이트됩니다.")

    message = await ctx.send("@everyone 🦋", embed=embed)
    thread = await message.create_thread(name=f"🦋 {title}")

    # 유저 정보를 포함한 ParticipantView 생성
    view = ParticipantView(thread, message, ctx.author, title, format_user_info)
    await message.edit(view=view)

def setup_game_commands(bot):
    for i in range(1, 6):
        def create_match_command(i):
            async def match_command(ctx, *, title: str = f"나비내전{i}"):
                await start_match(ctx, title)
            return match_command
        bot.command(name=f"내전{i}")(create_match_command(i))

    @commands.command(name='사이버테스트', aliases=['사테', 'cyber'])
    async def cyber_draft_test(self, ctx):
        """사이버펑크 스타일 드래프트 테스트"""
        try:
            # 사이버 테스트용 세션 ID 생성
            session_id = f"cyber_{int(datetime.now().timestamp())}"
            
            # 테스트용 참가자 (현재 명령어 실행자 포함)
            participants = [self.format_user_info(ctx.author)]
            
            # 더미 참가자들 추가
            for i in range(9):
                dummy_user = {
                    'discord_id': f'cyber_{i}',
                    'username': f'CyberUser{i+1}',
                    'display_name': f'사이버유저{i+1}',
                    'avatar_url': f'https://cdn.discordapp.com/embed/avatars/{i % 6}.png',
                    'discriminator': f'{3000 + i:04d}'
                }
                participants.append(dummy_user)
            
            # 웹서버에 테스트 세션 생성
            session_data = {
                'session_id': session_id,
                'participants': participants,
                'channel_id': str(ctx.channel.id),
                'guild_id': str(ctx.guild.id),
                'created_by': self.format_user_info(ctx.author),
                'created_at': datetime.now().isoformat(),
                'title': '🤖 사이버펑크 드래프트'
            }
            
            response = requests.post(
                f'{self.web_server_url}/api/session/create',
                json=session_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                embed = discord.Embed(
                    title="🤖 사이버펑크 드래프트",
                    description="사이버펑크 스타일 드래프트 페이지가 생성되었습니다!",
                    color=0x00ff88
                )
                embed.add_field(
                    name="🎮 사이버 페이지",
                    value=f"[매트릭스 진입!]({self.web_server_url}/draft_cyber/{session_id})",
                    inline=False
                )
                embed.add_field(name="세션 ID", value=f"`{session_id}`", inline=True)
                embed.add_field(name="참가자", value=f"{len(participants)}명", inline=True)
                embed.add_field(name="테마", value="🟢 네온 사이버펑크", inline=True)
                
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"❌ 사이버 세션 생성 실패: {response.text}")
                
        except Exception as e:
            await ctx.send(f"❌ 사이버 드래프트 실패: {str(e)}")
