import discord
import re
import datetime
from discord.ext import commands
from discord import app_commands, ui
from database import SessionLocal, GuildConfig, Warning, TempBan, AutoModConfig
from typing import Optional, Union


def get_msg(guild_id: int, key: str, **kwargs) -> str:
    from main import get_msg as main_get_msg
    return main_get_msg(guild_id, key, **kwargs)


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_dm_safe(self, user: Union[discord.Member, discord.User], embed: discord.Embed):
        try:
            await user.send(embed=embed)
        except:
            pass

    async def log_mod_action(self, guild: discord.Guild, embed: discord.Embed):
        session = SessionLocal()
        try:
            config = session.query(GuildConfig).filter_by(guild_id=guild.id).first()
            if config and config.mod_log_channel_id:
                channel = guild.get_channel(config.mod_log_channel_id)
                if channel and hasattr(channel, 'send'):
                    await channel.send(embed=embed)
        finally:
            session.close()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        session = SessionLocal()
        try:
            automod = session.query(AutoModConfig).filter_by(guild_id=message.guild.id).first()
            config = session.query(GuildConfig).filter_by(guild_id=message.guild.id).first()
            if not automod or not automod.enabled:
                return

            content = message.content
            violation = False
            reason = ""

            if automod.bad_words_enabled and automod.bad_words_list:
                bad_words = [w.strip().lower() for w in str(automod.bad_words_list).split(',') if w.strip()]
                if any(word in content.lower() for word in bad_words):
                    violation = True
                    reason = "Bad words"
                    action = automod.bad_words_action or "warn"

            if not violation and automod.caps_enabled:
                letters = sum(1 for c in content if c.isalpha())
                caps = sum(1 for c in content if c.isupper())
                if letters >= (automod.caps_min_length or 10) and (caps / letters * 100) >= (automod.caps_threshold or 70):
                    violation = True
                    reason = "Excessive caps"
                    action = automod.caps_action or "warn"

            if not violation and automod.anti_links_enabled:
                if re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content):
                    if not message.author.guild_permissions.manage_messages:
                        has_exempt = False
                        if automod.allowed_link_roles and message.author._roles:
                            for rid in automod.allowed_link_roles:
                                if rid in message.author._roles:
                                    has_exempt = True
                                    break
                        if not has_exempt:
                            violation = True
                            reason = "Links"
                            action = automod.anti_links_action or "warn"

            if violation and config:
                await message.delete()
                if action == 'mute':
                    dur = getattr(automod, 'spam_mute_duration', None) or 5
                    await message.author.timeout(datetime.timedelta(minutes=dur), reason=reason)
                elif action == 'kick':
                    await message.author.kick(reason=reason)
                elif action == 'ban':
                    await message.author.ban(reason=reason)
                else:
                    warn = Warning(
                        guild_id=message.guild.id, user_id=message.author.id,
                        reason=reason, moderator_id=self.bot.user.id,
                        timestamp=datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
                    )
                    session.add(warn)
                    session.commit()
        finally:
            session.close()

    @app_commands.command(name="kick", description="Kicks a member")
    @app_commands.checks.has_permissions(kick_members=True)
    @app_commands.choices(reason=[
        app_commands.Choice(name="Нарушение правил", value="Rule violation"),
        app_commands.Choice(name="Спам", value="Spam"),
        app_commands.Choice(name="Оскорбление", value="Harassment"),
        app_commands.Choice(name="Другое", value="Other"),
    ])
    async def kick_slash(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason", silent: bool = False):
        if not interaction.guild: return
        await member.kick(reason=reason)
        if not silent:
            embed = discord.Embed(
                title=get_msg(interaction.guild.id, 'kicked'),
                description=get_msg(interaction.guild.id, 'dm_kick', server=interaction.guild.name, reason=reason),
                color=discord.Color.orange(),
            )
            await self.send_dm_safe(member, embed)
        log_embed = discord.Embed(title="Member Kicked", color=discord.Color.orange(), timestamp=datetime.datetime.now(datetime.timezone.utc))
        log_embed.add_field(name="User", value=f"{member} ({member.id})")
        log_embed.add_field(name="Moderator", value=str(interaction.user))
        log_embed.add_field(name=get_msg(interaction.guild.id, 'reason'), value=reason)
        log_embed.add_field(name="Silent", value="Yes" if silent else "No")
        await self.log_mod_action(interaction.guild, log_embed)
        await interaction.response.send_message(get_msg(interaction.guild.id, 'kick_success', member=member.mention))

    @app_commands.command(name="ban", description="Bans a member")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.choices(reason=[
        app_commands.Choice(name="Нарушение правил", value="Rule violation"),
        app_commands.Choice(name="Спам/Рейд", value="Spam/Raid"),
        app_commands.Choice(name="Оскорбление", value="Harassment"),
        app_commands.Choice(name="Другое", value="Other"),
    ])
    async def ban_slash(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason", delete_messages_days: int = 0, silent: bool = False):
        if not interaction.guild: return
        await member.ban(reason=reason, delete_message_days=min(delete_messages_days, 7))
        if not silent:
            embed = discord.Embed(
                title=get_msg(interaction.guild.id, 'banned'),
                description=get_msg(interaction.guild.id, 'dm_ban', server=interaction.guild.name, reason=reason),
                color=discord.Color.red(),
            )
            await self.send_dm_safe(member, embed)
        log_embed = discord.Embed(title="Member Banned", color=discord.Color.red(), timestamp=datetime.datetime.now(datetime.timezone.utc))
        log_embed.add_field(name="User", value=f"{member} ({member.id})")
        log_embed.add_field(name="Moderator", value=str(interaction.user))
        log_embed.add_field(name=get_msg(interaction.guild.id, 'reason'), value=reason)
        log_embed.add_field(name="Del Msg Days", value=str(delete_messages_days))
        await self.log_mod_action(interaction.guild, log_embed)
        await interaction.response.send_message(get_msg(interaction.guild.id, 'ban_success', member=member.mention))

    @app_commands.command(name="unban", description="Unbans a member")
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban_slash(self, interaction: discord.Interaction, user_id: str, reason: str = "No reason"):
        if not interaction.guild: return
        user = await self.bot.fetch_user(int(user_id))
        await interaction.guild.unban(user, reason=reason)
        dm_embed = discord.Embed(
            title="Unbanned",
            description=get_msg(interaction.guild.id, 'dm_unban', server=interaction.guild.name, reason=reason),
            color=discord.Color.green(),
        )
        await self.send_dm_safe(user, dm_embed)
        log_embed = discord.Embed(title="Member Unbanned", color=discord.Color.green(), timestamp=datetime.datetime.now(datetime.timezone.utc))
        log_embed.add_field(name="User", value=f"{user} ({user_id})")
        log_embed.add_field(name="Moderator", value=str(interaction.user))
        log_embed.add_field(name=get_msg(interaction.guild.id, 'reason'), value=reason)
        await self.log_mod_action(interaction.guild, log_embed)
        await interaction.response.send_message(get_msg(interaction.guild.id, 'unban_success', user=user))

    @app_commands.command(name="mute", description="Mutes a member (Timeout)")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute_slash(self, interaction: discord.Interaction, member: discord.Member, minutes: int = 60, reason: str = "No reason"):
        if not interaction.guild: return
        duration = datetime.timedelta(minutes=minutes)
        await member.timeout(duration, reason=reason)
        embed = discord.Embed(
            title=get_msg(interaction.guild.id, 'muted'),
            description=get_msg(interaction.guild.id, 'dm_mute', server=interaction.guild.name, minutes=minutes, reason=reason),
            color=discord.Color.light_gray(),
        )
        await self.send_dm_safe(member, embed)
        log_embed = discord.Embed(title="Member Muted", color=discord.Color.light_gray(), timestamp=datetime.datetime.now(datetime.timezone.utc))
        log_embed.add_field(name="User", value=f"{member} ({member.id})")
        log_embed.add_field(name=get_msg(interaction.guild.id, 'duration'), value=f"{minutes} minutes")
        log_embed.add_field(name="Moderator", value=str(interaction.user))
        log_embed.add_field(name=get_msg(interaction.guild.id, 'reason'), value=reason)
        await self.log_mod_action(interaction.guild, log_embed)
        await interaction.response.send_message(get_msg(interaction.guild.id, 'mute_success', member=member.mention, minutes=minutes))

    @app_commands.command(name="unmute", description="Unmutes a member")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def unmute_slash(self, interaction: discord.Interaction, member: discord.Member):
        if not interaction.guild: return
        await member.timeout(None)
        dm_embed = discord.Embed(
            title=get_msg(interaction.guild.id, 'unmuted'),
            description=get_msg(interaction.guild.id, 'dm_unmute', server=interaction.guild.name),
            color=discord.Color.green(),
        )
        await self.send_dm_safe(member, dm_embed)
        log_embed = discord.Embed(title="Member Unmuted", color=discord.Color.green(), timestamp=datetime.datetime.now(datetime.timezone.utc))
        log_embed.add_field(name="User", value=f"{member} ({member.id})")
        log_embed.add_field(name="Moderator", value=str(interaction.user))
        await self.log_mod_action(interaction.guild, log_embed)
        await interaction.response.send_message(get_msg(interaction.guild.id, 'unmute_success', member=member.mention))

    @app_commands.command(name="warn", description="Warns a member")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def warn_slash(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
        if not interaction.guild: return
        session = SessionLocal()
        try:
            warn = Warning(guild_id=interaction.guild.id, user_id=member.id, reason=reason, moderator_id=interaction.user.id, timestamp=datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None))
            session.add(warn)
            session.commit()
            dm_embed = discord.Embed(
                title=get_msg(interaction.guild.id, 'warned'),
                description=get_msg(interaction.guild.id, 'dm_warn', server=interaction.guild.name, reason=reason),
                color=discord.Color.yellow(),
            )
            await self.send_dm_safe(member, dm_embed)
            await interaction.response.send_message(get_msg(interaction.guild.id, 'warn_success', member=member.mention, reason=reason))
        finally:
            session.close()

    @app_commands.command(name="clear", description="Clears messages")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear_slash(self, interaction: discord.Interaction, amount: int, member: Optional[discord.Member] = None):
        if not interaction.channel or not hasattr(interaction.channel, 'purge'): return
        await interaction.response.defer(ephemeral=True)
        if member:
            def check(m): return m.author.id == member.id
            deleted = await interaction.channel.purge(limit=amount, check=check)
        else:
            deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(get_msg(interaction.guild.id, 'clear_success', count=len(deleted)))

    @app_commands.command(name="tempban", description="Bans a member for a specific time")
    @app_commands.checks.has_permissions(ban_members=True)
    async def tempban_slash(self, interaction: discord.Interaction, member: discord.Member, duration: str, reason: str = "No reason"):
        if not interaction.guild: return
        seconds = 0
        match = re.match(r"(\d+)([smhd])", duration.lower())
        if not match:
            await interaction.response.send_message(get_msg(interaction.guild.id, 'invalid_duration'), ephemeral=True)
            return
        amount, unit = match.groups()
        amount = int(amount)
        if unit == 's': seconds = amount
        elif unit == 'm': seconds = amount * 60
        elif unit == 'h': seconds = amount * 3600
        elif unit == 'd': seconds = amount * 86400
        unban_time = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + datetime.timedelta(seconds=seconds)
        session = SessionLocal()
        try:
            new_tempban = TempBan(guild_id=interaction.guild.id, user_id=member.id, unban_time=unban_time, reason=reason)
            session.add(new_tempban)
            session.commit()
            await member.ban(reason=reason)
            embed = discord.Embed(
                title=get_msg(interaction.guild.id, 'banned'),
                description=get_msg(interaction.guild.id, 'dm_ban', server=interaction.guild.name, reason=reason),
                color=discord.Color.red(),
            )
            await self.send_dm_safe(member, embed)
            await interaction.response.send_message(get_msg(interaction.guild.id, 'tempban_success', member=member.mention, duration=duration))
        finally:
            session.close()

    @app_commands.command(name="automod_setup", description="Configure automod settings")
    @app_commands.checks.has_permissions(administrator=True)
    async def automod_setup(self, interaction: discord.Interaction,
                            enabled: bool,
                            anti_links: bool = False,
                            anti_spam: bool = False,
                            bad_words: bool = False,
                            caps_filter: bool = False,
                            spam_action: str = "warn",
                            link_action: str = "warn",
                            bad_words_action: str = "warn",
                            caps_action: str = "warn",
                            mute_minutes: int = 5):
        if not interaction.guild: return
        session = SessionLocal()
        try:
            config = session.query(AutoModConfig).filter_by(guild_id=interaction.guild.id).first()
            if not config:
                config = AutoModConfig(guild_id=interaction.guild.id)
                session.add(config)
            config.enabled = enabled
            config.anti_spam_enabled = anti_spam
            config.anti_links_enabled = anti_links
            config.bad_words_enabled = bad_words
            config.caps_enabled = caps_filter
            config.spam_action = spam_action
            config.anti_links_action = link_action
            config.bad_words_action = bad_words_action
            config.caps_action = caps_action
            config.spam_mute_duration = mute_minutes
            gc = session.query(GuildConfig).filter_by(guild_id=interaction.guild.id).first()
            if gc:
                gc.anti_spam = anti_spam
                gc.anti_links = anti_links
                gc.automod_enabled = enabled
                gc.automod_action = spam_action
                gc.mute_duration = mute_minutes
            session.commit()
            await interaction.response.send_message(get_msg(interaction.guild.id, 'automod_updated', enabled=enabled, anti_links=anti_links, action=spam_action))
        finally:
            session.close()


async def setup(bot):
    await bot.add_cog(Moderation(bot))
