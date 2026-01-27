import discord
import asyncio
from discord.ext import commands
from discord import app_commands, ui
from database import SessionLocal, VoiceChannelConfig, TempVoiceChannel
from typing import Optional, Dict


class VoiceControlPanel(ui.View):
    def __init__(self, channel_id: int, owner_id: int):
        super().__init__(timeout=None)
        self.channel_id = channel_id
        self.owner_id = owner_id

    async def check_owner(self, interaction: discord.Interaction) -> bool:
        session = SessionLocal()
        try:
            temp_channel = session.query(TempVoiceChannel).filter_by(channel_id=self.channel_id).first()
            if not temp_channel:
                await interaction.response.send_message("Канал не найден.", ephemeral=True)
                return False
            if interaction.user.id != temp_channel.owner_id:
                await interaction.response.send_message("Только владелец канала может использовать эти настройки.", ephemeral=True)
                return False
            return True
        finally:
            session.close()

    @ui.button(label="🔒 Закрыть", style=discord.ButtonStyle.secondary, custom_id="vc_lock", row=0)
    async def lock_channel(self, interaction: discord.Interaction, button: ui.Button):
        if not await self.check_owner(interaction):
            return
        channel = interaction.guild.get_channel(self.channel_id)
        if channel:
            await channel.set_permissions(interaction.guild.default_role, connect=False)
            session = SessionLocal()
            try:
                temp_channel = session.query(TempVoiceChannel).filter_by(channel_id=self.channel_id).first()
                if temp_channel:
                    temp_channel.is_locked = True
                    session.commit()
            finally:
                session.close()
            await interaction.response.send_message("🔒 Канал закрыт для входа.", ephemeral=True)

    @ui.button(label="🔓 Открыть", style=discord.ButtonStyle.secondary, custom_id="vc_unlock", row=0)
    async def unlock_channel(self, interaction: discord.Interaction, button: ui.Button):
        if not await self.check_owner(interaction):
            return
        channel = interaction.guild.get_channel(self.channel_id)
        if channel:
            await channel.set_permissions(interaction.guild.default_role, connect=True)
            session = SessionLocal()
            try:
                temp_channel = session.query(TempVoiceChannel).filter_by(channel_id=self.channel_id).first()
                if temp_channel:
                    temp_channel.is_locked = False
                    session.commit()
            finally:
                session.close()
            await interaction.response.send_message("🔓 Канал открыт для входа.", ephemeral=True)

    @ui.button(label="👁️ Скрыть", style=discord.ButtonStyle.secondary, custom_id="vc_hide", row=0)
    async def hide_channel(self, interaction: discord.Interaction, button: ui.Button):
        if not await self.check_owner(interaction):
            return
        channel = interaction.guild.get_channel(self.channel_id)
        if channel:
            await channel.set_permissions(interaction.guild.default_role, view_channel=False)
            session = SessionLocal()
            try:
                temp_channel = session.query(TempVoiceChannel).filter_by(channel_id=self.channel_id).first()
                if temp_channel:
                    temp_channel.is_hidden = True
                    session.commit()
            finally:
                session.close()
            await interaction.response.send_message("👁️ Канал скрыт.", ephemeral=True)

    @ui.button(label="👀 Показать", style=discord.ButtonStyle.secondary, custom_id="vc_show", row=0)
    async def show_channel(self, interaction: discord.Interaction, button: ui.Button):
        if not await self.check_owner(interaction):
            return
        channel = interaction.guild.get_channel(self.channel_id)
        if channel:
            await channel.set_permissions(interaction.guild.default_role, view_channel=True)
            session = SessionLocal()
            try:
                temp_channel = session.query(TempVoiceChannel).filter_by(channel_id=self.channel_id).first()
                if temp_channel:
                    temp_channel.is_hidden = False
                    session.commit()
            finally:
                session.close()
            await interaction.response.send_message("👀 Канал виден.", ephemeral=True)

    @ui.button(label="✏️ Переименовать", style=discord.ButtonStyle.primary, custom_id="vc_rename", row=1)
    async def rename_channel(self, interaction: discord.Interaction, button: ui.Button):
        if not await self.check_owner(interaction):
            return
        modal = RenameModal(self.channel_id)
        await interaction.response.send_modal(modal)

    @ui.button(label="👥 Лимит", style=discord.ButtonStyle.primary, custom_id="vc_limit", row=1)
    async def set_limit(self, interaction: discord.Interaction, button: ui.Button):
        if not await self.check_owner(interaction):
            return
        modal = LimitModal(self.channel_id)
        await interaction.response.send_modal(modal)

    @ui.button(label="➕ Пригласить", style=discord.ButtonStyle.success, custom_id="vc_invite", row=1)
    async def invite_user(self, interaction: discord.Interaction, button: ui.Button):
        if not await self.check_owner(interaction):
            return
        modal = InviteModal(self.channel_id)
        await interaction.response.send_modal(modal)

    @ui.button(label="➖ Выгнать", style=discord.ButtonStyle.danger, custom_id="vc_kick", row=1)
    async def kick_user(self, interaction: discord.Interaction, button: ui.Button):
        if not await self.check_owner(interaction):
            return
        modal = KickModal(self.channel_id)
        await interaction.response.send_modal(modal)

    @ui.button(label="🚫 Забанить", style=discord.ButtonStyle.danger, custom_id="vc_ban", row=2)
    async def ban_user(self, interaction: discord.Interaction, button: ui.Button):
        if not await self.check_owner(interaction):
            return
        modal = BanModal(self.channel_id)
        await interaction.response.send_modal(modal)

    @ui.button(label="👑 Передать владение", style=discord.ButtonStyle.primary, custom_id="vc_transfer", row=2)
    async def transfer_ownership(self, interaction: discord.Interaction, button: ui.Button):
        if not await self.check_owner(interaction):
            return
        modal = TransferModal(self.channel_id)
        await interaction.response.send_modal(modal)


class RenameModal(ui.Modal, title='Переименовать канал'):
    new_name = ui.TextInput(
        label='Новое название канала',
        placeholder='Введите новое название...',
        min_length=1,
        max_length=100
    )

    def __init__(self, channel_id: int):
        super().__init__()
        self.channel_id = channel_id

    async def on_submit(self, interaction: discord.Interaction):
        channel = interaction.guild.get_channel(self.channel_id)
        if channel:
            await channel.edit(name=self.new_name.value)
            session = SessionLocal()
            try:
                temp_channel = session.query(TempVoiceChannel).filter_by(channel_id=self.channel_id).first()
                if temp_channel:
                    temp_channel.name = self.new_name.value
                    session.commit()
            finally:
                session.close()
            await interaction.response.send_message(f"✅ Канал переименован в **{self.new_name.value}**", ephemeral=True)
        else:
            await interaction.response.send_message("Канал не найден.", ephemeral=True)


class LimitModal(ui.Modal, title='Установить лимит пользователей'):
    limit = ui.TextInput(
        label='Лимит (0 = без лимита)',
        placeholder='Введите число от 0 до 99...',
        min_length=1,
        max_length=2
    )

    def __init__(self, channel_id: int):
        super().__init__()
        self.channel_id = channel_id

    async def on_submit(self, interaction: discord.Interaction):
        try:
            limit_value = int(self.limit.value)
            if limit_value < 0 or limit_value > 99:
                await interaction.response.send_message("Лимит должен быть от 0 до 99.", ephemeral=True)
                return
        except ValueError:
            await interaction.response.send_message("Введите корректное число.", ephemeral=True)
            return

        channel = interaction.guild.get_channel(self.channel_id)
        if channel:
            await channel.edit(user_limit=limit_value)
            session = SessionLocal()
            try:
                temp_channel = session.query(TempVoiceChannel).filter_by(channel_id=self.channel_id).first()
                if temp_channel:
                    temp_channel.user_limit = limit_value
                    session.commit()
            finally:
                session.close()
            await interaction.response.send_message(f"✅ Лимит установлен: **{limit_value}**", ephemeral=True)
        else:
            await interaction.response.send_message("Канал не найден.", ephemeral=True)


class InviteModal(ui.Modal, title='Пригласить пользователя'):
    user_id = ui.TextInput(
        label='ID пользователя или @упоминание',
        placeholder='Введите ID пользователя...',
        min_length=1,
        max_length=50
    )

    def __init__(self, channel_id: int):
        super().__init__()
        self.channel_id = channel_id

    async def on_submit(self, interaction: discord.Interaction):
        user_input = self.user_id.value.strip()
        user_input = user_input.replace('<@', '').replace('>', '').replace('!', '')
        try:
            user_id = int(user_input)
            member = interaction.guild.get_member(user_id)
            if not member:
                await interaction.response.send_message("Пользователь не найден на сервере.", ephemeral=True)
                return
        except ValueError:
            await interaction.response.send_message("Введите корректный ID пользователя.", ephemeral=True)
            return

        channel = interaction.guild.get_channel(self.channel_id)
        if channel:
            await channel.set_permissions(member, connect=True, view_channel=True)
            await interaction.response.send_message(f"✅ {member.mention} приглашён в канал.", ephemeral=True)
        else:
            await interaction.response.send_message("Канал не найден.", ephemeral=True)


class KickModal(ui.Modal, title='Выгнать пользователя'):
    user_id = ui.TextInput(
        label='ID пользователя или @упоминание',
        placeholder='Введите ID пользователя...',
        min_length=1,
        max_length=50
    )

    def __init__(self, channel_id: int):
        super().__init__()
        self.channel_id = channel_id

    async def on_submit(self, interaction: discord.Interaction):
        user_input = self.user_id.value.strip()
        user_input = user_input.replace('<@', '').replace('>', '').replace('!', '')
        try:
            user_id = int(user_input)
            member = interaction.guild.get_member(user_id)
            if not member:
                await interaction.response.send_message("Пользователь не найден на сервере.", ephemeral=True)
                return
        except ValueError:
            await interaction.response.send_message("Введите корректный ID пользователя.", ephemeral=True)
            return

        channel = interaction.guild.get_channel(self.channel_id)
        if channel and member.voice and member.voice.channel == channel:
            await member.move_to(None)
            await interaction.response.send_message(f"✅ {member.mention} выгнан из канала.", ephemeral=True)
        else:
            await interaction.response.send_message("Пользователь не в этом канале.", ephemeral=True)


class BanModal(ui.Modal, title='Забанить пользователя в канале'):
    user_id = ui.TextInput(
        label='ID пользователя или @упоминание',
        placeholder='Введите ID пользователя...',
        min_length=1,
        max_length=50
    )

    def __init__(self, channel_id: int):
        super().__init__()
        self.channel_id = channel_id

    async def on_submit(self, interaction: discord.Interaction):
        user_input = self.user_id.value.strip()
        user_input = user_input.replace('<@', '').replace('>', '').replace('!', '')
        try:
            user_id = int(user_input)
            member = interaction.guild.get_member(user_id)
            if not member:
                await interaction.response.send_message("Пользователь не найден на сервере.", ephemeral=True)
                return
        except ValueError:
            await interaction.response.send_message("Введите корректный ID пользователя.", ephemeral=True)
            return

        channel = interaction.guild.get_channel(self.channel_id)
        if channel:
            await channel.set_permissions(member, connect=False, view_channel=False)
            if member.voice and member.voice.channel == channel:
                await member.move_to(None)
            await interaction.response.send_message(f"✅ {member.mention} забанен в канале.", ephemeral=True)
        else:
            await interaction.response.send_message("Канал не найден.", ephemeral=True)


class TransferModal(ui.Modal, title='Передать владение каналом'):
    user_id = ui.TextInput(
        label='ID нового владельца или @упоминание',
        placeholder='Введите ID пользователя...',
        min_length=1,
        max_length=50
    )

    def __init__(self, channel_id: int):
        super().__init__()
        self.channel_id = channel_id

    async def on_submit(self, interaction: discord.Interaction):
        user_input = self.user_id.value.strip()
        user_input = user_input.replace('<@', '').replace('>', '').replace('!', '')
        try:
            user_id = int(user_input)
            member = interaction.guild.get_member(user_id)
            if not member:
                await interaction.response.send_message("Пользователь не найден на сервере.", ephemeral=True)
                return
        except ValueError:
            await interaction.response.send_message("Введите корректный ID пользователя.", ephemeral=True)
            return

        session = SessionLocal()
        try:
            temp_channel = session.query(TempVoiceChannel).filter_by(channel_id=self.channel_id).first()
            if temp_channel:
                temp_channel.owner_id = member.id
                session.commit()
                await interaction.response.send_message(f"✅ Владение передано {member.mention}.", ephemeral=True)
            else:
                await interaction.response.send_message("Канал не найден.", ephemeral=True)
        finally:
            session.close()


class VoiceChannels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_controls: Dict[int, int] = {}

    @app_commands.command(name="voice_setup", description="Настроить систему кастомных голосовых каналов")
    @app_commands.checks.has_permissions(administrator=True)
    async def voice_setup(self, interaction: discord.Interaction,
                          creator_channel: discord.VoiceChannel,
                          control_channel: Optional[discord.TextChannel] = None,
                          default_name: str = "{user} канал",
                          default_limit: int = 0):
        session = SessionLocal()
        try:
            config = session.query(VoiceChannelConfig).filter_by(
                guild_id=interaction.guild.id,
                creator_channel_id=creator_channel.id
            ).first()
            
            if config:
                config.default_name = default_name
                config.default_user_limit = default_limit
                config.control_channel_id = control_channel.id if control_channel else None
                config.category_id = creator_channel.category.id if creator_channel.category else None
            else:
                config = VoiceChannelConfig(
                    guild_id=interaction.guild.id,
                    creator_channel_id=creator_channel.id,
                    category_id=creator_channel.category.id if creator_channel.category else None,
                    default_name=default_name,
                    default_user_limit=default_limit,
                    control_channel_id=control_channel.id if control_channel else None
                )
                session.add(config)
            
            session.commit()
            
            embed = discord.Embed(
                title="✅ Система голосовых каналов настроена",
                description=f"**Канал-создатель:** {creator_channel.mention}\n"
                           f"**Канал управления:** {control_channel.mention if control_channel else 'Не указан'}\n"
                           f"**Шаблон названия:** `{default_name}`\n"
                           f"**Лимит по умолчанию:** {default_limit if default_limit > 0 else 'Без лимита'}",
                color=discord.Color.green()
            )
            embed.set_footer(text="Войдите в канал-создатель, чтобы создать свой голосовой канал!")
            await interaction.response.send_message(embed=embed)
        finally:
            session.close()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if after.channel and after.channel != before.channel:
            session = SessionLocal()
            try:
                config = session.query(VoiceChannelConfig).filter_by(
                    guild_id=member.guild.id,
                    creator_channel_id=after.channel.id
                ).first()
                
                if config:
                    channel_name = config.default_name.replace("{user}", member.display_name)
                    category = member.guild.get_channel(config.category_id) if config.category_id else after.channel.category
                    
                    new_channel = await member.guild.create_voice_channel(
                        name=channel_name,
                        category=category,
                        user_limit=config.default_user_limit
                    )
                    
                    await new_channel.set_permissions(member, manage_channels=True, connect=True, move_members=True)
                    
                    await member.move_to(new_channel)
                    
                    temp_channel = TempVoiceChannel(
                        guild_id=member.guild.id,
                        channel_id=new_channel.id,
                        owner_id=member.id,
                        name=channel_name,
                        user_limit=config.default_user_limit
                    )
                    session.add(temp_channel)
                    session.commit()
                    
                    embed = discord.Embed(
                        title="🎤 Панель управления каналом",
                        description=f"**Владелец:** {member.mention}\n\n"
                                   "Используйте кнопки ниже для управления своим каналом:",
                        color=discord.Color.blurple()
                    )
                    embed.add_field(
                        name="🔒 Закрыть/Открыть",
                        value="Запретить/Разрешить вход",
                        inline=True
                    )
                    embed.add_field(
                        name="👁️ Скрыть/Показать",
                        value="Скрыть канал от всех",
                        inline=True
                    )
                    embed.add_field(
                        name="✏️ Переименовать",
                        value="Изменить название канала",
                        inline=True
                    )
                    embed.add_field(
                        name="👥 Лимит",
                        value="Установить макс. участников",
                        inline=True
                    )
                    embed.add_field(
                        name="➕ Пригласить",
                        value="Дать доступ пользователю",
                        inline=True
                    )
                    embed.add_field(
                        name="➖ Выгнать",
                        value="Выгнать из канала",
                        inline=True
                    )
                    embed.add_field(
                        name="🚫 Забанить",
                        value="Заблокировать доступ",
                        inline=True
                    )
                    embed.add_field(
                        name="👑 Передать",
                        value="Передать владение",
                        inline=True
                    )
                    
                    view = VoiceControlPanel(new_channel.id, member.id)
                    msg = await new_channel.send(embed=embed, view=view)
                    self.active_controls[new_channel.id] = msg.id
            finally:
                session.close()
        
        if before.channel and before.channel != after.channel:
            session = SessionLocal()
            try:
                temp_channel = session.query(TempVoiceChannel).filter_by(channel_id=before.channel.id).first()
                if temp_channel:
                    if len(before.channel.members) == 0:
                        if before.channel.id in self.active_controls:
                            del self.active_controls[before.channel.id]
                        
                        await before.channel.delete()
                        session.delete(temp_channel)
                        session.commit()
            finally:
                session.close()


async def setup(bot):
    await bot.add_cog(VoiceChannels(bot))
