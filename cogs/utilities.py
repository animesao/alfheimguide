import discord
from discord.ext import commands, tasks
from discord import app_commands
from database import SessionLocal, Reminder, Poll, PollVote, GuildConfig
import datetime
from typing import Optional
import json

class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_reminders.start()

    def cog_unload(self):
        self.check_reminders.cancel()

    def get_msg(self, guild_id: int, key: str, **kwargs) -> str:
        from main import get_msg as main_get_msg
        return main_get_msg(guild_id, key, **kwargs)

    @tasks.loop(seconds=30)
    async def check_reminders(self):
        session = SessionLocal()
        try:
            now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
            due_reminders = session.query(Reminder).filter(Reminder.remind_at <= now).all()
            
            for reminder in due_reminders:
                try:
                    channel = self.bot.get_channel(reminder.channel_id)
                    if channel:
                        user = await self.bot.fetch_user(reminder.user_id)
                        embed = discord.Embed(
                            title="⏰ Reminder",
                            description=reminder.message,
                            color=discord.Color.blue(),
                            timestamp=reminder.created_at
                        )
                        embed.set_footer(text=f"Set on")
                        await channel.send(f"{user.mention}", embed=embed)
                    
                    session.delete(reminder)
                except Exception as e:
                    print(f"Error sending reminder: {e}")
            
            session.commit()
        except Exception as e:
            print(f"Error checking reminders: {e}")
        finally:
            session.close()

    @check_reminders.before_loop
    async def before_check_reminders(self):
        await self.bot.wait_until_ready()

    @app_commands.command(name="remind", description="Set a reminder")
    async def remind(self, interaction: discord.Interaction, time: str, message: str):
        """
        Set a reminder. Time format: 10s, 5m, 2h, 1d
        """
        if not interaction.guild:
            return
        
        # Parse time
        import re
        match = re.match(r"(\d+)([smhd])", time.lower())
        if not match:
            await interaction.response.send_message(
                "❌ Invalid time format. Use: 10s, 5m, 2h, 1d",
                ephemeral=True
            )
            return
        
        amount, unit = match.groups()
        amount = int(amount)
        
        seconds = 0
        if unit == 's':
            seconds = amount
        elif unit == 'm':
            seconds = amount * 60
        elif unit == 'h':
            seconds = amount * 3600
        elif unit == 'd':
            seconds = amount * 86400
        
        if seconds < 10:
            await interaction.response.send_message("❌ Minimum reminder time is 10 seconds", ephemeral=True)
            return
        
        if seconds > 31536000:  # 1 year
            await interaction.response.send_message("❌ Maximum reminder time is 1 year", ephemeral=True)
            return
        
        remind_at = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + datetime.timedelta(seconds=seconds)
        
        session = SessionLocal()
        try:
            reminder = Reminder(
                guild_id=interaction.guild.id,
                user_id=interaction.user.id,
                channel_id=interaction.channel.id,
                message=message,
                remind_at=remind_at
            )
            session.add(reminder)
            session.commit()
            
            await interaction.response.send_message(
                f"✅ Reminder set for <t:{int(remind_at.timestamp())}:R>: {message}"
            )
        finally:
            session.close()

    @app_commands.command(name="reminders", description="View your active reminders")
    async def reminders(self, interaction: discord.Interaction):
        if not interaction.guild:
            return
        
        session = SessionLocal()
        try:
            user_reminders = session.query(Reminder).filter_by(
                guild_id=interaction.guild.id,
                user_id=interaction.user.id
            ).order_by(Reminder.remind_at).all()
            
            if not user_reminders:
                await interaction.response.send_message("📭 You have no active reminders", ephemeral=True)
                return
            
            config = session.query(GuildConfig).filter_by(guild_id=interaction.guild.id).first()
            color_int = int(config.embed_color) if config and config.embed_color else 0x3498db
            
            embed = discord.Embed(
                title="⏰ Your Reminders",
                color=discord.Color(color_int)
            )
            
            for reminder in user_reminders[:10]:
                timestamp = int(reminder.remind_at.timestamp())
                embed.add_field(
                    name=f"ID: {reminder.id}",
                    value=f"{reminder.message}\n<t:{timestamp}:R>",
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        finally:
            session.close()

    @app_commands.command(name="reminder_cancel", description="Cancel a reminder")
    async def reminder_cancel(self, interaction: discord.Interaction, reminder_id: int):
        if not interaction.guild:
            return
        
        session = SessionLocal()
        try:
            reminder = session.query(Reminder).filter_by(
                id=reminder_id,
                guild_id=interaction.guild.id,
                user_id=interaction.user.id
            ).first()
            
            if not reminder:
                await interaction.response.send_message("❌ Reminder not found", ephemeral=True)
                return
            
            session.delete(reminder)
            session.commit()
            
            await interaction.response.send_message("✅ Reminder cancelled", ephemeral=True)
        finally:
            session.close()

    @app_commands.command(name="poll", description="Create a poll")
    async def poll(
        self,
        interaction: discord.Interaction,
        question: str,
        option1: str,
        option2: str,
        option3: Optional[str] = None,
        option4: Optional[str] = None,
        option5: Optional[str] = None,
        duration: Optional[str] = None
    ):
        if not interaction.guild:
            return
        
        options = [option1, option2]
        if option3:
            options.append(option3)
        if option4:
            options.append(option4)
        if option5:
            options.append(option5)
        
        # Parse duration if provided
        ends_at = None
        if duration:
            import re
            match = re.match(r"(\d+)([mhd])", duration.lower())
            if match:
                amount, unit = match.groups()
                amount = int(amount)
                seconds = 0
                if unit == 'm':
                    seconds = amount * 60
                elif unit == 'h':
                    seconds = amount * 3600
                elif unit == 'd':
                    seconds = amount * 86400
                
                ends_at = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + datetime.timedelta(seconds=seconds)
        
        session = SessionLocal()
        try:
            config = session.query(GuildConfig).filter_by(guild_id=interaction.guild.id).first()
            color_int = int(config.embed_color) if config and config.embed_color else 0x3498db
            
            embed = discord.Embed(
                title="📊 " + question,
                color=discord.Color(color_int)
            )
            
            # Add options with emoji numbers
            emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
            description = ""
            for idx, option in enumerate(options):
                description += f"{emojis[idx]} {option}\n"
            
            embed.description = description
            embed.set_footer(text=f"Poll by {interaction.user.display_name}")
            
            if ends_at:
                embed.add_field(
                    name="⏰ Ends",
                    value=f"<t:{int(ends_at.timestamp())}:R>",
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed)
            message = await interaction.original_response()
            
            # Add reactions
            for idx in range(len(options)):
                await message.add_reaction(emojis[idx])
            
            # Save poll to database
            poll = Poll(
                guild_id=interaction.guild.id,
                channel_id=interaction.channel.id,
                message_id=message.id,
                question=question,
                options=json.dumps(options),
                creator_id=interaction.user.id,
                ends_at=ends_at
            )
            session.add(poll)
            session.commit()
        finally:
            session.close()

    @app_commands.command(name="poll_results", description="View poll results")
    async def poll_results(self, interaction: discord.Interaction, message_id: str):
        if not interaction.guild:
            return
        
        try:
            msg_id = int(message_id)
        except ValueError:
            await interaction.response.send_message("❌ Invalid message ID", ephemeral=True)
            return
        
        session = SessionLocal()
        try:
            poll = session.query(Poll).filter_by(message_id=msg_id).first()
            
            if not poll:
                await interaction.response.send_message("❌ Poll not found", ephemeral=True)
                return
            
            # Get the message and count reactions
            try:
                channel = self.bot.get_channel(poll.channel_id)
                message = await channel.fetch_message(poll.message_id)
            except:
                await interaction.response.send_message("❌ Could not fetch poll message", ephemeral=True)
                return
            
            options = json.loads(poll.options)
            emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
            
            config = session.query(GuildConfig).filter_by(guild_id=interaction.guild.id).first()
            color_int = int(config.embed_color) if config and config.embed_color else 0x3498db
            
            embed = discord.Embed(
                title="📊 Poll Results: " + poll.question,
                color=discord.Color(color_int)
            )
            
            total_votes = 0
            vote_counts = []
            
            for idx, option in enumerate(options):
                reaction = discord.utils.get(message.reactions, emoji=emojis[idx])
                count = reaction.count - 1 if reaction else 0  # -1 to exclude bot's reaction
                vote_counts.append(count)
                total_votes += count
            
            # Create results
            results_text = ""
            for idx, option in enumerate(options):
                count = vote_counts[idx]
                percentage = (count / total_votes * 100) if total_votes > 0 else 0
                bar_length = int(percentage / 10)
                bar = "█" * bar_length + "░" * (10 - bar_length)
                results_text += f"{emojis[idx]} **{option}**\n{bar} {percentage:.1f}% ({count} votes)\n\n"
            
            embed.description = results_text
            embed.set_footer(text=f"Total votes: {total_votes}")
            
            await interaction.response.send_message(embed=embed)
        finally:
            session.close()

    @app_commands.command(name="serverinfo", description="View server information")
    async def serverinfo(self, interaction: discord.Interaction):
        if not interaction.guild:
            return
        
        guild = interaction.guild
        
        session = SessionLocal()
        try:
            config = session.query(GuildConfig).filter_by(guild_id=guild.id).first()
            color_int = int(config.embed_color) if config and config.embed_color else 0x3498db
            
            embed = discord.Embed(
                title=f"📊 {guild.name}",
                color=discord.Color(color_int)
            )
            
            if guild.icon:
                embed.set_thumbnail(url=guild.icon.url)
            
            # Basic info
            embed.add_field(name="🆔 Server ID", value=guild.id, inline=True)
            embed.add_field(name="👑 Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
            embed.add_field(name="📅 Created", value=f"<t:{int(guild.created_at.timestamp())}:R>", inline=True)
            
            # Member stats
            total_members = guild.member_count
            bots = len([m for m in guild.members if m.bot])
            humans = total_members - bots
            
            embed.add_field(name="👥 Members", value=f"Total: {total_members}\nHumans: {humans}\nBots: {bots}", inline=True)
            
            # Channel stats
            text_channels = len(guild.text_channels)
            voice_channels = len(guild.voice_channels)
            categories = len(guild.categories)
            
            embed.add_field(name="📝 Channels", value=f"Text: {text_channels}\nVoice: {voice_channels}\nCategories: {categories}", inline=True)
            
            # Other stats
            embed.add_field(name="😀 Emojis", value=len(guild.emojis), inline=True)
            embed.add_field(name="🎭 Roles", value=len(guild.roles), inline=True)
            embed.add_field(name="🚀 Boost Level", value=f"Level {guild.premium_tier} ({guild.premium_subscription_count} boosts)", inline=True)
            
            # Verification level
            verification_levels = {
                discord.VerificationLevel.none: "None",
                discord.VerificationLevel.low: "Low",
                discord.VerificationLevel.medium: "Medium",
                discord.VerificationLevel.high: "High",
                discord.VerificationLevel.highest: "Highest"
            }
            embed.add_field(name="🔒 Verification", value=verification_levels.get(guild.verification_level, "Unknown"), inline=True)
            
            await interaction.response.send_message(embed=embed)
        finally:
            session.close()

    @app_commands.command(name="userinfo", description="View user information")
    async def userinfo(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        if not interaction.guild:
            return
        
        target = member or interaction.user
        
        session = SessionLocal()
        try:
            config = session.query(GuildConfig).filter_by(guild_id=interaction.guild.id).first()
            color_int = int(config.embed_color) if config and config.embed_color else 0x3498db
            
            embed = discord.Embed(
                title=f"👤 {target.display_name}",
                color=discord.Color(color_int)
            )
            
            embed.set_thumbnail(url=target.display_avatar.url)
            
            # Basic info
            embed.add_field(name="🆔 User ID", value=target.id, inline=True)
            embed.add_field(name="📛 Username", value=f"{target.name}", inline=True)
            embed.add_field(name="🤖 Bot", value="Yes" if target.bot else "No", inline=True)
            
            # Dates
            embed.add_field(name="📅 Account Created", value=f"<t:{int(target.created_at.timestamp())}:R>", inline=True)
            if target.joined_at:
                embed.add_field(name="📥 Joined Server", value=f"<t:{int(target.joined_at.timestamp())}:R>", inline=True)
            
            # Roles
            roles = [role.mention for role in target.roles if role.name != "@everyone"]
            if roles:
                embed.add_field(name=f"🎭 Roles ({len(roles)})", value=" ".join(roles[:10]), inline=False)
            
            # Status
            status_emojis = {
                discord.Status.online: "🟢 Online",
                discord.Status.idle: "🟡 Idle",
                discord.Status.dnd: "🔴 Do Not Disturb",
                discord.Status.offline: "⚫ Offline"
            }
            embed.add_field(name="📡 Status", value=status_emojis.get(target.status, "Unknown"), inline=True)
            
            # Top role
            if target.top_role.name != "@everyone":
                embed.add_field(name="⭐ Top Role", value=target.top_role.mention, inline=True)
            
            await interaction.response.send_message(embed=embed)
        finally:
            session.close()

async def setup(bot):
    await bot.add_cog(Utilities(bot))
