"""게임 시작 뷰"""
import discord
from discord.ui import Button, View
from bot.utils.session_manager import session_manager
from bot.config import Config

class GameStartView(View):
    def __init__(self, thread, host, embed_message, title, participants):
        super().__init__(timeout=None)
        self.thread = thread
        self.host = host
        self.embed_message = embed_message
        self.title = title
        self.participants = participants

    @discord.ui.button(label="🦋 나비 내전 시작", style=discord.ButtonStyle.green)
    async def start_game(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.host and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("내전 시작은 주최자만 할 수 있습니다!", ephemeral=True)
            return

        await interaction.response.defer()
        
        session_id = session_manager.create_session(
            host_id=self.host.id,
            title=self.title,
            participants=self.participants
        )
        
        draft_url = f"http://{Config.FLASK_HOST}:{Config.FLASK_PORT}/draft/{session_id}"
        
        embed = discord.Embed(
            title=f"🦋 {self.title} 밴픽 페이지",
            description=f"아래 링크를 클릭해서 나비 내전 밴픽 페이지로 이동하세요!\n\n[🦋 밴픽 페이지 바로가기]({draft_url})",
            color=0x06ffa5
        )
        embed.add_field(name="참가자", value=f"{len(self.participants)}명", inline=True)
        embed.add_field(name="세션 ID", value=session_id[:8], inline=True)
        embed.set_footer(text="🦋 모든 참가자가 접속할 때까지 기다려주세요.")
        
        await self.thread.send(f"@everyone **🦋 {self.title}** 나비 내전이 시작됩니다! 밴픽 페이지로 이동해주세요.", embed=embed)
