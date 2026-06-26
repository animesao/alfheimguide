import discord
import datetime
from discord.ext import commands, tasks
from discord import app_commands
from database import SessionLocal, UserActivity, MessageLog, UserLevel, GuildConfig
from typing import Optional
from collections import defaultdict


class Statistics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.daily_stats = defaultdict(lambda: defaultdict(int))
        self.voice_tracker = {}
        self.auto_save_stats.start()

    def cog_unload(self):
        self.auto_save_stats.cancel()

    @tasks.loop(minutes=5)
    async def auto_save_stats(self):
        now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        session = SessionLocal()
        try:
            for guild_id, users in list(self.daily_stats.items()):
                for user_id, count in list(users.items()):
                    if count > 0:
                        existing = session.query(UserActivity).filter_by(
                            guild_id=guild_id, user_id=user_id, date=today
                        ).first()
                        if existing:
                            existing.message_count += count
                        else:
                            session.add(UserActivity(
                                guild_id=guild_id, user_id=user_id,
                                date=today, message_count=count
                            ))
                self.daily_stats[guild_id].clear()
            session.commit()
        finally:
            session.close()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        self.daily_stats[message.guild.id][message.author.id] += 1

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if member.bot:
            return
        key = f"{member.guild.id}_{member.id}"
        now = datetime.datetime.now(datetime.timezone.utc)
        if after.channel and not before.channel:
            self.voice_tracker[key] = now
        elif not after.channel and before.channel and key in self.voice_tracker:
            minutes = int((now - self.voice_tracker.pop(key)).total_seconds() / 60)
            if minutes > 0:
                session = SessionLocal()
                try:
                    activity = UserActivity(
                        guild_id=member.guild.id, user_id=member.id,
                        date=now.replace(tzinfo=None), message_count=0, voice_minutes=minutes
                    )
                    session.add(activity)
                    session.commit()
                finally:
                    session.close()

    @app_commands.command(name="topmembers", description="View most active members")
    async def topmembers(self, interaction: discord.Interaction, timeframe: str = "today"):
        if not interaction.guild: return
        session = SessionLocal()
        try:
            config = session.query(GuildConfig).filter_by(guild_id=interaction.guild.id).first()
            if not config or not config.stats_enabled:
                await interaction.response.send_message("📊 Statistics are disabled", ephemeral=True); return
            color_int = int(config.embed_color) if config and config.embed_color else 0x3498db
            now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
            if timeframe == "today":
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                title = "📊 Most Active Today"
            elif timeframe == "week":
                start_date = now - datetime.timedelta(days=7)
                title = "📊 Most Active This Week"
            elif timeframe == "month":
                start_date = now - datetime.timedelta(days=30)
                title = "📊 Most Active This Month"
            else:
                start_date = datetime.datetime(2020, 1, 1)
                title = "📊 Most Active All Time"
            from sqlalchemy import func
            results = session.query(
                MessageLog.user_id, func.count(MessageLog.id)
            ).filter(
                MessageLog.guild_id == interaction.guild.id,
                MessageLog.created_at >= start_date
            ).group_by(MessageLog.user_id).order_by(func.count(MessageLog.id).desc()).limit(10).all()
            sorted_users = [(r[0], r[1]) for r in results]
            embed = discord.Embed(title=title, color=discord.Color(color_int))
            if not sorted_users:
                embed.description = "No activity data yet"
            else:
                leaderboard_text = ""
                for idx, (user_id, count) in enumerate(sorted_users, 1):
                    member = interaction.guild.get_member(user_id)
                    if member:
                        medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
                        leaderboard_text += f"{medal} **{member.display_name}** - {count:,} messages\n"
                embed.description = leaderboard_text
            await interaction.response.send_message(embed=embed)
        finally:
            session.close()

    @app_commands.command(name="channelstats", description="View channel activity statistics")
    async def channelstats(self, interaction: discord.Interaction, days: int = 7):
        if not interaction.guild: return
        if days < 1 or days > 30:
            await interaction.response.send_message("❌ Days must be between 1 and 30", ephemeral=True); return
        session = SessionLocal()
        try:
            config = session.query(GuildConfig).filter_by(guild_id=interaction.guild.id).first()
            color_int = int(config.embed_color) if config and config.embed_color else 0x3498db
            start_date = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) - datetime.timedelta(days=days)
            messages = session.query(MessageLog).filter(
                MessageLog.guild_id == interaction.guild.id,
                MessageLog.created_at >= start_date
            ).all()
            channel_counts = defaultdict(int)
            for msg in messages:
                channel_counts[msg.channel_id] += 1
            sorted_channels = sorted(channel_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            embed = discord.Embed(title=f"📊 Channel Activity (Last {days} Days)", color=discord.Color(color_int))
            if not sorted_channels:
                embed.description = "No activity data yet"
            else:
                stats_text = ""
                total_messages = sum(channel_counts.values())
                for idx, (channel_id, count) in enumerate(sorted_channels, 1):
                    channel = interaction.guild.get_channel(channel_id)
                    if channel:
                        percentage = (count / total_messages * 100) if total_messages > 0 else 0
                        bar = "█" * int(percentage / 10) + "░" * (10 - int(percentage / 10))
                        stats_text += f"**{idx}. {channel.mention}**\n{bar} {percentage:.1f}% ({count:,} msgs)\n\n"
                embed.description = stats_text
                embed.set_footer(text=f"Total: {total_messages:,} messages")
            await interaction.response.send_message(embed=embed)
        finally:
            session.close()

    @app_commands.command(name="serverstats", description="View detailed server statistics")
    async def serverstats(self, interaction: discord.Interaction):
        if not interaction.guild: return
        await interaction.response.defer()
        session = SessionLocal()
        try:
            config = session.query(GuildConfig).filter_by(guild_id=interaction.guild.id).first()
            color_int = int(config.embed_color) if config and config.embed_color else 0x3498db
            guild = interaction.guild
            now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_start = now - datetime.timedelta(days=7)

            total_messages = session.query(MessageLog).filter_by(guild_id=guild.id).count()
            today_messages = session.query(MessageLog).filter(
                MessageLog.guild_id == guild.id, MessageLog.created_at >= today_start
            ).count()
            week_messages = session.query(MessageLog).filter(
                MessageLog.guild_id == guild.id, MessageLog.created_at >= week_start
            ).count()

            total_members = guild.member_count
            bots = len([m for m in guild.members if m.bot])
            humans = total_members - bots
            online = len([m for m in guild.members if m.status != discord.Status.offline])
            new_today = len([m for m in guild.members if m.joined_at and m.joined_at.replace(tzinfo=None) >= today_start])

            embed = discord.Embed(
                title=f"📊 Server Statistics - {guild.name}",
                color=discord.Color(color_int),
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )
            if guild.icon:
                embed.set_thumbnail(url=guild.icon.url)

            embed.add_field(name="👥 Members", value=f"Total: **{total_members:,}**\nHumans: **{humans:,}**\nBots: **{bots:,}**\nOnline: **{online:,}**\nNew Today: **{new_today:,}**", inline=True)
            embed.add_field(name="💬 Messages", value=f"Total: **{total_messages:,}**\nToday: **{today_messages:,}**\nThis Week: **{week_messages:,}**", inline=True)
            embed.add_field(name="📝 Channels", value=f"Text: **{len(guild.text_channels)}**\nVoice: **{len(guild.voice_channels)}**\nCategories: **{len(guild.categories)}**", inline=True)
            embed.add_field(name="🎭 Roles", value=f"**{len(guild.roles)}** roles", inline=True)
            embed.add_field(name="😀 Emojis", value=f"**{len(guild.emojis)}** emojis", inline=True)
            embed.add_field(name="🚀 Boosts", value=f"Level **{guild.premium_tier}**\n**{guild.premium_subscription_count}** boosts", inline=True)

            week_days = []
            for i in range(7):
                day_start = now - datetime.timedelta(days=6-i)
                day_start = day_start.replace(hour=0, minute=0, second=0, microsecond=0)
                day_end = day_start + datetime.timedelta(days=1)
                day_messages = session.query(MessageLog).filter(
                    MessageLog.guild_id == guild.id,
                    MessageLog.created_at >= day_start,
                    MessageLog.created_at < day_end
                ).count()
                week_days.append(day_messages)

            max_messages = max(week_days) if week_days else 1
            days_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            activity_graph = ""
            for idx, count in enumerate(week_days):
                bar_length = int((count / max_messages * 10)) if max_messages > 0 else 0
                bar = "█" * bar_length + "░" * (10 - bar_length)
                activity_graph += f"{days_names[idx]}: {bar} {count}\n"

            embed.add_field(name="📈 Activity (Last 7 Days)", value=f"```{activity_graph}```", inline=False)
            await interaction.followup.send(embed=embed)
        finally:
            session.close()

    @app_commands.command(name="userstats", description="View detailed user statistics")
    async def userstats(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        if not interaction.guild: return
        target = member or interaction.user
        session = SessionLocal()
        try:
            config = session.query(GuildConfig).filter_by(guild_id=interaction.guild.id).first()
            color_int = int(config.embed_color) if config and config.embed_color else 0x3498db

            total_messages = session.query(MessageLog).filter_by(guild_id=interaction.guild.id, user_id=target.id).count()
            today_start = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None).replace(hour=0, minute=0, second=0, microsecond=0)
            today_messages = session.query(MessageLog).filter(
                MessageLog.guild_id == interaction.guild.id, MessageLog.user_id == target.id,
                MessageLog.created_at >= today_start
            ).count()

            user_level = session.query(UserLevel).filter_by(guild_id=interaction.guild.id, user_id=target.id).first()
            level = user_level.level if user_level else 1
            xp = user_level.xp if user_level else 0

            all_users = session.query(UserLevel).filter_by(guild_id=interaction.guild.id).all()
            sorted_users = sorted(all_users, key=lambda u: (u.level or 1, u.xp or 0), reverse=True)
            rank = next((i + 1 for i, u in enumerate(sorted_users) if u.user_id == target.id), 0)

            messages = session.query(MessageLog).filter_by(guild_id=interaction.guild.id, user_id=target.id).all()
            channel_counts = defaultdict(int)
            for msg in messages:
                channel_counts[msg.channel_id] += 1
            most_active_channel = None
            if channel_counts:
                mid = max(channel_counts, key=channel_counts.get)
                most_active_channel = interaction.guild.get_channel(mid)

            embed = discord.Embed(title=f"📊 Statistics for {target.display_name}", color=discord.Color(color_int))
            embed.set_thumbnail(url=target.display_avatar.url)
            embed.add_field(name="💬 Messages", value=f"Total: **{total_messages:,}**\nToday: **{today_messages:,}**", inline=True)
            embed.add_field(name="📊 Level", value=f"Level: **{level}**\nXP: **{xp:,}**\nRank: **#{rank}**", inline=True)
            if most_active_channel:
                embed.add_field(name="📝 Most Active", value=f"{most_active_channel.mention}\n**{channel_counts[most_active_channel.id]:,}** msgs", inline=True)
            if target.joined_at:
                days_in_server = (datetime.datetime.now(datetime.timezone.utc) - target.joined_at).days
                embed.add_field(name="📅 Member For", value=f"**{days_in_server}** days", inline=True)
                avg_messages = total_messages / max(days_in_server, 1)
                embed.add_field(name="📈 Average", value=f"**{avg_messages:.1f}** msgs/day", inline=True)
            await interaction.response.send_message(embed=embed)
        finally:
            session.close()

    @app_commands.command(name="activity_graph", description="View server activity graph")
    async def activity_graph(self, interaction: discord.Interaction, days: int = 7):
        if not interaction.guild: return
        if days < 1 or days > 30:
            await interaction.response.send_message("❌ Days must be between 1 and 30", ephemeral=True); return
        session = SessionLocal()
        try:
            config = session.query(GuildConfig).filter_by(guild_id=interaction.guild.id).first()
            color_int = int(config.embed_color) if config and config.embed_color else 0x3498db
            now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
            daily_counts = []
            for i in range(days):
                day_start = now - datetime.timedelta(days=days-1-i)
                day_start = day_start.replace(hour=0, minute=0, second=0, microsecond=0)
                day_end = day_start + datetime.timedelta(days=1)
                cnt = session.query(MessageLog).filter(
                    MessageLog.guild_id == interaction.guild.id,
                    MessageLog.created_at >= day_start, MessageLog.created_at < day_end
                ).count()
                daily_counts.append((day_start, cnt))

            embed = discord.Embed(title=f"📈 Activity (Last {days} Days)", color=discord.Color(color_int))
            max_count = max([c for _, c in daily_counts]) if daily_counts else 1
            graph_text = ""
            for date, count in daily_counts:
                bar = "█" * int((count / max_count * 20)) if max_count > 0 else 0
                graph_text += f"{date.strftime('%m/%d')}: {bar} {count}\n"
            embed.description = f"```{graph_text}```"
            total = sum(c for _, c in daily_counts)
            avg = total / days if days > 0 else 0
            embed.set_footer(text=f"Total: {total:,} | Avg: {avg:.1f}/day")
            await interaction.response.send_message(embed=embed)
        finally:
            session.close()


async def setup(bot):
    await bot.add_cog(Statistics(bot))
