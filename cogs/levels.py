import discord
from discord.ext import commands
from discord import app_commands
from database import SessionLocal, UserLevel, GuildConfig
import random
from typing import Optional

class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        session = SessionLocal()
        try:
            user_lvl = session.query(UserLevel).filter_by(guild_id=message.guild.id, user_id=message.author.id).first()
            if not user_lvl:
                user_lvl = UserLevel(guild_id=message.guild.id, user_id=message.author.id, xp=0, level=1)
                session.add(user_lvl)
            
            current_xp = int(user_lvl.xp) if user_lvl.xp is not None else 0
            current_level = int(user_lvl.level) if user_lvl.level is not None else 1
                
            new_xp = current_xp + random.randint(5, 15)
            next_lvl_xp = current_level * 100
            
            if new_xp >= next_lvl_xp:
                current_level += 1
                new_xp = 0
                await message.channel.send(f"🎉 {message.author.mention} reached level {current_level}!")
            
            user_lvl.xp = new_xp
            user_lvl.level = current_level
            session.commit()
        finally:
            session.close()

    @app_commands.command(name="rank", description="Shows your current level and rank")
    async def rank_slash(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        if not interaction.guild: return
        target_member = member or interaction.user
        if not isinstance(target_member, discord.Member): return
        
        session = SessionLocal()
        try:
            user_lvl = session.query(UserLevel).filter_by(guild_id=interaction.guild.id, user_id=target_member.id).first()
            if not user_lvl:
                await interaction.response.send_message("No rank data yet.", ephemeral=True)
                return
            config = session.query(GuildConfig).filter_by(guild_id=interaction.guild.id).first()
            color_int = int(config.embed_color) if config and config.embed_color else 0x3498db
            embed = discord.Embed(title=f"Rank - {target_member.name}", color=discord.Color(color_int))
            
            current_level = int(user_lvl.level) if user_lvl.level is not None else 1
            current_xp = int(user_lvl.xp) if user_lvl.xp is not None else 0
            
            embed.add_field(name="Level", value=str(current_level))
            embed.add_field(name="XP", value=f"{current_xp}/{current_level * 100}")
            embed.set_thumbnail(url=target_member.display_avatar.url)
            await interaction.response.send_message(embed=embed)
        finally:
            session.close()

async def setup(bot):
    await bot.add_cog(Levels(bot))
