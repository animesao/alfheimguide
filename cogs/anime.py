import discord
import random
import aiohttp
import asyncio
from discord.ext import commands
from discord import app_commands
from database import SessionLocal, GuildConfig


ANIME_API_SOURCES = [
    "https://api.waifu.pics/sfw/waifu",
    "https://api.waifu.pics/sfw/neko",
    "https://api.waifu.pics/sfw/shinobu",
    "https://api.waifu.pics/sfw/megumin",
    "https://api.waifu.pics/sfw/bullying",
    "https://api.waifu.pics/sfw/cuddle",
    "https://api.waifu.pics/sfw/hug",
    "https://api.waifu.pics/sfw/kiss",
    "https://api.waifu.pics/sfw/pat",
    "https://api.waifu.pics/sfw/smug",
]

FALLBACK_APIS = [
    "https://nekos.life/api/v2/img/waifu",
    "https://nekos.life/api/v2/img/neko",
    "https://nekos.life/api/v2/img/hug",
]

NEKOS_ENDPOINTS = [
    "waifu", "neko", "hug", "kiss", "pat", "smug", "cuddle", "tickle"
]


def get_msg(guild_id: int, key: str, **kwargs) -> str:
    from main import get_msg as main_get_msg
    return main_get_msg(guild_id, key, **kwargs)


class Anime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session: aiohttp.ClientSession = None

    async def cog_load(self):
        self.session = aiohttp.ClientSession()

    async def cog_unload(self):
        if self.session:
            await self.session.close()

    async def fetch_anime_image(self) -> str | None:
        sources = list(ANIME_API_SOURCES)
        random.shuffle(sources)

        for url in sources:
            try:
                async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        image_url = data.get("url")
                        if image_url:
                            return image_url
            except (asyncio.TimeoutError, aiohttp.ClientError):
                continue

        endpoint = random.choice(NEKOS_ENDPOINTS)
        try:
            async with self.session.get(
                f"https://nekos.life/api/v2/img/{endpoint}",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    image_url = data.get("url")
                    if image_url:
                        return image_url
        except (asyncio.TimeoutError, aiohttp.ClientError):
            pass

        return None

    @app_commands.command(name="anime", description="Sends a random anime image")
    async def anime(self, interaction: discord.Interaction):
        if not interaction.guild:
            return

        await interaction.response.defer()

        session = SessionLocal()
        try:
            config = session.query(GuildConfig).filter_by(guild_id=interaction.guild.id).first()
            color_int = int(config.embed_color) if config and config.embed_color else 0x3498db
            title = get_msg(interaction.guild.id, "anime_title")

            image_url = await self.fetch_anime_image()

            if image_url:
                embed = discord.Embed(title=title, color=discord.Color(color_int))
                embed.set_image(url=image_url)
                embed.set_footer(
                    text=f"Requested by {interaction.user.display_name}",
                    icon_url=interaction.user.display_avatar.url,
                )
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(
                    "❌ Не удалось получить изображение. Попробуйте позже."
                )
        except Exception as e:
            err_msg = str(e)[:200]
            await interaction.followup.send(f"❌ Ошибка: {err_msg}")
        finally:
            session.close()


async def setup(bot):
    await bot.add_cog(Anime(bot))
