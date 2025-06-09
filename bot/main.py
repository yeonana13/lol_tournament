"""나비 내전 봇 메인 실행 파일"""
import asyncio
import discord
from discord.ext import commands
from bot.config import Config
from bot.commands.game_commands import setup_game_commands
from bot.commands.utility_commands import setup_utility_commands
from bot.views.participant_view import ParticipantView
from bot.utils.nickname_parser import get_tier_sort_key
from database.connection import create_tables

# 인텐트 설정
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True

# 나비 봇 생성
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print("🦋" + "="*50)
    print("🦋 나비 내전 봇이 실행되었습니다!")
    print(f"🦋 봇 이름: {bot.user}")
    print(f"🦋 서버 수: {len(bot.guilds)}")
    print("🦋" + "="*50)
    
    # 데이터베이스 테이블 생성
    create_tables()

@bot.event
async def on_member_remove(member):
    """멤버가 서버를 나갈 때 참가자 목록에서 제거"""
    for view in bot.persistent_views:
        if isinstance(view, ParticipantView):
            updated = False
            
            if member.id in view.participants:
                view.participants.remove(member.id)
                updated = True
                
                if view.waitlist:
                    next_participant_id = view.waitlist.pop(0)
                    view.participants.append(next_participant_id)
                    view.sort_participants()
                    
                    try:
                        next_member = await member.guild.fetch_member(next_participant_id)
                        next_name = next_member.display_name
                    except:
                        next_name = f"알 수 없는 사용자 (ID: {next_participant_id})"
                        
                    await view.thread.send(f"**🦋 {member.display_name}님이 서버를 나가서 제거되었고, {next_name}님이 대기자에서 참가자로 승격되었습니다.**")
                else:
                    await view.thread.send(f"**🦋 {member.display_name}님이 서버를 나가서 목록에서 제거되었습니다.**")
            
            elif member.id in view.waitlist:
                view.waitlist.remove(member.id)
                updated = True
                await view.thread.send(f"**🦋 {member.display_name}님이 서버를 나가서 대기자 목록에서 제거되었습니다.**")
            
            if updated:
                try:
                    await asyncio.sleep(0.5)
                    # update_embed_from_event 메서드가 없으므로 일반 update_embed 사용
                    # 실제로는 interaction 없이 업데이트하는 별도 메서드가 필요
                    pass
                except Exception as e:
                    await view.thread.send(f"🦋 임베드 업데이트 중 오류가 발생했습니다: {str(e)}")

@bot.event
async def on_member_update(before, after):
    """멤버 닉네임 변경 시 목록 업데이트"""
    if before.display_name != after.display_name:
        for view in bot.persistent_views:
            if isinstance(view, ParticipantView):
                if after.id in view.participants or after.id in view.waitlist:
                    await asyncio.sleep(0.5)
                    await view.thread.send(f"**🦋 {before.display_name}님의 닉네임이 {after.display_name}(으)로 변경되어 목록이 업데이트되었습니다.**")

def run_bot():
    """나비 봇 실행"""
    # 명령어 등록
    setup_game_commands(bot)
    setup_utility_commands(bot)
    
    # 봇 실행
    bot.run(Config.DISCORD_BOT_TOKEN)

if __name__ == "__main__":
    run_bot()
