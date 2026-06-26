import discord
import datetime
from discord.ext import commands
from discord import app_commands, ui
from database import SessionLocal, GuildConfig


def ordinal(n: int) -> str:
    if 11 <= n % 100 <= 13:
        return f"{n}th"
    return {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")


class WelcomeConfigModal(ui.Modal, title="Настройка приветствий"):
    channel = ui.TextInput(label="Канал (ID или #)", placeholder="0 = системный канал", required=True, max_length=20)
    title = ui.TextInput(label="Заголовок", placeholder="Оставь пустым для авто", required=False, max_length=100)
    message = ui.TextInput(label="Текст приветствия", placeholder="Оставь пустым для авто", required=False, max_length=500, style=discord.TextStyle.paragraph)
    footer = ui.TextInput(label="Footer", placeholder="Оставь пустым для авто", required=False, max_length=100)
    image_url = ui.TextInput(label="URL изображения", placeholder="https://...", required=False, max_length=300)
    dm_message = ui.TextInput(label="ЛС (пусто = откл)", placeholder="Привет на {server}!", required=False, max_length=500)

    def __init__(self, config: GuildConfig):
        super().__init__(timeout=300)
        if config:
            self.channel.default = str(config.welcome_channel_id or "0")
            self.title.default = config.welcome_title or ""
            self.message.default = config.welcome_message or ""
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

            raw = self.channel.value.strip()
            if raw == "0" or not raw:
                config.welcome_channel_id = None
            else:
                try:
                    config.welcome_channel_id = int(raw)
                except ValueError:
                    if raw.startswith("<#") and raw.endswith(">"):
                        config.welcome_channel_id = int(raw[2:-1])
                    else:
                        await interaction.response.send_message("Укажи ID канала или `0` для системного", ephemeral=True)
                        return

            config.welcome_title = self.title.value.strip() or None
            config.welcome_message = self.message.value.strip() or None
            config.welcome_footer = self.footer.value.strip() or None
            config.welcome_image_url = self.image_url.value.strip() or None
            config.welcome_dm_message = self.dm_message.value.strip() or None
            config.welcome_dm_enabled = bool(self.dm_message.value.strip())
            config.welcome_enabled = True
            session.commit()

            ch = config.welcome_channel_id or (interaction.guild.system_channel.id if interaction.guild.system_channel else "—")
            await interaction.response.send_message(f"Приветствия сохранены! Канал: <#{config.welcome_channel_id}>" if config.welcome_channel_id else "Приветствия сохранены! Канал: системный", ephemeral=True)
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

    def _get_join_position(self, guild: discord.Guild, member: discord.Member) -> int:
        if not member.joined_at:
            return guild.member_count
        pos = 1
        if len(guild.members) < 5000:
            for m in guild.members:
                if m.joined_at and m.joined_at < member.joined_at:
                    pos += 1
            return pos
        return guild.member_count

    def _build_default_welcome(self, member: discord.Member, config, lang: str) -> discord.Embed:
        embed_color = int(config.embed_color) if config and config.embed_color else 0x5865F2
        g = member.guild

        is_ru = lang == "ru"

        greeting = f"Привет, {member.mention}! Добро пожаловать на **{g.name}**." if is_ru else f"Hey, {member.mention}! Welcome to **{g.name}**."

        pos = self._get_join_position(g, member)
        pos_text = f"Ты **{pos}{ordinal(pos)}** участник нашего сообщества!" if is_ru else f"You are the **{pos}{ordinal(pos)}** member of our community!"

        description_parts = [greeting, pos_text]

        if g.description:
            description_parts.append(f"\n> {g.description[:200]}")

        rules = g.rules_channel
        if rules:
            rules_text = f"📖 Ознакомься с правилами: {rules.mention}" if is_ru else f"📖 Check the rules: {rules.mention}"
            description_parts.append(rules_text)

        enjoy_text = "💬 Приятного общения!" if is_ru else "💬 Enjoy your stay!"
        description_parts.append(enjoy_text)

        embed = discord.Embed(
            title=f"Добро пожаловать, {member.display_name}!" if is_ru else f"Welcome, {member.display_name}!",
            description="\n".join(description_parts),
            color=discord.Color(embed_color),
            timestamp=datetime.datetime.now(datetime.timezone.utc),
        )

        if g.icon:
            embed.set_author(name=g.name, icon_url=g.icon.url)

        embed.set_thumbnail(url=member.display_avatar.url)

        embed.add_field(
            name="Регистрация" if is_ru else "Joined Discord",
            value=f"<t:{int(member.created_at.timestamp())}:R>",
            inline=True,
        )
        embed.add_field(
            name="Участников" if is_ru else "Members",
            value=str(g.member_count),
            inline=True,
        )

        if g.owner:
            embed.add_field(
                name="Владелец" if is_ru else "Owner",
                value=g.owner.mention,
                inline=True,
            )

        embed.set_footer(text=f"ID: {member.id}")

        return embed

    def _build_custom_welcome(self, member: discord.Member, config) -> discord.Embed:
        embed_color = int(config.embed_color) if config and config.embed_color else 0x5865F2
        g = member.guild

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

        embed.add_field(
            name="Участник с",
            value=f"<t:{int(datetime.datetime.now().timestamp())}:R>",
            inline=True,
        )
        embed.add_field(
            name="Всего участников",
            value=str(g.member_count),
            inline=True,
        )

        if g.icon:
            embed.set_author(name=g.name, icon_url=g.icon.url)

        return embed

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        session = SessionLocal()
        try:
            config = session.query(GuildConfig).filter_by(guild_id=member.guild.id).first()

            lang = str(config.language) if config and config.language else "ru"
            is_custom = config and config.welcome_message and config.welcome_message.strip()

            if config and not config.welcome_enabled and not is_custom:
                return

            channel_id = None
            if config and config.welcome_channel_id:
                channel_id = config.welcome_channel_id
            elif member.guild.system_channel:
                channel_id = member.guild.system_channel.id

            if not channel_id:
                return

            channel = member.guild.get_channel(channel_id)
            if not channel:
                return

            if is_custom:
                embed = self._build_custom_welcome(member, config)
            else:
                embed = self._build_default_welcome(member, config, lang)

            await channel.send(embed=embed)

            if config and config.welcome_dm_enabled and config.welcome_dm_message:
                try:
                    await member.send(self.format_text(config.welcome_dm_message, member))
                except Exception:
                    pass

            if config and config.welcome_auto_role_id:
                role = member.guild.get_role(int(config.welcome_auto_role_id))
                if role:
                    try:
                        await member.add_roles(role)
                    except Exception:
                        pass
        finally:
            session.close()

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        session = SessionLocal()
        try:
            config = session.query(GuildConfig).filter_by(guild_id=member.guild.id).first()

            lang = str(config.language) if config and config.language else "ru"

            if config and config.welcome_leave_enabled == False:
                return

            if config and config.welcome_leave_channel_id:
                channel_id = config.welcome_leave_channel_id
            elif member.guild.system_channel:
                channel_id = member.guild.system_channel.id
            else:
                return
            is_ru = lang == "ru"

            channel = member.guild.get_channel(channel_id)
            if not channel:
                return

            days = (datetime.datetime.now(datetime.timezone.utc) - (member.joined_at or datetime.datetime.now(datetime.timezone.utc))).days

            embed_color = int(config.embed_color) if config and config.embed_color else 0xE74C3C
            embed = discord.Embed(
                title="Пользователь покинул сервер" if is_ru else "User left the server",
                description=(
                    f"{member.mention} **{member.display_name}** {'покинул нас' if is_ru else 'left us'}\n"
                    f"{'Пробыл' if is_ru else 'Stayed'}: **{days} {'дн.' if is_ru else 'days'}**\n"
                    f"{'Участников' if is_ru else 'Members'}: **{member.guild.member_count}**"
                ),
                color=discord.Color(embed_color),
                timestamp=datetime.datetime.now(datetime.timezone.utc),
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=f"ID: {member.id}")
            await channel.send(embed=embed)
        finally:
            session.close()

    @app_commands.command(name="welcome_setup", description="Настройка приветствий")
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

    @app_commands.command(name="welcome_test", description="Тест приветствия")
    @app_commands.checks.has_permissions(administrator=True)
    async def welcome_test(self, interaction: discord.Interaction):
        await self.on_member_join(interaction.user)
        await interaction.response.send_message("Тестовое приветствие отправлено!", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Welcome(bot))
