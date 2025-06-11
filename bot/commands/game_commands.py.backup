"""나비 내전 게임 관련 명령어"""
import discord
from discord.ext import commands
from bot.views.participant_view import ParticipantView

async def start_match(ctx, title):
    embed = discord.Embed(
        title=f"🦋 {title}",
        description="나비 내전이 시작되었습니다! 참가하려면 아래 버튼을 클릭하세요.",
        color=0x06ffa5
    )
    embed.set_footer(text="🦋 참가자 및 대기자 명단은 실시간으로 업데이트됩니다.")

    message = await ctx.send("@everyone 🦋", embed=embed)
    thread = await message.create_thread(name=f"🦋 {title}")

    view = ParticipantView(thread, message, ctx.author, title)
    await message.edit(view=view)

def setup_game_commands(bot):
    for i in range(1, 6):
        def create_match_command(i):
            async def match_command(ctx, *, title: str = f"나비내전{i}"):
                await start_match(ctx, title)
            return match_command
        bot.command(name=f"내전{i}")(create_match_command(i))
