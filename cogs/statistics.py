import discord
from discord.ext import commands
from discord import app_commands
from database import SessionLocal, UserActivity, MessageLog, UserLevel, GuildConfig
import datetime
from typing import Optional
from collections import defaultdict

class Statistics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.daily_stats = defaultdict(lambda: defaultdict(int))  # {guild_id: {user_id: count}}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        
        # Track daily message count
        guild_key = message.guild.id
        user_key = message.author.id
        self.daily_stats[guild_key][user_key] += 1

    def get_msg(self, guild_id: int, key: str, **kwargs) -> str:
        from main import get_msg as main_get_msg
        return main_get_msg(guild_id, key, **kwargs)

    @app_commands.command(name="topmembers", description="View most active members")
    async def topmembers(self, interaction: discord.Interaction, timeframe: str = "today"):
        """
        View most active members. Timeframe: today, week, month, alltime
        """
        if not interaction.guild:
            return
        
        session = SessionLocal()
        try:
            config = session.query(GuildConfig).filter_by(guild_id=interaction.guild.id).first()
            
            if not config or not config.stats_enabled:
                await interaction.response.send_message("📊 Statistics are disabled", ephemeral=True)
                return
            
            color_int = int(config.embed_color) if config and config.embed_color else 0x3498db
            
            # Calculate date range
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
            
            # Count messages per user
            messages = session.query(MessageLog).filter(
                MessageLog.guild_id == interaction.guild.id,
                MessageLog.created_at >= start_date
            ).all()
            
            user_counts = defaultdict(int)
            for msg in messages:
                user_counts[msg.user_id] += 1
            
            # Sort by count
            sorted_users = sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            embed = discord.Embed(
                title=title,
                color=discord.Color(color_int)
            )
            
            if not sorted_users:
                embed.description = "No activity data yet"
            else:
                leaderboard_text = ""
                for idx, (user_id, count) in enumerate(sorted_users, 1):
                    try:
                        member = interaction.guild.get_member(user_id)
                        if member:
                            medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
                            leaderboard_text += f"{medal} **{member.display_name}** - {count:,} messages\n"
                    except:
                        continue
                
                embed.description = leaderboard_text
            
            await interaction.response.send_message(embed=embed)
        finally:
            session.close()

    @app_commands.command(name="channelstats", description="View channel activity statistics")
    async def channelstats(self, interaction: discord.Interaction):
        if not interaction.guild:
            return
        
        session = SessionLocal()
        try:
            config = session.query(GuildConfig).filter_by(guild_id=interaction.guild.id).first()
            color_int = int(config.embed_color) if config and config.embed_color else 0x3498db
            
            # Get messages from last 7 days
            start_date = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) - datetime.timedelta(days=7)
            
            messages = session.query(MessageLog).filter(
                MessageLog.guild_id == interaction.guild.id,
                MessageLog.created_at >= start_date
            ).all()
            
            channel_counts = defaultdict(int)
            for msg in messages:
                channel_counts[msg.channel_id] += 1
            
            sorted_channels = sorted(channel_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            embed = discord.Embed(
                title="📊 Channel Activity (Last 7 Days)",
                color=discord.Color(color_int)
            )
            
            if not sorted_channels:
                embed.description = "No activity data yet"
            else:
                stats_text = ""
                total_messages = sum(channel_counts.values())
                
                for idx, (channel_id, count) in enumerate(sorted_channels, 1):
                    try:
                        channel = interaction.guild.get_channel(channel_id)
                        if channel:
                            percentage = (count / total_messages * 100) if total_messages > 0 else 0
                            bar_length = int(percentage / 10)
                            bar = "█" * bar_length + "░" * (10 - bar_length)
                            stats_text += f"**{idx}. {channel.mention}**\n{bar} {percentage:.1f}% ({count:,} messages)\n\n"
                    except:
                        continue
                
                embed.description = stats_text
                embed.set_footer(text=f"Total messages: {total_messages:,}")
            
            await interaction.response.send_message(embed=embed)
        finally:
            session.close()

    @app_commands.command(name="serverstats", description="View detailed server statistics")
    async def serverstats(self, interaction: discord.Interaction):
        if not interaction.guild:
            return
        
        await interaction.response.defer()
        
        session = SessionLocal()
        try:
            config = session.query(GuildConfig).filter_by(guild_id=interaction.guild.id).first()
            color_int = int(config.embed_color) if config and config.embed_color else 0x3498db
            
            guild = interaction.guild
            
            # Get various stats
            now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_start = now - datetime.timedelta(days=7)
            
            # Message stats
            total_messages = session.query(MessageLog).filter_by(guild_id=guild.id).count()
            today_messages = session.query(MessageLog).filter(
                MessageLog.guild_id == guild.id,
                MessageLog.created_at >= today_start
            ).count()
            week_messages = session.query(MessageLog).filter(
                MessageLog.guild_id == guild.id,
                MessageLog.created_at >= week_start
            ).count()
            
            # Member stats
            total_members = guild.member_count
            bots = len([m for m in guild.members if m.bot])
            humans = total_members - bots
            
            # Online members
            online = len([m for m in guild.members if m.status != discord.Status.offline])
            
            # New members today
            new_today = len([m for m in guild.members if m.joined_at and m.joined_at.replace(tzinfo=None) >= today_start])
            
            embed = discord.Embed(
                title=f"📊 Server Statistics - {guild.name}",
                color=discord.Color(color_int),
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )
            
            if guild.icon:
                embed.set_thumbnail(url=guild.icon.url)
            
            # Member stats
            embed.add_field(
                name="👥 Members",
                value=f"Total: **{total_members:,}**\nHumans: **{humans:,}**\nBots: **{bots:,}**\nOnline: **{online:,}**\nNew Today: **{new_today:,}**",
                inline=True
            )
            
            # Message stats
            embed.add_field(
                name="💬 Messages",
                value=f"Total: **{total_messages:,}**\nToday: **{today_messages:,}**\nThis Week: **{week_messages:,}**",
                inline=True
            )
            
            # Channel stats
            text_channels = len(guild.text_channels)
            voice_channels = len(guild.voice_channels)
            categories = len(guild.categories)
            
            embed.add_field(
                name="📝 Channels",
                value=f"Text: **{text_channels}**\nVoice: **{voice_channels}**\nCategories: **{categories}**",
                inline=True
            )
            
            # Server info
            embed.add_field(
                name="🎭 Roles",
                value=f"**{len(guild.roles)}** roles",
                inline=True
            )
            
            embed.add_field(
                name="😀 Emojis",
                value=f"**{len(guild.emojis)}** emojis",
                inline=True
            )
            
            embed.add_field(
                name="🚀 Boosts",
                value=f"Level **{guild.premium_tier}**\n**{guild.premium_subscription_count}** boosts",
                inline=True
            )
            
            # Activity graph (simple text-based)
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
            activity_graph = ""
            days_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            
            for idx, count in enumerate(week_days):
                bar_length = int((count / max_messages * 10)) if max_messages > 0 else 0
                bar = "█" * bar_length + "░" * (10 - bar_length)
                activity_graph += f"{days_names[idx]}: {bar} {count}\n"
            
            embed.add_field(
                name="📈 Activity (Last 7 Days)",
                value=f"```{activity_graph}```",
                inline=False
            )
            
            await interaction.followup.send(embed=embed)
        finally:
            session.close()

    @app_commands.command(name="userstats", description="View detailed user statistics")
    async def userstats(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        if not interaction.guild:
            return
        
        target = member or interaction.user
        
        session = SessionLocal()
        try:
            config = session.query(GuildConfig).filter_by(guild_id=interaction.guild.id).first()
            color_int = int(config.embed_color) if config and config.embed_color else 0x3498db
            
            # Get message count
            total_messages = session.query(MessageLog).filter_by(
                guild_id=interaction.guild.id,
                user_id=target.id
            ).count()
            
            # Get messages today
            today_start = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None).replace(hour=0, minute=0, second=0, microsecond=0)
            today_messages = session.query(MessageLog).filter(
                MessageLog.guild_id == interaction.guild.id,
                MessageLog.user_id == target.id,
                MessageLog.created_at >= today_start
            ).count()
            
            # Get level info
            user_level = session.query(UserLevel).filter_by(
                guild_id=interaction.guild.id,
                user_id=target.id
            ).first()
            
            level = user_level.level if user_level else 1
            xp = user_level.xp if user_level else 0
            
            # Calculate rank
            all_users = session.query(UserLevel).filter_by(guild_id=interaction.guild.id).all()
            sorted_users = sorted(all_users, key=lambda u: (u.level, u.xp), reverse=True)
            rank = next((idx + 1 for idx, u in enumerate(sorted_users) if u.user_id == target.id), 0)
            
            # Most active channel
            messages = session.query(MessageLog).filter_by(
                guild_id=interaction.guild.id,
                user_id=target.id
            ).all()
            
            channel_counts = defaultdict(int)
            for msg in messages:
                channel_counts[msg.channel_id] += 1
            
            most_active_channel = None
            if channel_counts:
                most_active_channel_id = max(channel_counts, key=channel_counts.get)
                most_active_channel = interaction.guild.get_channel(most_active_channel_id)
            
            embed = discord.Embed(
                title=f"📊 Statistics for {target.display_name}",
                color=discord.Color(color_int)
            )
            
            embed.set_thumbnail(url=target.display_avatar.url)
            
            embed.add_field(
                name="💬 Messages",
                value=f"Total: **{total_messages:,}**\nToday: **{today_messages:,}**",
                inline=True
            )
            
            embed.add_field(
                name="📊 Level",
                value=f"Level: **{level}**\nXP: **{xp}/{level * 100}**\nRank: **#{rank}**",
                inline=True
            )
            
            if most_active_channel:
                embed.add_field(
                    name="📝 Most Active Channel",
                    value=f"{most_active_channel.mention}\n**{channel_counts[most_active_channel.id]:,}** messages",
                    inline=True
                )
            
            # Join date
            if target.joined_at:
                days_in_server = (datetime.datetime.now(datetime.timezone.utc) - target.joined_at).days
                embed.add_field(
                    name="📅 Member For",
                    value=f"**{days_in_server}** days",
                    inline=True
                )
            
            # Average messages per day
            if target.joined_at:
                days = max((datetime.datetime.now(datetime.timezone.utc) - target.joined_at).days, 1)
                avg_messages = total_messages / days
                embed.add_field(
                    name="📈 Average",
                    value=f"**{avg_messages:.1f}** messages/day",
                    inline=True
                )
            
            await interaction.response.send_message(embed=embed)
        finally:
            session.close()

    @app_commands.command(name="activity_graph", description="View server activity graph")
    async def activity_graph(self, interaction: discord.Interaction, days: int = 7):
        if not interaction.guild:
            return
        
        if days < 1 or days > 30:
            await interaction.response.send_message("❌ Days must be between 1 and 30", ephemeral=True)
            return
        
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
                
                day_messages = session.query(MessageLog).filter(
                    MessageLog.guild_id == interaction.guild.id,
                    MessageLog.created_at >= day_start,
                    MessageLog.created_at < day_end
                ).count()
                
                daily_counts.append((day_start, day_messages))
            
            embed = discord.Embed(
                title=f"📈 Activity Graph (Last {days} Days)",
                color=discord.Color(color_int)
            )
            
            max_messages = max([count for _, count in daily_counts]) if daily_counts else 1
            
            graph_text = ""
            for date, count in daily_counts:
                bar_length = int((count / max_messages * 20)) if max_messages > 0 else 0
                bar = "█" * bar_length
                date_str = date.strftime("%m/%d")
                graph_text += f"{date_str}: {bar} {count}\n"
            
            embed.description = f"```{graph_text}```"
            
            total = sum([count for _, count in daily_counts])
            avg = total / days if days > 0 else 0
            embed.set_footer(text=f"Total: {total:,} messages | Average: {avg:.1f} messages/day")
            
            await interaction.response.send_message(embed=embed)
        finally:
            session.close()

async def setup(bot):
    await bot.add_cog(Statistics(bot))
