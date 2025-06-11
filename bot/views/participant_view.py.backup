"""참가자 관리 뷰"""
import random
import asyncio
import discord
from discord.ui import Button, View
from shared.constants import MAX_PARTICIPANTS, RANDOM_MESSAGES
from bot.utils.nickname_parser import get_tier_sort_key
from bot.views.game_start_view import GameStartView

class ParticipantView(View):
    def __init__(self, thread, embed_message, host, title):
        super().__init__(timeout=None)
        self.participants = []
        self.waitlist = []
        self.thread = thread
        self.embed_message = embed_message
        self.host = host
        self.game_started = False
        self.title = title

    def sort_participants(self):
        def tier_key(user_id):
            try:
                for member in self.embed_message.guild.members:
                    if member.id == user_id:
                        return get_tier_sort_key(member.display_name)
            except:
                pass
            return float('inf')
        self.participants.sort(key=tier_key)

    async def check_full(self):
        if len(self.participants) == MAX_PARTICIPANTS and not self.game_started:
            self.game_started = True
            await asyncio.sleep(3)

            embed = discord.Embed(
                title="🦋 나비 내전 시작 준비",
                description=f"{self.host.mention}, 내전을 시작하겠습니까?",
                color=0x06ffa5
            )
            embed.set_footer(text="🦋 내전을 시작하려면 아래 버튼을 눌러주세요.")

            view = GameStartView(self.thread, self.host, self.embed_message, self.title, self.participants)
            await self.thread.send(embed=embed, view=view)

    @discord.ui.button(label="참가하기", style=discord.ButtonStyle.green)
    async def join(self, interaction: discord.Interaction, button: Button):
        user_id = interaction.user.id

        if user_id in self.participants or user_id in self.waitlist:
            await interaction.response.send_message("이미 참가자 또는 대기자 명단에 있습니다!", ephemeral=True)
            return

        if len(self.participants) < MAX_PARTICIPANTS:
            self.participants.append(user_id)
            self.sort_participants()
            await self.update_embed(interaction)
            await self.check_full()
        else:
            self.waitlist.append(user_id)
            await interaction.response.send_message("참가 인원이 가득 찼습니다. 대기자로 추가되었습니다!", ephemeral=True)
            await self.update_embed(interaction)

        await self.thread.send(f"🦋 {interaction.user.mention} 님이 나비 내전에 참가했습니다! 🎉")

    @discord.ui.button(label="참가취소", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: Button):
        user_id = interaction.user.id

        if user_id in self.participants:
            self.participants.remove(user_id)
            if self.waitlist:
                next_participant_id = self.waitlist.pop(0)
                self.participants.append(next_participant_id)
                self.sort_participants()
                next_member = await interaction.guild.fetch_member(next_participant_id)
                next_participant_name = next_member.display_name if next_member else f"알 수 없는 사용자 (ID: {next_participant_id})"
                await self.thread.send(f"**_🦋 대기자에서 참가자로 이동: {next_participant_name}_**")
            await self.update_embed(interaction)
            await self.thread.send(f"**_🦋 참가 취소: {interaction.user.display_name}_**")
        elif user_id in self.waitlist:
            self.waitlist.remove(user_id)
            await self.update_embed(interaction)
            await self.thread.send(f"**_🦋 대기 취소: {interaction.user.display_name}_**")
        else:
            await interaction.response.send_message("참가자나 대기자 명단에 없습니다!", ephemeral=True)

    @discord.ui.button(emoji="📢", label="", style=discord.ButtonStyle.blurple)
    async def notify(self, interaction: discord.Interaction, button: Button):
        remaining_slots = MAX_PARTICIPANTS - len(self.participants)
        random_message = random.choice(RANDOM_MESSAGES).format(remaining_slots)

        await interaction.channel.send(f"@everyone {random_message}")
        await self.thread.send(f"**_🦋 홍보 알림: {interaction.user.display_name}님이 나비 내전 참여를 홍보했습니다!_**")
        await interaction.response.defer()

    @discord.ui.button(emoji="❌", label="", style=discord.ButtonStyle.gray)
    async def delete_message(self, interaction: discord.Interaction, button: Button):
        if interaction.user == self.host or interaction.user.guild_permissions.administrator:
            await self.embed_message.delete()
        else:
            await interaction.response.send_message("이 버튼은 주최자 또는 관리자만 사용할 수 있습니다.", ephemeral=True)

    async def update_embed(self, interaction):
        try:
            embed = self.embed_message.embeds[0]
            remaining_slots = MAX_PARTICIPANTS - len(self.participants)
            
            participant_list = []
            for user_id in self.participants:
                try:
                    member = await interaction.guild.fetch_member(user_id)
                    participant_list.append(f"🦋 {member.display_name}")
                except:
                    participant_list.append(f"🦋 알 수 없는 사용자 (ID: {user_id})")
            
            waitlist_list = []
            for user_id in self.waitlist:
                try:
                    member = await interaction.guild.fetch_member(user_id)
                    waitlist_list.append(f"⏳ {member.display_name}")
                except:
                    waitlist_list.append(f"⏳ 알 수 없는 사용자 (ID: {user_id})")
            
            embed.description = (
                f"**🦋 남은 자리: {remaining_slots}명**\n\n"
                f"**참가자 명단:**\n" +
                ("\n".join(participant_list) if participant_list else "없음") +
                "\n\n**대기자 명단:**\n" +
                ("\n".join(waitlist_list) if waitlist_list else "없음")
            )
            await self.embed_message.edit(embed=embed, view=self)
            await interaction.response.defer()
        except Exception as e:
            print(f"업데이트 중 오류 발생: {str(e)}")
            try:
                await interaction.response.defer()
            except:
                pass
