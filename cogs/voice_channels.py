import discord
import asyncio
from discord.ext import commands, tasks
from discord import app_commands, ui
from database import SessionLocal, VoiceChannelConfig, TempVoiceChannel
from typing import Optional, Dict


class VoiceControlPanel(ui.View):
    def __init__(self, channel_id: int, lang: str = "ru"):
        super().__init__(timeout=None)
        self.channel_id = channel_id
        self.lang = lang

    async def check_owner(self, interaction: discord.Interaction) -> bool:
        session = SessionLocal()
        try:
            temp_channel = session.query(TempVoiceChannel).filter_by(channel_id=self.channel_id).first()
            if not temp_channel:
                await interaction.response.send_message("Канал не найден.", ephemeral=True)
                return False
            if interaction.user.id != temp_channel.owner_id:
                if not interaction.user.guild_permissions.manage_channels:
                    await interaction.response.send_message("Только владелец может это сделать.", ephemeral=True)
                    return False
            return True
        finally:
            session.close()

    def _label(self, ru: str, en: str) -> str:
        return ru if self.lang == "ru" else en

    @ui.button(label="🔒 Закрыть", style=discord.ButtonStyle.secondary, row=0)
    async def lock_channel(self, interaction: discord.Interaction, button: ui.Button):
        if not await self.check_owner(interaction): return
        channel = interaction.guild.get_channel(self.channel_id)
        if channel:
            await channel.set_permissions(interaction.guild.default_role, connect=False)
            session = SessionLocal()
            try:
                tc = session.query(TempVoiceChannel).filter_by(channel_id=self.channel_id).first()
                if tc: tc.is_locked = True; session.commit()
            finally: session.close()
            await interaction.response.send_message(self._label("🔒 Канал закрыт.", "🔒 Channel locked."), ephemeral=True)

    @ui.button(label="🔓 Открыть", style=discord.ButtonStyle.secondary, row=0)
    async def unlock_channel(self, interaction: discord.Interaction, button: ui.Button):
        if not await self.check_owner(interaction): return
        channel = interaction.guild.get_channel(self.channel_id)
        if channel:
            await channel.set_permissions(interaction.guild.default_role, connect=True)
            session = SessionLocal()
            try:
                tc = session.query(TempVoiceChannel).filter_by(channel_id=self.channel_id).first()
                if tc: tc.is_locked = False; session.commit()
            finally: session.close()
            await interaction.response.send_message(self._label("🔓 Канал открыт.", "🔓 Channel unlocked."), ephemeral=True)

    @ui.button(label="👁️ Скрыть", style=discord.ButtonStyle.secondary, row=0)
    async def hide_channel(self, interaction: discord.Interaction, button: ui.Button):
        if not await self.check_owner(interaction): return
        channel = interaction.guild.get_channel(self.channel_id)
        if channel:
            await channel.set_permissions(interaction.guild.default_role, view_channel=False)
            session = SessionLocal()
            try:
                tc = session.query(TempVoiceChannel).filter_by(channel_id=self.channel_id).first()
                if tc: tc.is_hidden = True; session.commit()
            finally: session.close()
            await interaction.response.send_message(self._label("👁️ Канал скрыт.", "👁️ Channel hidden."), ephemeral=True)

    @ui.button(label="👀 Показать", style=discord.ButtonStyle.secondary, row=0)
    async def show_channel(self, interaction: discord.Interaction, button: ui.Button):
        if not await self.check_owner(interaction): return
        channel = interaction.guild.get_channel(self.channel_id)
        if channel:
            await channel.set_permissions(interaction.guild.default_role, view_channel=True)
            session = SessionLocal()
            try:
                tc = session.query(TempVoiceChannel).filter_by(channel_id=self.channel_id).first()
                if tc: tc.is_hidden = False; session.commit()
            finally: session.close()
            await interaction.response.send_message(self._label("👀 Канал виден.", "👀 Channel visible."), ephemeral=True)

    @ui.button(label="✏️ Переименовать", style=discord.ButtonStyle.primary, row=1)
    async def rename_channel(self, interaction: discord.Interaction, button: ui.Button):
        if not await self.check_owner(interaction): return
        modal = RenameModal(self.channel_id, self.lang)
        await interaction.response.send_modal(modal)

    @ui.button(label="👥 Лимит", style=discord.ButtonStyle.primary, row=1)
    async def set_limit(self, interaction: discord.Interaction, button: ui.Button):
        if not await self.check_owner(interaction): return
        modal = LimitModal(self.channel_id, self.lang)
        await interaction.response.send_modal(modal)

    @ui.button(label="➕ Пригласить", style=discord.ButtonStyle.success, row=1)
    async def invite_user(self, interaction: discord.Interaction, button: ui.Button):
        if not await self.check_owner(interaction): return
        modal = UserActionModal(self.channel_id, "invite", self.lang)
        await interaction.response.send_modal(modal)

    @ui.button(label="➖ Выгнать", style=discord.ButtonStyle.danger, row=1)
    async def kick_user(self, interaction: discord.Interaction, button: ui.Button):
        if not await self.check_owner(interaction): return
        modal = UserActionModal(self.channel_id, "kick", self.lang)
        await interaction.response.send_modal(modal)

    @ui.button(label="🚫 Забанить", style=discord.ButtonStyle.danger, row=2)
    async def ban_user(self, interaction: discord.Interaction, button: ui.Button):
        if not await self.check_owner(interaction): return
        modal = UserActionModal(self.channel_id, "ban", self.lang)
        await interaction.response.send_modal(modal)

    @ui.button(label="👑 Передать", style=discord.ButtonStyle.primary, row=2)
    async def transfer_ownership(self, interaction: discord.Interaction, button: ui.Button):
        if not await self.check_owner(interaction): return
        modal = UserActionModal(self.channel_id, "transfer", self.lang)
        await interaction.response.send_modal(modal)

    @ui.button(label="🔊 Битрейт", style=discord.ButtonStyle.secondary, row=2)
    async def set_bitrate(self, interaction: discord.Interaction, button: ui.Button):
        if not await self.check_owner(interaction): return
        modal = BitrateModal(self.channel_id, self.lang)
        await interaction.response.send_modal(modal)


class RenameModal(ui.Modal, title="Переименовать"):
    name = ui.TextInput(label="Новое название", placeholder="Voice Chat", min_length=1, max_length=100)
    def __init__(self, channel_id: int):
        super().__init__()
        self.channel_id = channel_id
    async def on_submit(self, interaction: discord.Interaction):
        channel = interaction.guild.get_channel(self.channel_id)
        if channel:
            await channel.edit(name=self.name.value)
            session = SessionLocal()
            try:
                tc = session.query(TempVoiceChannel).filter_by(channel_id=self.channel_id).first()
                if tc: tc.name = self.name.value; session.commit()
            finally: session.close()
            await interaction.response.send_message(f"✅ Канал переименован в **{self.name.value}**", ephemeral=True)


class LimitModal(ui.Modal, title="Лимит участников"):
    limit = ui.TextInput(label="Лимит (0 = без лимита)", placeholder="5", min_length=1, max_length=2)
    def __init__(self, channel_id: int):
        super().__init__()
        self.channel_id = channel_id
    async def on_submit(self, interaction: discord.Interaction):
        try:
            val = max(0, min(99, int(self.limit.value)))
        except Exception:
            await interaction.response.send_message("❌ Введите число!", ephemeral=True); return
        channel = interaction.guild.get_channel(self.channel_id)
        if channel:
            await channel.edit(user_limit=val)
            session = SessionLocal()
            try:
                tc = session.query(TempVoiceChannel).filter_by(channel_id=self.channel_id).first()
                if tc: tc.user_limit = val; session.commit()
            finally: session.close()
            await interaction.response.send_message(f"✅ Лимит: {val if val > 0 else 'без лимита'}", ephemeral=True)


class BitrateModal(ui.Modal, title="Битрейт (kbps)"):
    bitrate = ui.TextInput(label="Битрейт (8-384)", placeholder="64", min_length=1, max_length=3)
    def __init__(self, channel_id: int):
        super().__init__()
        self.channel_id = channel_id
    async def on_submit(self, interaction: discord.Interaction):
        try:
            val = max(8, min(384, int(self.bitrate.value)))
        except Exception:
            await interaction.response.send_message("❌ Введите число!", ephemeral=True); return
        channel = interaction.guild.get_channel(self.channel_id)
        if channel:
            await channel.edit(bitrate=val * 1000)
            await interaction.response.send_message(f"✅ Битрейт: {val} kbps", ephemeral=True)


class UserActionModal(ui.Modal, title="Действие"):
    user_id_input = ui.TextInput(label="ID или @упоминание", placeholder="123456789", min_length=1, max_length=50)
    def __init__(self, channel_id: int, action: str):
        super().__init__(title={
            "invite": "Пригласить", "kick": "Выгнать",
            "ban": "Забанить", "transfer": "Передать владение"
        }.get(action, "Действие"))
        self.channel_id = channel_id
        self.action = action
    async def on_submit(self, interaction: discord.Interaction):
        uid = self.user_id_input.value.strip().replace("<@", "").replace(">", "").replace("!", "")
        try:
            member = interaction.guild.get_member(int(uid))
            if not member:
                member = await interaction.guild.fetch_member(int(uid))
        except Exception:
            await interaction.response.send_message("❌ Пользователь не найден!", ephemeral=True); return

        channel = interaction.guild.get_channel(self.channel_id)
        if not channel:
            await interaction.response.send_message("❌ Канал не найден!", ephemeral=True); return

        if self.action == "invite":
            await channel.set_permissions(member, connect=True, view_channel=True)
            await interaction.response.send_message(f"✅ {member.mention} приглашён!", ephemeral=True)
        elif self.action == "kick":
            if member.voice and member.voice.channel == channel:
                await member.move_to(None)
                await interaction.response.send_message(f"✅ {member.mention} выгнан!", ephemeral=True)
            else:
                await interaction.response.send_message("❌ Не в этом канале!", ephemeral=True)
        elif self.action == "ban":
            await channel.set_permissions(member, connect=False, view_channel=False)
            if member.voice and member.voice.channel == channel:
                await member.move_to(None)
            await interaction.response.send_message(f"✅ {member.mention} забанен!", ephemeral=True)
        elif self.action == "transfer":
            session = SessionLocal()
            try:
                tc = session.query(TempVoiceChannel).filter_by(channel_id=self.channel_id).first()
                if tc: tc.owner_id = member.id; session.commit()
            finally: session.close()
            await interaction.response.send_message(f"✅ Владение передано {member.mention}!", ephemeral=True)


class VoiceChannels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_controls: Dict[int, int] = {}
        self.check_empty_channels.start()

    def cog_unload(self):
        self.check_empty_channels.cancel()

    @tasks.loop(seconds=30)
    async def check_empty_channels(self):
        session = SessionLocal()
        try:
            empty = session.query(TempVoiceChannel).all()
            for tc in empty:
                try:
                    channel = self.bot.get_channel(tc.channel_id)
                    if channel and len(channel.members) == 0:
                        self.active_controls.pop(tc.channel_id, None)
                        await channel.delete()
                        session.delete(tc)
                except Exception:
                    pass
            session.commit()
        except Exception:
            pass
        finally:
            session.close()

    @check_empty_channels.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

    @app_commands.command(name="voice_setup", description="Настроить систему голосовых каналов")
    @app_commands.checks.has_permissions(administrator=True)
    async def voice_setup(self, interaction: discord.Interaction,
                          creator_channel: discord.VoiceChannel,
                          default_name: str = "{user} канал",
                          default_limit: int = 0,
                          bitrate: int = 64):
        session = SessionLocal()
        try:
            config = session.query(VoiceChannelConfig).filter_by(
                guild_id=interaction.guild.id, creator_channel_id=creator_channel.id
            ).first()
            if config:
                config.default_name = default_name
                config.default_user_limit = default_limit
                config.bitrate = bitrate * 1000
                config.category_id = creator_channel.category.id if creator_channel.category else None
            else:
                config = VoiceChannelConfig(
                    guild_id=interaction.guild.id, creator_channel_id=creator_channel.id,
                    category_id=creator_channel.category.id if creator_channel.category else None,
                    default_name=default_name, default_user_limit=default_limit,
                    bitrate=bitrate * 1000,
                )
                session.add(config)
            session.commit()
            embed = discord.Embed(
                title="✅ Система голосовых каналов",
                description=f"**Канал-создатель:** {creator_channel.mention}\n"
                           f"**Шаблон:** `{default_name}`\n**Лимит:** {default_limit if default_limit else 'Без лимита'}\n"
                           f"**Битрейт:** {bitrate} kbps",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)
        finally:
            session.close()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if after.channel and after.channel != before.channel:
            session = SessionLocal()
            try:
                config = session.query(VoiceChannelConfig).filter_by(
                    guild_id=member.guild.id, creator_channel_id=after.channel.id
                ).first()
                if config:
                    channel_name = config.default_name.replace("{user}", member.display_name)
                    category = member.guild.get_channel(config.category_id) if config.category_id else after.channel.category
                    new_channel = await member.guild.create_voice_channel(
                        name=channel_name, category=category,
                        user_limit=config.default_user_limit, bitrate=config.bitrate or 64000,
                    )
                    await new_channel.set_permissions(member, manage_channels=True, connect=True, move_members=True)
                    await member.move_to(new_channel)

                    tc = TempVoiceChannel(
                        guild_id=member.guild.id, channel_id=new_channel.id,
                        owner_id=member.id, name=channel_name,
                        user_limit=config.default_user_limit,
                    )
                    session.add(tc)
                    session.commit()

                    if config.send_panel_on_create:
                        gc = session.query(GuildConfig).filter_by(guild_id=member.guild.id).first()
                        lang = str(gc.language) if gc and gc.language else "ru"
                        is_ru = lang == "ru"
                        embed = discord.Embed(
                            title="🎤 Панель управления" if is_ru else "🎤 Control Panel",
                            description=f"**{'Владелец' if is_ru else 'Owner'}:** {member.mention}\n{'Используйте кнопки для управления' if is_ru else 'Use buttons to control'}",
                            color=discord.Color.blurple()
                        )
                        embed.add_field(name="🔒/🔓", value="Закрыть/открыть" if is_ru else "Lock/Unlock", inline=True)
                        embed.add_field(name="👁️/👀", value="Скрыть/показать" if is_ru else "Hide/Show", inline=True)
                        embed.add_field(name="✏️", value="Переименовать" if is_ru else "Rename", inline=True)
                        embed.add_field(name="👥", value="Лимит" if is_ru else "User limit", inline=True)
                        embed.add_field(name="➕/➖", value="Пригласить/выгнать" if is_ru else "Invite/Kick", inline=True)
                        embed.add_field(name="🚫/👑", value="Забанить/передать" if is_ru else "Ban/Transfer", inline=True)
                        embed.add_field(name="🔊", value="Битрейт" if is_ru else "Bitrate", inline=True)
                        view = VoiceControlPanel(new_channel.id, lang)
                        msg = await new_channel.send(embed=embed, view=view)
                        self.active_controls[new_channel.id] = msg.id
            finally:
                session.close()

        if before.channel and before.channel != after.channel:
            session = SessionLocal()
            try:
                tc = session.query(TempVoiceChannel).filter_by(channel_id=before.channel.id).first()
                if tc and len(before.channel.members) == 0:
                    self.active_controls.pop(before.channel.id, None)
                    try:
                        await before.channel.delete()
                    except Exception:
                        pass
                    session.delete(tc)
                    session.commit()
            finally:
                session.close()


async def setup(bot):
    await bot.add_cog(VoiceChannels(bot))
