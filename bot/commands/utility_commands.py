"""나비 내전 유틸리티 명령어"""
import random
import discord
from discord.ext import commands

def setup_utility_commands(bot):
    @bot.command(name="주사위")
    async def roll_dice(ctx):
        dice_result = random.randint(1, 6)
        dice_emojis = {1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5: "5️⃣", 6: "6️⃣"}
        
        embed = discord.Embed(
            title="🦋 나비 주사위 결과",
            description=f"{ctx.author.mention}님이 나비 주사위를 굴렸습니다!\n\n🎲 결과: {dice_emojis[dice_result]} ({dice_result})",
            color=0x06ffa5
        )
        await ctx.send(embed=embed)
    
    @bot.command(name="나비")
    async def butterfly_info(ctx):
        embed = discord.Embed(
            title="🦋 나비 내전 시스템",
            description="나비처럼 아름다운 내전을 즐겨보세요!",
            color=0x06ffa5
        )
        embed.add_field(name="📋 명령어", value="`!내전1` ~ `!내전5`", inline=True)
        embed.add_field(name="🎲 주사위", value="`!주사위`", inline=True)
        embed.add_field(name="🦋 정보", value="`!나비`", inline=True)
        embed.set_footer(text="🦋 나비 서버에서 즐거운 내전 되세요!")
        await ctx.send(embed=embed)
