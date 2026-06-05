import discord
import datetime
from discord.ext import commands
from discord import app_commands, ui
from database import SessionLocal, GuildConfig
from typing import Optional


class WelcomeConfigModal(ui.Modal, title="👋 Настройка приветствий"):
    channel_id = ui.TextInput(label="ID канала приветствий", placeholder="123456789", required=True, max_length=20)
    title = ui.TextInput(label="Заголовок", placeholder="Добро пожаловать!", default="Добро пожаловать!", required=True, max_length=100)
    message = ui.TextInput(label="Текст", placeholder="Добро пожаловать на {server}, {user}!", required=True, max_length=500, style=discord.TextStyle.paragraph)
    footer = ui.TextInput(label="Footer", placeholder="Приятного пребывания!", required=False, max_length=100)
    image_url = ui.TextInput(label="URL изображения", placeholder="https://...", required=False, max_length=300)
    dm_message = ui.TextInput(label="ЛС сообщение (пусто - откл)", placeholder="Привет на {server}!", required=False, max_length=500)

    def __init__(self, config: GuildConfig):
        super().__init__(timeout=300)
        if config:
            self.channel_id.default = str(config.welcome_channel_id or "")
            self.title.default = config.welcome_title or "Добро пожаловать!"
            self.message.default = config.welcome_message or "Добро пожаловать на {server}, {user}!"
            self.footer.default = config.welcome_footer or ""
            self.image_url.default = config.welcome_image_url or ""
            self.dm_message.default = config.welcome_dm_message or ""

    async def on_submit(self, interaction: discord.Interaction):
        session = SessionLocal()
        try:
            config = session.query(GuildConfig).filter_by(guild_id=interaction.guild_id).first()
            if not config:
                config = GuildConfig(guild_id=interaction.guild_id)
                session.add(config)
            try:
                config.welcome_channel_id = int(self.channel_id.value) if self.channel_id.value else None
            except:
                await interaction.response.send_message("❌ Неверный ID канала!", ephemeral=True)
                return
            config.welcome_title = self.title.value
            config.welcome_message = self.message.value
            config.welcome_footer = self.footer.value or None
            config.welcome_image_url = self.image_url.value or None
            config.welcome_dm_message = self.dm_message.value or None
            config.welcome_dm_enabled = bool(self.dm_message.value)
            config.welcome_enabled = True
            session.commit()
            await interaction.response.send_message(f"✅ Приветствия настроены! Канал: <#{config.welcome_channel_id}>", ephemeral=True)
        finally:
            session.close()


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def format_text(self, text: str, member: discord.Member) -> str:
        if not text:
            return ""
        return text.replace("{user}", member.mention) \
                   .replace("{username}", member.name) \
                   .replace("{displayname}", member.display_name) \
                   .replace("{server}", member.guild.name) \
                   .replace("{members}", str(member.guild.member_count)) \
                   .replace("{id}", str(member.id)) \
                   .replace("\\n", "\n")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        session = SessionLocal()
        try:
            config = session.query(GuildConfig).filter_by(guild_id=member.guild.id).first()
            if not config or not config.welcome_enabled:
                return

            if config.welcome_channel_id:
                channel = member.guild.get_channel(config.welcome_channel_id)
                if channel:
                    embed_color = int(config.embed_color) if config.embed_color else 0x3498db
                    embed = discord.Embed(
                        title=self.format_text(config.welcome_title or "Добро пожаловать!", member),
                        description=self.format_text(config.welcome_message or "Добро пожаловать на {server}, {user}!", member),
                        color=discord.Color(embed_color),
                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                    )
                    embed.set_thumbnail(url=member.display_avatar.url)
                    if config.welcome_footer:
                        embed.set_footer(text=self.format_text(config.welcome_footer, member))
                    if config.welcome_image_url:
                        embed.set_image(url=config.welcome_image_url)
                    embed.add_field(name="📅 Участник с", value=f"<t:{int(datetime.datetime.now().timestamp())}:R>", inline=True)
                    embed.add_field(name="👥 Всего участников", value=str(member.guild.member_count), inline=True)
                    await channel.send(embed=embed)

            if config.welcome_dm_enabled and config.welcome_dm_message:
                try:
                    await member.send(self.format_text(config.welcome_dm_message, member))
                except:
                    pass

            if config.welcome_auto_role_id:
                role = member.guild.get_role(int(config.welcome_auto_role_id))
                if role:
                    try:
                        await member.add_roles(role)
                    except:
                        pass
        finally:
            session.close()

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        session = SessionLocal()
        try:
            config = session.query(GuildConfig).filter_by(guild_id=member.guild.id).first()
            if not config or not config.welcome_leave_enabled:
                return
            if config.welcome_leave_channel_id:
                channel = member.guild.get_channel(config.welcome_leave_channel_id)
                if channel:
                    embed = discord.Embed(
                        title="👋 Пользователь покинул сервер",
                        description=f"**{member.display_name}** ({member.name}) покинул нас\n"
                                   f"👥 Участников: **{member.guild.member_count}**",
                        color=discord.Color.red(),
                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                    )
                    embed.set_thumbnail(url=member.display_avatar.url)
                    await channel.send(embed=embed)
        finally:
            session.close()

    @app_commands.command(name="welcome_setup", description="Detailed welcome system configuration")
    @app_commands.checks.has_permissions(administrator=True)
    async def welcome_setup(self, interaction: discord.Interaction):
        if not interaction.guild:
            return
        session = SessionLocal()
        try:
            config = session.query(GuildConfig).filter_by(guild_id=interaction.guild.id).first()
            if not config:
                config = GuildConfig(guild_id=interaction.guild.id)
                session.add(config)
                session.commit()
            await interaction.response.send_modal(WelcomeConfigModal(config))
        finally:
            session.close()

    @app_commands.command(name="welcome_test", description="Test welcome message")
    @app_commands.checks.has_permissions(administrator=True)
    async def welcome_test(self, interaction: discord.Interaction):
        await self.on_member_join(interaction.user)
        await interaction.response.send_message("✅ Тестовое приветствие отправлено!", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Welcome(bot))
