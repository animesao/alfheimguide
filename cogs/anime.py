import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import random
from database import SessionLocal, GuildConfig

class Anime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.waifu_api_url = "https://api.waifu.pics/sfw/waifu"

    @app_commands.command(name="anime", description="Sends a random anime image")
    async def anime(self, interaction: discord.Interaction):
        if not interaction.guild: return
        
        await interaction.response.defer()
        
        session = SessionLocal()
        try:
            config = session.query(GuildConfig).filter_by(guild_id=interaction.guild.id).first()
            color_int = int(config.embed_color) if config and config.embed_color else 0x3498db
            
            # Importing get_msg from main is tricky due to circular imports, 
            # so we'll just check language here or use a helper if available.
            # In this project main.py has MESSAGES and get_msg.
            from main import get_msg
            
            title = get_msg(interaction.guild.id, 'anime_title')
            
            async with aiohttp.ClientSession() as session_http:
                async with session_http.get(self.waifu_api_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        image_url = data.get('url')
                        
                        embed = discord.Embed(title=title, color=discord.Color(color_int))
                        embed.set_image(url=image_url)
                        embed.set_footer(text=f"Requested by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
                        
                        await interaction.followup.send(embed=embed)
                    else:
                        await interaction.followup.send("❌ Error fetching image from API.")
        except Exception as e:
            print(f"Error in anime command: {e}")
            await interaction.followup.send("❌ An error occurred.")
        finally:
            session.close()

async def setup(bot):
    await bot.add_cog(Anime(bot))
