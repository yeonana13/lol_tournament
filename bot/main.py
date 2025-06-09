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
import discord
from discord.ext import commands
import asyncio
import json
import uuid
from datetime import datetime

# 봇 설정
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='%', intents=intents)

# 게임 세션 저장소
game_sessions = {}

class GameSession:
    def __init__(self, session_id, channel_id):
        self.session_id = session_id
        self.channel_id = channel_id
        self.participants = []
        self.status = 'recruiting'
        self.created_at = datetime.now()
        self.max_players = 10
    
    def add_participant(self, user):
        if len(self.participants) < self.max_players:
            self.participants.append({
                'discord_id': str(user.id),
                'discord_name': user.display_name,
                'joined_at': datetime.now()
            })
            return True
        return False
    
    def remove_participant(self, user_id):
        self.participants = [p for p in self.participants if p['discord_id'] != str(user_id)]
    
    def is_full(self):
        return len(self.participants) >= self.max_players
    
    def get_participant_count(self):
        return len(self.participants)

@bot.event
async def on_ready():
    print(f'🦋 {bot.user} 나비 내전 봇이 준비되었습니다!')
    print(f'🔗 봇이 {len(bot.guilds)}개의 서버에 연결되어 있습니다.')

@bot.command(name='내전1')
async def start_game_1(ctx):
    await start_internal_game(ctx, 1)

@bot.command(name='내전2') 
async def start_game_2(ctx):
    await start_internal_game(ctx, 2)

@bot.command(name='내전3')
async def start_game_3(ctx):
    await start_internal_game(ctx, 3)

@bot.command(name='내전4')
async def start_game_4(ctx):
    await start_internal_game(ctx, 4)

@bot.command(name='내전5')
async def start_game_5(ctx):
    await start_internal_game(ctx, 5)

async def start_internal_game(ctx, game_number):
    """내전 게임 시작"""
    session_id = f"game_{game_number}_{ctx.channel.id}_{int(datetime.now().timestamp())}"
    
    # 기존 세션이 있는지 확인
    if session_id in game_sessions:
        await ctx.send("🦋 이미 진행 중인 내전이 있습니다!")
        return
    
    # 새 게임 세션 생성
    session = GameSession(session_id, ctx.channel.id)
    game_sessions[session_id] = session
    
    embed = discord.Embed(
        title=f"🦋 나비 내전 {game_number} 모집 시작!",
        description=f"현재 참가자: 0/10명\n\n⚡ 아래 버튼을 눌러 참가하세요!",
        color=0x9932cc
    )
    embed.add_field(name="참가자 목록", value="아직 아무도 참가하지 않았습니다.", inline=False)
    
    view = GameParticipationView(session_id)
    message = await ctx.send(embed=embed, view=view)
    
    # 메시지 ID 저장
    session.message_id = message.id

class GameParticipationView(discord.ui.View):
    def __init__(self, session_id):
        super().__init__(timeout=300)  # 5분 타임아웃
        self.session_id = session_id
    
    @discord.ui.button(label='🦋 참가하기', style=discord.ButtonStyle.primary)
    async def join_game(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        session = game_sessions.get(self.session_id)
        if not session:
            await interaction.followup.send("❌ 게임 세션을 찾을 수 없습니다.", ephemeral=True)
            return
        
        # 이미 참가했는지 확인
        user_id = str(interaction.user.id)
        if any(p['discord_id'] == user_id for p in session.participants):
            await interaction.followup.send("⚠️ 이미 참가하셨습니다!", ephemeral=True)
            return
        
        # 참가자 추가
        if session.add_participant(interaction.user):
            participant_list = "\n".join([f"{i+1}. {p['discord_name']}" for i, p in enumerate(session.participants)])
            
            embed = discord.Embed(
                title=f"🦋 나비 내전 모집 중...",
                description=f"현재 참가자: {session.get_participant_count()}/10명",
                color=0x9932cc
            )
            embed.add_field(name="참가자 목록", value=participant_list, inline=False)
            
            # 10명이 모였는지 확인
            if session.is_full():
                embed.title = "🎉 10명 모집 완료!"
                embed.description = "밴픽 페이지로 이동합니다..."
                embed.color = 0x00ff00
                
                # 밴픽 페이지 링크 생성
                banpick_url = f"{Config.get_base_url()}/banpick/{session.session_id}"
                embed.add_field(name="🔗 밴픽 페이지", value=f"[여기를 클릭하세요!]({banpick_url})", inline=False)
                
                # 세션 상태 업데이트
                session.status = 'lobby'
                
                # 참가자들에게 DM 발송
                for participant in session.participants:
                    try:
                        user = await interaction.client.fetch_user(int(participant['discord_id']))
                        await user.send(f"🦋 내전 밴픽이 시작되었습니다!\n🔗 {banpick_url}")
                    except:
                        pass  # DM 발송 실패는 무시
                
                # 버튼 비활성화
                for item in self.children:
                    item.disabled = True
            
            await interaction.edit_original_response(embed=embed, view=self if not session.is_full() else None)
            
        else:
            await interaction.followup.send("❌ 참가자가 가득 찼습니다!", ephemeral=True)
    
    @discord.ui.button(label='❌ 참가 취소', style=discord.ButtonStyle.secondary)
    async def leave_game(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        session = game_sessions.get(self.session_id)
        if not session:
            await interaction.followup.send("❌ 게임 세션을 찾을 수 없습니다.", ephemeral=True)
            return
        
        # 참가자 제거
        user_id = str(interaction.user.id)
        if not any(p['discord_id'] == user_id for p in session.participants):
            await interaction.followup.send("⚠️ 참가하지 않은 상태입니다!", ephemeral=True)
            return
        
        session.remove_participant(user_id)
        
        if session.participants:
            participant_list = "\n".join([f"{i+1}. {p['discord_name']}" for i, p in enumerate(session.participants)])
        else:
            participant_list = "아직 아무도 참가하지 않았습니다."
        
        embed = discord.Embed(
            title=f"🦋 나비 내전 모집 중...",
            description=f"현재 참가자: {session.get_participant_count()}/10명",
            color=0x9932cc
        )
        embed.add_field(name="참가자 목록", value=participant_list, inline=False)
        
        await interaction.edit_original_response(embed=embed, view=self)

@bot.command(name='나비')
async def nabi_info(ctx):
    """나비 시스템 정보"""
    embed = discord.Embed(
        title="🦋 나비 내전 시스템",
        description="아름다운 리그 오브 레전드 내전 시스템입니다.",
        color=0x9932cc
    )
    embed.add_field(name="📋 명령어", value="`!내전1` ~ `!내전5`: 내전 모집\n`!나비`: 시스템 정보", inline=False)
    embed.add_field(name="🎮 기능", value="• 10명 자동 모집\n• 웹 기반 밴픽\n• 실시간 결과 처리", inline=False)
    
    await ctx.send(embed=embed)



@bot.command(name='테스트')
async def test_fill_game(ctx):
    """테스트용: 게임을 더미 참가자로 채우기"""
    # 진행 중인 세션 찾기
    channel_sessions = [s for s in game_sessions.values() if s.channel_id == ctx.channel.id and s.status == 'recruiting']
    
    if not channel_sessions:
        await ctx.send("❌ 진행 중인 내전이 없습니다. 먼저 %내전1을 실행하세요!")
        return
    
    session = channel_sessions[0]
    
    # 더미 참가자들 추가
    dummy_users = [
        {'discord_id': f'dummy_{i}', 'discord_name': f'테스터{i}', 'joined_at': datetime.now()}
        for i in range(1, 11)
    ]
    
    # 기존 참가자 수만큼 제외하고 추가
    current_count = len(session.participants)
    needed = 10 - current_count
    
    if needed <= 0:
        await ctx.send("✅ 이미 10명이 모였습니다!")
        return
    
    # 더미 참가자 추가
    for i in range(needed):
        if i < len(dummy_users):
            session.participants.append(dummy_users[i])
    
    # 임베드 업데이트
    participant_list = "\n".join([f"{i+1}. {p['discord_name']}" for i, p in enumerate(session.participants)])
    
    embed = discord.Embed(
        title="🎉 10명 모집 완료! (테스트)",
        description="밴픽 페이지로 이동합니다...",
        color=0x00ff00
    )
    embed.add_field(name="참가자 목록", value=participant_list, inline=False)
    
    # 밴픽 페이지 링크 생성
    banpick_url = f"{Config.get_base_url()}/banpick/{session.session_id}"
    embed.add_field(name="🔗 밴픽 페이지", value=f"[여기를 클릭하세요!]({banpick_url})", inline=False)
    
    # 세션 상태 업데이트
    session.status = 'lobby'
    
    await ctx.send(embed=embed)

@bot.command(name='리셋')
async def reset_games(ctx):
    """테스트용: 현재 채널의 모든 게임 세션 리셋"""
    # 현재 채널의 세션들 제거
    sessions_to_remove = [sid for sid, session in game_sessions.items() if session.channel_id == ctx.channel.id]
    
    for sid in sessions_to_remove:
        del game_sessions[sid]
    
    await ctx.send(f"✅ {len(sessions_to_remove)}개의 게임 세션을 리셋했습니다!")




@bot.command(name='드래프트테스트')
async def draft_test(ctx):
    """드래프트 페이지 바로 테스트"""
    session_id = f"draft_test_{ctx.channel.id}_{int(datetime.now().timestamp())}"
    
    embed = discord.Embed(
        title="🎮 드래프트 테스트",
        description="밴픽 드래프트 시스템을 테스트합니다!",
        color=0x9932cc
    )
    
    # 드래프트 페이지 링크 생성
    draft_url = f"{Config.get_base_url()}/draft/{session_id}"
    embed.add_field(name="🔗 드래프트 페이지", value=f"[여기를 클릭하세요!]({draft_url})", inline=False)
    embed.add_field(name="💡 안내", value="포지션 선택 없이 바로 밴픽을 테스트할 수 있습니다.", inline=False)
    
    await ctx.send(embed=embed)


def main():
    """봇 실행"""
    print("🦋 나비 내전 디스코드 봇 시작...")
    if not Config.DISCORD_BOT_TOKEN:
        print("❌ 디스코드 봇 토큰이 설정되지 않았습니다!")
        print("💡 .env 파일에 DISCORD_BOT_TOKEN을 설정해주세요.")
        return
    
    try:
        bot.run(Config.DISCORD_BOT_TOKEN)
    except Exception as e:
        print(f"❌ 봇 실행 실패: {e}")

if __name__ == "__main__":
    main()
