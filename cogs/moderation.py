import discord
from discord.ext import commands
from discord import app_commands
from database import SessionLocal, GuildConfig, Warning
import datetime
from typing import Optional

def get_msg(guild_id: int, key: str, **kwargs):
    from main import get_msg as main_get_msg
    return main_get_msg(guild_id, key, **kwargs)

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_dm_safe(self, member: discord.Member, embed: discord.Embed):
        try:
            await member.send(embed=embed)
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
            config = session.query(GuildConfig).filter_by(guild_id=message.guild.id).first()
            if not config or not config.automod_enabled:
                return

            if config.bad_words:
                bad_words = [w.strip().lower() for w in str(config.bad_words).split(',') if w.strip()]
                if any(word in message.content.lower() for word in bad_words):
                    await message.delete()
                    await message.channel.send(get_msg(message.guild.id, 'automod_bad_words', user=message.author.mention), delete_after=5)
                    return

            if config.anti_links:
                import re
                if re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.content):
                    if not message.author.guild_permissions.manage_messages:
                        await message.delete()
                        await message.channel.send(get_msg(message.guild.id, 'automod_links', user=message.author.mention), delete_after=5)
                        return
        finally:
            session.close()

    @app_commands.command(name="kick", description="Kicks a member")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick_slash(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
        if not interaction.guild: return
        embed = discord.Embed(title=get_msg(interaction.guild.id, 'kicked'), description=get_msg(interaction.guild.id, 'dm_kick', server=interaction.guild.name, reason=reason), color=discord.Color.orange())
        await self.send_dm_safe(member, embed)
        await member.kick(reason=reason)
        
        log_embed = discord.Embed(title="Member Kicked", color=discord.Color.orange())
        log_embed.add_field(name="User", value=f"{member} ({member.id})")
        log_embed.add_field(name="Moderator", value=str(interaction.user))
        log_embed.add_field(name=get_msg(interaction.guild.id, 'reason'), value=reason)
        await self.log_mod_action(interaction.guild, log_embed)
        await interaction.response.send_message(get_msg(interaction.guild.id, 'kick_success', member=member.mention))

    @app_commands.command(name="ban", description="Bans a member")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban_slash(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
        if not interaction.guild: return
        embed = discord.Embed(title=get_msg(interaction.guild.id, 'banned'), description=get_msg(interaction.guild.id, 'dm_ban', server=interaction.guild.name, reason=reason), color=discord.Color.red())
        await self.send_dm_safe(member, embed)
        await member.ban(reason=reason)
        
        log_embed = discord.Embed(title="Member Banned", color=discord.Color.red())
        log_embed.add_field(name="User", value=f"{member} ({member.id})")
        log_embed.add_field(name="Moderator", value=str(interaction.user))
        log_embed.add_field(name=get_msg(interaction.guild.id, 'reason'), value=reason)
        await self.log_mod_action(interaction.guild, log_embed)
        await interaction.response.send_message(get_msg(interaction.guild.id, 'ban_success', member=member.mention))

    @app_commands.command(name="unban", description="Unbans a member")
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban_slash(self, interaction: discord.Interaction, user_id: str, reason: str = "No reason"):
        if not interaction.guild: return
        user = await self.bot.fetch_user(int(user_id))
        await interaction.guild.unban(user, reason=reason)
        
        log_embed = discord.Embed(title="Member Unbanned", color=discord.Color.green())
        log_embed.add_field(name="User", value=f"{user} ({user_id})")
        log_embed.add_field(name="Moderator", value=str(interaction.user))
        log_embed.add_field(name=get_msg(interaction.guild.id, 'reason'), value=reason)
        await self.log_mod_action(interaction.guild, log_embed)
        await interaction.response.send_message(get_msg(interaction.guild.id, 'unban_success', user=user))

    @app_commands.command(name="mute", description="Mutes a member (Timeout)")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute_slash(self, interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "No reason"):
        if not interaction.guild: return
        duration = datetime.timedelta(minutes=minutes)
        await member.timeout(duration, reason=reason)
        
        embed = discord.Embed(title=get_msg(interaction.guild.id, 'muted'), description=get_msg(interaction.guild.id, 'dm_mute', server=interaction.guild.name, minutes=minutes, reason=reason), color=discord.Color.light_gray())
        await self.send_dm_safe(member, embed)
        
        log_embed = discord.Embed(title="Member Muted", color=discord.Color.light_gray())
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
        await interaction.response.send_message(get_msg(interaction.guild.id, 'unmute_success', member=member.mention))

    @app_commands.command(name="warn", description="Warns a member")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def warn_slash(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
        if not interaction.guild: return
        session = SessionLocal()
        try:
            new_warn = Warning(guild_id=interaction.guild.id, user_id=member.id, reason=reason, moderator_id=interaction.user.id, timestamp=datetime.datetime.utcnow())
            session.add(new_warn)
            session.commit()
            dm_embed = discord.Embed(title=get_msg(interaction.guild.id, 'warned'), description=get_msg(interaction.guild.id, 'dm_warn', server=interaction.guild.name, reason=reason), color=discord.Color.yellow())
            await self.send_dm_safe(member, dm_embed)
            await interaction.response.send_message(get_msg(interaction.guild.id, 'warn_success', member=member.mention, reason=reason))
        finally:
            session.close()

    @app_commands.command(name="clear", description="Clears messages")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear_slash(self, interaction: discord.Interaction, amount: int):
        if not interaction.channel or not hasattr(interaction.channel, 'purge'): return
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(get_msg(interaction.guild.id, 'clear_success', count=len(deleted)))

    @app_commands.command(name="automod_setup", description="Configure automod settings")
    @app_commands.checks.has_permissions(administrator=True)
    async def automod_setup(self, interaction: discord.Interaction, enabled: bool, anti_links: bool = False, bad_words: Optional[str] = None):
        if not interaction.guild: return
        session = SessionLocal()
        try:
            config = session.query(GuildConfig).filter_by(guild_id=interaction.guild.id).first()
            if not config:
                config = GuildConfig(guild_id=interaction.guild.id)
                session.add(config)
            
            config.automod_enabled = enabled
            config.anti_links = anti_links
            if bad_words is not None:
                config.bad_words = bad_words
            
            session.commit()
            await interaction.response.send_message(get_msg(interaction.guild.id, 'automod_updated', enabled=enabled, anti_links=anti_links))
        finally:
            session.close()

async def setup(bot):
    await bot.add_cog(Moderation(bot))
