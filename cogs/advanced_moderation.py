import discord
from discord.ext import commands, tasks
from discord import app_commands
from database import SessionLocal, Report, MessageLog, RaidProtection, SuspiciousJoin, GuildConfig, Warning
import datetime
from typing import Optional
import json

class AdvancedModeration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.spam_tracker = {}  # {user_id: [timestamps]}
        self.join_tracker = {}  # {guild_id: [timestamps]}
        self.check_raid_protection.start()

    def cog_unload(self):
        self.check_raid_protection.cancel()

    def get_msg(self, guild_id: int, key: str, **kwargs) -> str:
        from main import get_msg as main_get_msg
        return main_get_msg(guild_id, key, **kwargs)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        
        # Log message
        session = SessionLocal()
        try:
            attachments_data = []
            if message.attachments:
                attachments_data = [{"url": a.url, "filename": a.filename} for a in message.attachments]
            
            msg_log = MessageLog(
                guild_id=message.guild.id,
                message_id=message.id,
                channel_id=message.channel.id,
                user_id=message.author.id,
                content=message.content,
                attachments=json.dumps(attachments_data) if attachments_data else None
            )
            session.add(msg_log)
            session.commit()
            
            # Anti-spam check
            config = session.query(GuildConfig).filter_by(guild_id=message.guild.id).first()
            if config and config.anti_spam:
                now = datetime.datetime.now(datetime.timezone.utc).timestamp()
                user_key = f"{message.guild.id}_{message.author.id}"
                
                if user_key not in self.spam_tracker:
                    self.spam_tracker[user_key] = []
                
                # Remove old timestamps (older than 5 seconds)
                self.spam_tracker[user_key] = [t for t in self.spam_tracker[user_key] if now - t < 5]
                self.spam_tracker[user_key].append(now)
                
                # If more than 5 messages in 5 seconds
                if len(self.spam_tracker[user_key]) > 5:
                    try:
                        await message.delete()
                        duration = datetime.timedelta(minutes=5)
                        await message.author.timeout(duration, reason="Spam detected")
                        await message.channel.send(
                            f"⚠️ {message.author.mention} has been muted for spam (5 minutes)",
                            delete_after=5
                        )
                        self.spam_tracker[user_key] = []
                    except:
                        pass
        finally:
            session.close()

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
                
                # Send to log channel
                config = session.query(GuildConfig).filter_by(guild_id=message.guild.id).first()
                if config and config.log_channel_id:
                    log_channel = message.guild.get_channel(config.log_channel_id)
                    if log_channel:
                        embed = discord.Embed(
                            title="🗑️ Message Deleted",
                            color=discord.Color.red(),
                            timestamp=datetime.datetime.now(datetime.timezone.utc)
                        )
                        embed.add_field(name="Author", value=f"{message.author.mention} ({message.author.id})", inline=True)
                        embed.add_field(name="Channel", value=message.channel.mention, inline=True)
                        embed.add_field(name="Content", value=msg_log.content[:1024] if msg_log.content else "No content", inline=False)
                        
                        if msg_log.attachments:
                            attachments = json.loads(msg_log.attachments)
                            embed.add_field(name="Attachments", value="\n".join([a['url'] for a in attachments[:3]]), inline=False)
                        
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
                
                # Send to log channel
                config = session.query(GuildConfig).filter_by(guild_id=before.guild.id).first()
                if config and config.log_channel_id:
                    log_channel = before.guild.get_channel(config.log_channel_id)
                    if log_channel:
                        embed = discord.Embed(
                            title="📝 Message Edited",
                            color=discord.Color.orange(),
                            timestamp=datetime.datetime.now(datetime.timezone.utc)
                        )
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
        session = SessionLocal()
        try:
            # Track joins for raid protection
            guild_key = member.guild.id
            now = datetime.datetime.now(datetime.timezone.utc).timestamp()
            
            if guild_key not in self.join_tracker:
                self.join_tracker[guild_key] = []
            
            # Remove old timestamps (older than 60 seconds)
            self.join_tracker[guild_key] = [t for t in self.join_tracker[guild_key] if now - t < 60]
            self.join_tracker[guild_key].append(now)
            
            # Check raid protection
            raid_config = session.query(RaidProtection).filter_by(guild_id=member.guild.id).first()
            if raid_config and raid_config.enabled:
                if len(self.join_tracker[guild_key]) >= raid_config.join_threshold:
                    # Raid detected!
                    suspicious = SuspiciousJoin(guild_id=member.guild.id, user_id=member.id)
                    session.add(suspicious)
                    session.commit()
                    
                    # Take action
                    try:
                        if raid_config.action == "kick":
                            await member.kick(reason="Raid protection")
                        elif raid_config.action == "ban":
                            await member.ban(reason="Raid protection")
                        
                        # Notify in log channel
                        config = session.query(GuildConfig).filter_by(guild_id=member.guild.id).first()
                        if config and config.log_channel_id:
                            log_channel = member.guild.get_channel(config.log_channel_id)
                            if log_channel:
                                await log_channel.send(
                                    f"🚨 **RAID DETECTED!** {len(self.join_tracker[guild_key])} joins in 60 seconds. "
                                    f"Action taken: {raid_config.action} on {member.mention}"
                                )
                    except:
                        pass
        finally:
            session.close()

    @tasks.loop(minutes=5)
    async def check_raid_protection(self):
        # Clean up old join tracker data
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
        if not interaction.guild:
            return
        
        if user.id == interaction.user.id:
            await interaction.response.send_message("❌ You cannot report yourself", ephemeral=True)
            return
        
        session = SessionLocal()
        try:
            report = Report(
                guild_id=interaction.guild.id,
                reporter_id=interaction.user.id,
                reported_user_id=user.id,
                reason=reason,
                message_link=message_link,
                status="pending"
            )
            session.add(report)
            session.commit()
            
            # Send to report channel
            config = session.query(GuildConfig).filter_by(guild_id=interaction.guild.id).first()
            if config and config.report_channel_id:
                report_channel = interaction.guild.get_channel(config.report_channel_id)
                if report_channel:
                    embed = discord.Embed(
                        title="🚨 New Report",
                        color=discord.Color.red(),
                        timestamp=datetime.datetime.now(datetime.timezone.utc)
                    )
                    embed.add_field(name="Report ID", value=report.id, inline=True)
                    embed.add_field(name="Reporter", value=interaction.user.mention, inline=True)
                    embed.add_field(name="Reported User", value=user.mention, inline=True)
                    embed.add_field(name="Reason", value=reason, inline=False)
                    
                    if message_link:
                        embed.add_field(name="Message", value=f"[Jump to message]({message_link})", inline=False)
                    
                    embed.set_footer(text=f"Use /report_resolve {report.id} to resolve")
                    
                    await report_channel.send(embed=embed)
            
            await interaction.response.send_message(
                f"✅ Report submitted (ID: {report.id}). Moderators will review it soon.",
                ephemeral=True
            )
        finally:
            session.close()

    @app_commands.command(name="report_resolve", description="Resolve a report")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def report_resolve(self, interaction: discord.Interaction, report_id: int, action: str = "resolved"):
        if not interaction.guild:
            return
        
        session = SessionLocal()
        try:
            report = session.query(Report).filter_by(id=report_id, guild_id=interaction.guild.id).first()
            
            if not report:
                await interaction.response.send_message("❌ Report not found", ephemeral=True)
                return
            
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
        if not interaction.guild:
            return
        
        session = SessionLocal()
        try:
            pending_reports = session.query(Report).filter_by(
                guild_id=interaction.guild.id,
                status="pending"
            ).order_by(Report.created_at.desc()).limit(10).all()
            
            config = session.query(GuildConfig).filter_by(guild_id=interaction.guild.id).first()
            color_int = int(config.embed_color) if config and config.embed_color else 0x3498db
            
            embed = discord.Embed(
                title="🚨 Pending Reports",
                color=discord.Color(color_int)
            )
            
            if not pending_reports:
                embed.description = "No pending reports"
            else:
                for report in pending_reports:
                    try:
                        reporter = await self.bot.fetch_user(report.reporter_id)
                        reported = await self.bot.fetch_user(report.reported_user_id)
                        
                        embed.add_field(
                            name=f"Report #{report.id}",
                            value=f"**Reporter:** {reporter.mention}\n**Reported:** {reported.mention}\n**Reason:** {report.reason}\n**Time:** <t:{int(report.created_at.timestamp())}:R>",
                            inline=False
                        )
                    except:
                        continue
            
            await interaction.response.send_message(embed=embed)
        finally:
            session.close()

    @app_commands.command(name="slowmode", description="Set slowmode for a channel")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def slowmode(self, interaction: discord.Interaction, seconds: int, channel: Optional[discord.TextChannel] = None):
        if not interaction.guild:
            return
        
        target_channel = channel or interaction.channel
        
        if seconds < 0 or seconds > 21600:
            await interaction.response.send_message("❌ Slowmode must be between 0 and 21600 seconds (6 hours)", ephemeral=True)
            return
        
        await target_channel.edit(slowmode_delay=seconds)
        
        if seconds == 0:
            await interaction.response.send_message(f"✅ Slowmode disabled in {target_channel.mention}")
        else:
            await interaction.response.send_message(f"✅ Slowmode set to {seconds} seconds in {target_channel.mention}")

    @app_commands.command(name="massban", description="Ban multiple users by ID")
    @app_commands.checks.has_permissions(ban_members=True)
    async def massban(self, interaction: discord.Interaction, user_ids: str, reason: str = "Mass ban"):
        if not interaction.guild:
            return
        
        await interaction.response.defer()
        
        # Parse user IDs (comma or space separated)
        import re
        ids = re.findall(r'\d+', user_ids)
        
        if not ids:
            await interaction.followup.send("❌ No valid user IDs found")
            return
        
        banned_count = 0
        failed_count = 0
        
        for user_id in ids:
            try:
                user = await self.bot.fetch_user(int(user_id))
                await interaction.guild.ban(user, reason=reason)
                banned_count += 1
            except:
                failed_count += 1
        
        await interaction.followup.send(
            f"✅ Mass ban complete!\n"
            f"Banned: {banned_count}\n"
            f"Failed: {failed_count}"
        )

    @app_commands.command(name="masskick", description="Kick multiple users by ID")
    @app_commands.checks.has_permissions(kick_members=True)
    async def masskick(self, interaction: discord.Interaction, user_ids: str, reason: str = "Mass kick"):
        if not interaction.guild:
            return
        
        await interaction.response.defer()
        
        # Parse user IDs
        import re
        ids = re.findall(r'\d+', user_ids)
        
        if not ids:
            await interaction.followup.send("❌ No valid user IDs found")
            return
        
        kicked_count = 0
        failed_count = 0
        
        for user_id in ids:
            try:
                member = interaction.guild.get_member(int(user_id))
                if member:
                    await member.kick(reason=reason)
                    kicked_count += 1
                else:
                    failed_count += 1
            except:
                failed_count += 1
        
        await interaction.followup.send(
            f"✅ Mass kick complete!\n"
            f"Kicked: {kicked_count}\n"
            f"Failed: {failed_count}"
        )

    @app_commands.command(name="raid_protection", description="Configure raid protection")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.choices(action=[
        app_commands.Choice(name="Kick", value="kick"),
        app_commands.Choice(name="Ban", value="ban")
    ])
    async def raid_protection(
        self,
        interaction: discord.Interaction,
        enabled: bool,
        join_threshold: int = 5,
        action: str = "kick"
    ):
        if not interaction.guild:
            return
        
        session = SessionLocal()
        try:
            raid_config = session.query(RaidProtection).filter_by(guild_id=interaction.guild.id).first()
            
            if not raid_config:
                raid_config = RaidProtection(guild_id=interaction.guild.id)
                session.add(raid_config)
            
            raid_config.enabled = enabled
            raid_config.join_threshold = join_threshold
            raid_config.action = action
            
            session.commit()
            
            await interaction.response.send_message(
                f"✅ Raid protection {'enabled' if enabled else 'disabled'}\n"
                f"Threshold: {join_threshold} joins per minute\n"
                f"Action: {action}"
            )
        finally:
            session.close()

    @app_commands.command(name="warnings", description="View warnings for a user")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warnings(self, interaction: discord.Interaction, member: discord.Member):
        if not interaction.guild:
            return
        
        session = SessionLocal()
        try:
            warns = session.query(Warning).filter_by(
                guild_id=interaction.guild.id,
                user_id=member.id
            ).order_by(Warning.timestamp.desc()).all()
            
            config = session.query(GuildConfig).filter_by(guild_id=interaction.guild.id).first()
            color_int = int(config.embed_color) if config and config.embed_color else 0x3498db
            
            embed = discord.Embed(
                title=f"⚠️ Warnings for {member.display_name}",
                color=discord.Color(color_int)
            )
            
            if not warns:
                embed.description = "No warnings"
            else:
                for warn in warns[:10]:
                    try:
                        moderator = await self.bot.fetch_user(warn.moderator_id)
                        embed.add_field(
                            name=f"Warning #{warn.id}",
                            value=f"**Reason:** {warn.reason}\n**Moderator:** {moderator.mention}\n**Time:** <t:{int(warn.timestamp.timestamp())}:R>",
                            inline=False
                        )
                    except:
                        continue
            
            embed.set_footer(text=f"Total warnings: {len(warns)}")
            await interaction.response.send_message(embed=embed)
        finally:
            session.close()

async def setup(bot):
    await bot.add_cog(AdvancedModeration(bot))
