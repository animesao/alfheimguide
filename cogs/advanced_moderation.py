import discord
import json
import re
import logging
import datetime
from discord.ext import commands, tasks
from discord import app_commands
from database import SessionLocal, Report, MessageLog, RaidProtection, SuspiciousJoin, GuildConfig, Warning
from typing import Optional

logger = logging.getLogger("alfheim_bot.advanced_mod")


class AdvancedModeration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.spam_tracker = {}
        self.join_tracker = {}
        self._msg_log_cache = {}
        self._spam_config_cache = {}
        self.cache_cleanup.start()
        self.check_raid_protection.start()

    def cog_unload(self):
        self.check_raid_protection.cancel()
        self.cache_cleanup.cancel()

    @tasks.loop(minutes=30)
    async def cache_cleanup(self):
        self.spam_tracker.clear()
        self.join_tracker.clear()
        self._spam_config_cache.clear()

    def _get_guild_config(self, guild_id: int):
        if guild_id not in self._msg_log_cache:
            session = SessionLocal()
            try:
                config = session.query(GuildConfig).filter_by(guild_id=guild_id).first()
                if config:
                    self._msg_log_cache[guild_id] = {
                        'log_channel_id': config.log_channel_id,
                        'anti_spam': config.anti_spam,
                    }
                else:
                    self._msg_log_cache[guild_id] = {'log_channel_id': None, 'anti_spam': False}
            finally:
                session.close()
        return self._msg_log_cache[guild_id]

    def invalidate_cache(self, guild_id: int = None):
        if guild_id:
            self._msg_log_cache.pop(guild_id, None)
        else:
            self._msg_log_cache.clear()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        cfg = self._get_guild_config(message.guild.id)
        needs_log = cfg.get('log_channel_id') is not None

        if needs_log:
            attachments_data = []
            if message.attachments:
                attachments_data = [{"url": a.url, "filename": a.filename} for a in message.attachments]
            session = SessionLocal()
            try:
                msg_log = MessageLog(
                    guild_id=message.guild.id, message_id=message.id,
                    channel_id=message.channel.id, user_id=message.author.id,
                    content=message.content,
                    attachments=json.dumps(attachments_data) if attachments_data else None
                )
                session.add(msg_log)
                session.commit()
            finally:
                session.close()

        if cfg.get('anti_spam'):
            now = datetime.datetime.now(datetime.timezone.utc).timestamp()
            user_key = f"{message.guild.id}_{message.author.id}"
            if user_key not in self.spam_tracker:
                self.spam_tracker[user_key] = []
            self.spam_tracker[user_key] = [t for t in self.spam_tracker[user_key] if now - t < 5]
            self.spam_tracker[user_key].append(now)
            if len(self.spam_tracker[user_key]) > 5:
                try:
                    await message.delete()
                    await message.author.timeout(datetime.timedelta(minutes=5), reason="Spam detected")
                    await message.channel.send(f"⚠️ {message.author.mention} muted for spam (5m)", delete_after=5)
                    self.spam_tracker[user_key] = []
                except:
                    pass

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        session = SessionLocal()
        try:
            msg_log = session.query(MessageLog).filter_by(message_id=message.id).first()
            if msg_log:
                msg_log.deleted_at = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
                session.commit()
                cfg = self._get_guild_config(message.guild.id)
                if cfg.get('log_channel_id'):
                    log_channel = message.guild.get_channel(cfg['log_channel_id'])
                    if log_channel:
                        embed = discord.Embed(title="🗑️ Message Deleted", color=discord.Color.red(), timestamp=datetime.datetime.now(datetime.timezone.utc))
                        embed.add_field(name="Author", value=f"{message.author.mention} ({message.author.id})", inline=True)
                        embed.add_field(name="Channel", value=message.channel.mention, inline=True)
                        embed.add_field(name="Content", value=msg_log.content[:1024] if msg_log.content else "No content", inline=False)
                        if msg_log.attachments:
                            atts = json.loads(msg_log.attachments)
                            embed.add_field(name="Attachments", value="\n".join([a['url'] for a in atts[:3]]), inline=False)
                        await log_channel.send(embed=embed)
        finally:
            session.close()

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot or not before.guild or before.content == after.content:
            return
        session = SessionLocal()
        try:
            msg_log = session.query(MessageLog).filter_by(message_id=before.id).first()
            if msg_log:
                msg_log.old_content = msg_log.content
                msg_log.content = after.content
                msg_log.edited_at = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
                session.commit()
                cfg = self._get_guild_config(before.guild.id)
                if cfg.get('log_channel_id'):
                    log_channel = before.guild.get_channel(cfg['log_channel_id'])
                    if log_channel:
                        embed = discord.Embed(title="📝 Message Edited", color=discord.Color.orange(), timestamp=datetime.datetime.now(datetime.timezone.utc))
                        embed.add_field(name="Author", value=f"{before.author.mention} ({before.author.id})", inline=True)
                        embed.add_field(name="Channel", value=before.channel.mention, inline=True)
                        embed.add_field(name="Before", value=msg_log.old_content[:1024] if msg_log.old_content else "No content", inline=False)
                        embed.add_field(name="After", value=after.content[:1024], inline=False)
                        embed.add_field(name="Jump", value=f"[Go to message]({after.jump_url})", inline=False)
                        await log_channel.send(embed=embed)
        finally:
            session.close()

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild_key = member.guild.id
        now = datetime.datetime.now(datetime.timezone.utc).timestamp()
        if guild_key not in self.join_tracker:
            self.join_tracker[guild_key] = []
        self.join_tracker[guild_key] = [t for t in self.join_tracker[guild_key] if now - t < 60]
        self.join_tracker[guild_key].append(now)

        session = SessionLocal()
        try:
            raid_config = session.query(RaidProtection).filter_by(guild_id=member.guild.id).first()
            if raid_config and raid_config.enabled:
                if len(self.join_tracker[guild_key]) >= raid_config.join_threshold:
                    suspicious = SuspiciousJoin(guild_id=member.guild.id, user_id=member.id)
                    session.add(suspicious)
                    session.commit()
                    try:
                        if raid_config.action == "kick":
                            await member.kick(reason="Raid protection")
                        elif raid_config.action == "ban":
                            await member.ban(reason="Raid protection")
                        cfg = self._get_guild_config(member.guild.id)
                        if cfg.get('log_channel_id'):
                            log_channel = member.guild.get_channel(cfg['log_channel_id'])
                            if log_channel:
                                await log_channel.send(
                                    f"🚨 **RAID DETECTED!** {len(self.join_tracker[guild_key])} joins/60s. "
                                    f"Action: {raid_config.action} on {member.mention}"
                                )
                    except Exception as e:
                        pass
        finally:
            session.close()

    @tasks.loop(minutes=5)
    async def check_raid_protection(self):
        now = datetime.datetime.now(datetime.timezone.utc).timestamp()
        for guild_id in list(self.join_tracker.keys()):
            self.join_tracker[guild_id] = [t for t in self.join_tracker[guild_id] if now - t < 60]
            if not self.join_tracker[guild_id]:
                del self.join_tracker[guild_id]

    @check_raid_protection.before_loop
    async def before_check_raid_protection(self):
        await self.bot.wait_until_ready()

    @app_commands.command(name="report", description="Report a user to moderators")
    async def report(self, interaction: discord.Interaction, user: discord.Member, reason: str, message_link: Optional[str] = None):
        if not interaction.guild: return
        if user.id == interaction.user.id:
            await interaction.response.send_message("❌ You cannot report yourself", ephemeral=True); return
        session = SessionLocal()
        try:
            report = Report(guild_id=interaction.guild.id, reporter_id=interaction.user.id,
                           reported_user_id=user.id, reason=reason, message_link=message_link, status="pending")
            session.add(report)
            session.commit()
            config = session.query(GuildConfig).filter_by(guild_id=interaction.guild.id).first()
            if config and config.report_channel_id:
                rc = interaction.guild.get_channel(config.report_channel_id)
                if rc:
                    embed = discord.Embed(title="🚨 New Report", color=discord.Color.red(), timestamp=datetime.datetime.now(datetime.timezone.utc))
                    embed.add_field(name="ID", value=report.id, inline=True)
                    embed.add_field(name="Reporter", value=interaction.user.mention, inline=True)
                    embed.add_field(name="Reported", value=user.mention, inline=True)
                    embed.add_field(name="Reason", value=reason, inline=False)
                    if message_link:
                        embed.add_field(name="Message", value=f"[Jump]({message_link})", inline=False)
                    embed.set_footer(text=f"Use /report_resolve {report.id}")
                    await rc.send(embed=embed)
            await interaction.response.send_message(f"✅ Report submitted (ID: {report.id}).", ephemeral=True)
        finally:
            session.close()

    @app_commands.command(name="report_resolve", description="Resolve a report")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def report_resolve(self, interaction: discord.Interaction, report_id: int, action: str = "resolved"):
        if not interaction.guild: return
        session = SessionLocal()
        try:
            report = session.query(Report).filter_by(id=report_id, guild_id=interaction.guild.id).first()
            if not report:
                await interaction.response.send_message("❌ Report not found", ephemeral=True); return
            report.status = action
            report.moderator_id = interaction.user.id
            report.resolved_at = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
            session.commit()
            await interaction.response.send_message(f"✅ Report #{report_id} marked as {action}")
        finally:
            session.close()

    @app_commands.command(name="reports", description="View pending reports")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def reports(self, interaction: discord.Interaction):
        if not interaction.guild: return
        session = SessionLocal()
        try:
            pending = session.query(Report).filter_by(guild_id=interaction.guild.id, status="pending").order_by(Report.created_at.desc()).limit(10).all()
            config = session.query(GuildConfig).filter_by(guild_id=interaction.guild.id).first()
            color_int = int(config.embed_color) if config and config.embed_color else 0x3498db
            embed = discord.Embed(title="🚨 Pending Reports", color=discord.Color(color_int))
            if not pending:
                embed.description = "No pending reports"
            else:
                for r in pending:
                    try:
                        reporter = await self.bot.fetch_user(r.reporter_id)
                        reported = await self.bot.fetch_user(r.reported_user_id)
                        embed.add_field(name=f"Report #{r.id}", value=f"**Reporter:** {reporter.mention}\n**Reported:** {reported.mention}\n**Reason:** {r.reason}\n**Time:** <t:{int(r.created_at.timestamp())}:R>", inline=False)
                    except: continue
            await interaction.response.send_message(embed=embed)
        finally:
            session.close()

    @app_commands.command(name="slowmode", description="Set slowmode for a channel")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def slowmode(self, interaction: discord.Interaction, seconds: int = 0, channel: Optional[discord.TextChannel] = None):
        if not interaction.guild: return
        target = channel or interaction.channel
        if seconds < 0 or seconds > 21600:
            await interaction.response.send_message("❌ Slowmode must be 0-21600s", ephemeral=True); return
        await target.edit(slowmode_delay=seconds)
        if seconds == 0:
            await interaction.response.send_message(f"✅ Slowmode disabled in {target.mention}")
        else:
            await interaction.response.send_message(f"✅ Slowmode set to {seconds}s in {target.mention}")

    @app_commands.command(name="massban", description="Ban multiple users by ID")
    @app_commands.checks.has_permissions(ban_members=True)
    async def massban(self, interaction: discord.Interaction, user_ids: str, reason: str = "Mass ban"):
        if not interaction.guild: return
        await interaction.response.defer()
        ids = re.findall(r'\d+', user_ids)
        if not ids:
            await interaction.followup.send("❌ No valid user IDs found"); return
        banned = 0; failed = 0
        for uid in ids:
            try:
                user = await self.bot.fetch_user(int(uid))
                await interaction.guild.ban(user, reason=reason)
                banned += 1
            except: failed += 1
        await interaction.followup.send(f"✅ Massban: {banned} banned, {failed} failed")

    @app_commands.command(name="masskick", description="Kick multiple users by ID")
    @app_commands.checks.has_permissions(kick_members=True)
    async def masskick(self, interaction: discord.Interaction, user_ids: str, reason: str = "Mass kick"):
        if not interaction.guild: return
        await interaction.response.defer()
        ids = re.findall(r'\d+', user_ids)
        if not ids:
            await interaction.followup.send("❌ No valid user IDs found"); return
        kicked = 0; failed = 0
        for uid in ids:
            try:
                member = interaction.guild.get_member(int(uid))
                if member:
                    await member.kick(reason=reason)
                    kicked += 1
                else: failed += 1
            except: failed += 1
        await interaction.followup.send(f"✅ Masskick: {kicked} kicked, {failed} failed")

    @app_commands.command(name="raid_protection", description="Configure raid protection")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.choices(action=[
        app_commands.Choice(name="Kick", value="kick"),
        app_commands.Choice(name="Ban", value="ban")
    ])
    async def raid_protection(self, interaction: discord.Interaction, enabled: bool, join_threshold: int = 5, action: str = "kick"):
        if not interaction.guild: return
        session = SessionLocal()
        try:
            rc = session.query(RaidProtection).filter_by(guild_id=interaction.guild.id).first()
            if not rc:
                rc = RaidProtection(guild_id=interaction.guild.id)
                session.add(rc)
            rc.enabled = enabled
            rc.join_threshold = join_threshold
            rc.action = action
            session.commit()
            await interaction.response.send_message(f"✅ Raid protection {'enabled' if enabled else 'disabled'}\nThreshold: {join_threshold}/min\nAction: {action}")
        finally:
            session.close()

    @app_commands.command(name="warnings", description="View warnings for a user")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warnings(self, interaction: discord.Interaction, member: discord.Member):
        if not interaction.guild: return
        session = SessionLocal()
        try:
            warns = session.query(Warning).filter_by(guild_id=interaction.guild.id, user_id=member.id).order_by(Warning.timestamp.desc()).all()
            config = session.query(GuildConfig).filter_by(guild_id=interaction.guild.id).first()
            color_int = int(config.embed_color) if config and config.embed_color else 0x3498db
            embed = discord.Embed(title=f"⚠️ Warnings for {member.display_name}", color=discord.Color(color_int))
            if not warns:
                embed.description = "No warnings"
            else:
                for w in warns[:10]:
                    try:
                        mod = await self.bot.fetch_user(w.moderator_id)
                        embed.add_field(name=f"Warning #{w.id}", value=f"**Reason:** {w.reason}\n**Mod:** {mod.mention}\n**Time:** <t:{int(w.timestamp.timestamp())}:R>", inline=False)
                    except: continue
            embed.set_footer(text=f"Total: {len(warns)} warnings")
            await interaction.response.send_message(embed=embed)
        finally:
            session.close()

    @app_commands.command(name="refresh_cache", description="Сбросить кэш конфигов")
    @app_commands.checks.has_permissions(administrator=True)
    async def refresh_cache(self, interaction: discord.Interaction):
        self.invalidate_cache()
        await interaction.response.send_message("✅ Кэш конфигов сброшен", ephemeral=True)


async def setup(bot):
    await bot.add_cog(AdvancedModeration(bot))
