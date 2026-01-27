import discord
from discord.ext import commands
from discord import app_commands
from database import SessionLocal, GuildConfig
from typing import Optional

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        session = SessionLocal()
        try:
            config = session.query(GuildConfig).filter_by(guild_id=member.guild.id).first()
            if not config or not config.welcome_enabled or not config.welcome_channel_id:
                return
            
            channel = member.guild.get_channel(config.welcome_channel_id)
            if not channel or not hasattr(channel, 'send'):
                return

            welcome_text = str(config.welcome_message or 'Welcome {user}!').replace('{user}', member.mention).replace('{server}', member.guild.name).replace('\\n', '\n')
            
            embed_color = int(config.embed_color) if config.embed_color else 0x3498db
            embed = discord.Embed(
                title=str(config.welcome_title or 'Welcome!').replace('{user}', member.name),
                description=welcome_text,
                color=discord.Color(embed_color)
            )
            
            if config.welcome_footer:
                embed.set_footer(text=str(config.welcome_footer).replace('{user}', member.name))
            
            embed.set_thumbnail(url=member.display_avatar.url)
            
            if config.welcome_image_url:
                embed.set_image(url=str(config.welcome_image_url))
            
            await channel.send(embed=embed)
        finally:
            session.close()

    @app_commands.command(name="welcome_setup", description="Detailed welcome system configuration")
    @app_commands.checks.has_permissions(administrator=True)
    async def welcome_setup(self, interaction: discord.Interaction, 
                             channel: discord.TextChannel,
                             title: str = "Welcome {user}!",
                             message: str = "Welcome to {server}, {user}!",
                             footer: str = "Enjoy your stay!",
                             image_url: Optional[str] = None):
        if not interaction.guild: return
        session = SessionLocal()
        try:
            config = session.query(GuildConfig).filter_by(guild_id=interaction.guild.id).first()
            if not config:
                config = GuildConfig(guild_id=interaction.guild.id)
                session.add(config)
            
            config.welcome_channel_id = channel.id
            config.welcome_title = title
            config.welcome_message = message
            config.welcome_footer = footer
            config.welcome_image_url = image_url
            config.welcome_enabled = True
            
            session.commit()
            await interaction.response.send_message(f"✅ Welcome system configured in {channel.mention}")
        finally:
            session.close()

async def setup(bot):
    await bot.add_cog(Welcome(bot))
