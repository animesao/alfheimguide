import discord
import random
import asyncio
import math
import time
import logging
from datetime import datetime, timezone
from discord.ext import commands, tasks
from discord import app_commands, ui
from database import SessionLocal, UserLevel, LevelConfig, GuildConfig
from typing import Optional

logger = logging.getLogger("alfheim_bot.levels")


def get_msg(guild_id: int, key: str, **kwargs) -> str:
    from main import get_msg as main_get_msg
    return main_get_msg(guild_id, key, **kwargs)


class LevelConfigModal(ui.Modal, title="⚙️ Основные настройки"):
    enabled = ui.TextInput(label="Включено (true/false)", default="true", required=True, max_length=5)
    xp_min = ui.TextInput(label="Мин. XP за сообщение", default="5", required=True, max_length=5)
    xp_max = ui.TextInput(label="Макс. XP за сообщение", default="15", required=True, max_length=5)
    xp_cooldown = ui.TextInput(label="Задержка XP (сек)", default="60", required=True, max_length=5)
    announce = ui.TextInput(label="Объявления о уровне (true/false)", default="true", required=True, max_length=5)

    def __init__(self, config: Optional[LevelConfig]):
        super().__init__(timeout=300)
        if config:
            self.enabled.default = "true" if config.enabled else "false"
            self.xp_min.default = str(config.xp_min)
            self.xp_max.default = str(config.xp_max)
            self.xp_cooldown.default = str(config.xp_cooldown)
            self.announce.default = "true" if config.announce_levelup else "false"

    async def on_submit(self, interaction: discord.Interaction):
        session = SessionLocal()
        try:
            config = session.query(LevelConfig).filter_by(guild_id=interaction.guild_id).first()
            if not config:
                config = LevelConfig(guild_id=interaction.guild_id)
                session.add(config)
            try:
                config.enabled = self.enabled.value.lower() == "true"
                config.xp_min = max(1, int(self.xp_min.value))
                config.xp_max = max(1, int(self.xp_max.value))
                config.xp_cooldown = max(0, int(self.xp_cooldown.value))
                config.announce_levelup = self.announce.value.lower() == "true"
                session.commit()
                await interaction.response.send_message("✅ Основные настройки сохранены!", ephemeral=True)
            except ValueError:
                await interaction.response.send_message("❌ Неверный формат чисел!", ephemeral=True)
        finally:
            session.close()


class LevelFormulaModal(ui.Modal, title="🧮 Формула XP"):
    level_base = ui.TextInput(label="База XP для 1 ур.", default="100", required=True, max_length=10)
    level_mult = ui.TextInput(label="Множитель XP (1.5)", default="1.5", required=True, max_length=5)
    max_level = ui.TextInput(label="Макс. уровень", default="100", required=True, max_length=5)

    def __init__(self, config: Optional[LevelConfig]):
        super().__init__(timeout=300)
        if config:
            self.level_base.default = str(config.level_base_xp)
            self.level_mult.default = str(config.level_multiplier)
            self.max_level.default = str(config.max_level)

    async def on_submit(self, interaction: discord.Interaction):
        session = SessionLocal()
        try:
            config = session.query(LevelConfig).filter_by(guild_id=interaction.guild_id).first()
            if not config:
                config = LevelConfig(guild_id=interaction.guild_id)
                session.add(config)
            try:
                config.level_base_xp = max(1, int(self.level_base.value))
                config.level_multiplier = max(1.0, float(self.level_mult.value))
                config.max_level = max(1, int(self.max_level.value))
                session.commit()
                await interaction.response.send_message("✅ Формула XP сохранена!", ephemeral=True)
            except ValueError:
                await interaction.response.send_message("❌ Неверный формат чисел!", ephemeral=True)
        finally:
            session.close()


class LevelRewardModal(ui.Modal, title="🎁 Награда за уровень"):
    level = ui.TextInput(label="Уровень", placeholder="5", required=True, max_length=5)
    role_id = ui.TextInput(label="ID роли", placeholder="123456789", required=False, max_length=30)
    message = ui.TextInput(label="Сообщение", placeholder="Поздравляем!", required=False, max_length=200)

    def __init__(self, config: LevelConfig):
        super().__init__(timeout=300)
        self.config = config

    async def on_submit(self, interaction: discord.Interaction):
        session = SessionLocal()
        try:
            config = session.query(LevelConfig).filter_by(guild_id=interaction.guild_id).first()
            if not config:
                await interaction.response.send_message("❌ Сначала настройте уровни!", ephemeral=True)
                return
            rewards = dict(config.level_role_rewards) if config.level_role_rewards else {}
            try:
                lvl = int(self.level.value)
                rewards[str(lvl)] = {
                    "role_id": int(self.role_id.value) if self.role_id.value else None,
                    "message": self.message.value or None,
                }
                config.level_role_rewards = rewards
                session.commit()
                role_mention = f"<@&{self.role_id.value}>" if self.role_id.value else "нет"
                await interaction.response.send_message(f"✅ Награда за уровень **{lvl}** сохранена! Роль: {role_mention}", ephemeral=True)
            except ValueError:
                await interaction.response.send_message("❌ Неверный формат!", ephemeral=True)
        finally:
            session.close()


class LevelConfigView(ui.View):
    def __init__(self, config: LevelConfig):
        super().__init__(timeout=300)
        self.config = config

    @ui.button(label="⚙️ Основные настройки", style=discord.ButtonStyle.primary)
    async def main_config(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(LevelConfigModal(self.config))

    @ui.button(label="🎁 Добавить награду за уровень", style=discord.ButtonStyle.success)
    async def add_reward(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(LevelRewardModal(self.config))

    @ui.button(label="📋 Список наград", style=discord.ButtonStyle.secondary)
    async def list_rewards(self, interaction: discord.Interaction, button: ui.Button):
        session = SessionLocal()
        try:
            config = session.query(LevelConfig).filter_by(guild_id=interaction.guild_id).first()
            rewards = dict(config.level_role_rewards) if config and config.level_role_rewards else {}
            embed = discord.Embed(title="🎁 Награды за уровни", color=discord.Color.blue())
            if rewards:
                for lvl, data in sorted(rewards.items(), key=lambda x: int(x[0])):
                    role_text = f"<@&{data['role_id']}>" if data.get("role_id") else "нет"
                    msg_text = f" - {data['message']}" if data.get("message") else ""
                    embed.add_field(name=f"Уровень {lvl}", value=f"Роль: {role_text}{msg_text}", inline=False)
            else:
                embed.description = "Наград пока нет"
            await interaction.response.send_message(embed=embed, ephemeral=True)
        finally:
            session.close()

    @ui.button(label="🗑️ Очистить награды", style=discord.ButtonStyle.danger)
    async def clear_rewards(self, interaction: discord.Interaction, button: ui.Button):
        session = SessionLocal()
        try:
            config = session.query(LevelConfig).filter_by(guild_id=interaction.guild_id).first()
            if config:
                config.level_role_rewards = {}
                session.commit()
            await interaction.response.send_message("✅ Награды очищены!", ephemeral=True)
        finally:
            session.close()

    @ui.button(label="🧮 Формула XP", style=discord.ButtonStyle.secondary)
    async def formula_config(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(LevelFormulaModal(self.config))


def calc_level_xp(level: int, base_xp: int, multiplier: float) -> int:
    return int(base_xp * (multiplier ** (level - 1)))


class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.xp_cooldowns = {}
        self._lvl_cache = {}
        self._gc_cache = {}
        self._cache_ttl = 60
        self.cleanup_cooldowns.start()

    def cog_unload(self):
        self.cleanup_cooldowns.cancel()

    @tasks.loop(hours=1)
    async def cleanup_cooldowns(self):
        self.xp_cooldowns.clear()

    def _get_configs(self, guild_id: int):
        now = time.time()
        if guild_id in self._lvl_cache and guild_id in self._gc_cache:
            lvl_cached, lvl_ts = self._lvl_cache[guild_id]
            gc_cached, gc_ts = self._gc_cache[guild_id]
            if now - min(lvl_ts, gc_ts) < self._cache_ttl:
                return lvl_cached, gc_cached
        session = SessionLocal()
        try:
            config = session.query(LevelConfig).filter_by(guild_id=guild_id).first()
            guild_config = session.query(GuildConfig).filter_by(guild_id=guild_id).first()
            self._lvl_cache[guild_id] = (config, now)
            self._gc_cache[guild_id] = (guild_config, now)
            return config, guild_config
        finally:
            session.close()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        config, guild_config = self._get_configs(message.guild.id)
        if not config or not config.enabled or not guild_config or not guild_config.levels_enabled:
            return
        session = SessionLocal()
        try:

            user_key = f"{message.guild.id}_{message.author.id}"
            now = datetime.now(timezone.utc).replace(tzinfo=None)

            if user_key in self.xp_cooldowns:
                if (now - self.xp_cooldowns[user_key]).total_seconds() < config.xp_cooldown:
                    return

            user_lvl = session.query(UserLevel).filter_by(
                guild_id=message.guild.id, user_id=message.author.id
            ).first()
            if not user_lvl:
                user_lvl = UserLevel(guild_id=message.guild.id, user_id=message.author.id)
                session.add(user_lvl)

            xp_gain = random.randint(config.xp_min, config.xp_max)

            if config.xp_boost_role_ids and message.author._roles:
                for rid in config.xp_boost_role_ids:
                    if rid in message.author._roles:
                        xp_gain = int(xp_gain * config.xp_boost_multiplier)
                        break

            user_lvl.xp = (user_lvl.xp or 0) + xp_gain
            user_lvl.total_messages = (user_lvl.total_messages or 0) + 1
            user_lvl.last_message_xp = now

            next_lvl_xp = calc_level_xp(user_lvl.level or 1, config.level_base_xp, config.level_multiplier)

            if user_lvl.xp >= next_lvl_xp and (user_lvl.level or 1) < config.max_level:
                user_lvl.level = (user_lvl.level or 1) + 1
                user_lvl.xp = user_lvl.xp - next_lvl_xp
                session.commit()

                await self.handle_levelup(message, user_lvl, config, guild_config)
            else:
                session.commit()

            self.xp_cooldowns[user_key] = now
        except Exception as e:
            logger.warning(f"xp error g={message.guild.id} u={message.author.id}: {e}")
        finally:
            session.close()

    async def handle_levelup(self, message, user_lvl, config, guild_config):
        if config.announce_levelup:
            channel_id = config.announce_channel_id or message.channel.id
            channel = message.guild.get_channel(channel_id)
            if channel:
                embed = discord.Embed(
                    title="🎉 Повышение уровня!",
                    description=f"{message.author.mention} достиг уровня **{user_lvl.level}**!",
                    color=discord.Color.gold(),
                )
                embed.set_thumbnail(url=message.author.display_avatar.url)
                await channel.send(embed=embed)

        rewards = dict(config.level_role_rewards) if config.level_role_rewards else {}
        reward = rewards.get(str(user_lvl.level))
        if reward and reward.get("role_id"):
            role = message.guild.get_role(int(reward["role_id"]))
            if role:
                try:
                    if config.stack_roles:
                        await message.author.add_roles(role)
                    else:
                        for lvl_data in rewards.values():
                            if lvl_data.get("role_id") and lvl_data["role_id"] != reward["role_id"]:
                                old_role = message.guild.get_role(int(lvl_data["role_id"]))
                                if old_role and old_role in message.author.roles:
                                    await message.author.remove_roles(old_role)
                        await message.author.add_roles(role)
                except Exception:
                    pass

    @app_commands.command(name="rank", description="Shows your current level and rank")
    async def rank_slash(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        if not interaction.guild:
            return
        target = member or interaction.user
        session = SessionLocal()
        try:
            config = session.query(LevelConfig).filter_by(guild_id=interaction.guild.id).first()
            user_lvl = session.query(UserLevel).filter_by(
                guild_id=interaction.guild.id, user_id=target.id
            ).first()
            guild_config = session.query(GuildConfig).filter_by(guild_id=interaction.guild.id).first()
            color_int = int(guild_config.embed_color) if guild_config and guild_config.embed_color else 0x3498db

            if not user_lvl:
                embed = discord.Embed(
                    title=f"📊 {target.display_name}",
                    description="Нет данных об уровне",
                    color=discord.Color(color_int),
                )
                embed.set_thumbnail(url=target.display_avatar.url)
                await interaction.response.send_message(embed=embed)
                return

            level = user_lvl.level or 1
            xp = user_lvl.xp or 0
            base = config.level_base_xp if config else 100
            mult = config.level_multiplier if config else 1.5
            next_xp = calc_level_xp(level, base, mult)

            from sqlalchemy import func, and_, or_
            rank = session.query(func.count(UserLevel.user_id)).filter(
                and_(
                    UserLevel.guild_id == interaction.guild.id,
                    UserLevel.user_id != target.id,
                    or_(
                        UserLevel.level > (user_lvl.level or 1),
                        and_(
                            UserLevel.level == (user_lvl.level or 1),
                            UserLevel.xp > (user_lvl.xp or 0)
                        )
                    )
                )
            ).scalar() + 1

            embed = discord.Embed(
                title=f"📊 {target.display_name}",
                color=discord.Color(color_int),
            )
            embed.set_thumbnail(url=target.display_avatar.url)
            embed.add_field(name="Уровень", value=str(level), inline=True)
            embed.add_field(name="Ранг", value=f"#{rank}", inline=True)
            embed.add_field(name="XP", value=f"{xp:,}/{next_xp:,}", inline=True)
            embed.add_field(name="Всего сообщений", value=f"{user_lvl.total_messages or 0:,}", inline=True)
            if user_lvl.voice_minutes:
                embed.add_field(name="В голосовых", value=f"{user_lvl.voice_minutes} мин", inline=True)

            progress = min(xp / next_xp * 100, 100) if next_xp > 0 else 0
            bar = "█" * int(progress / 10) + "░" * (10 - int(progress / 10))
            embed.add_field(name="Прогресс", value=f"{bar} {progress:.0f}%", inline=False)

            await interaction.response.send_message(embed=embed)
        finally:
            session.close()

    @app_commands.command(name="level_config", description="Full level system configuration")
    @app_commands.checks.has_permissions(administrator=True)
    async def level_config(self, interaction: discord.Interaction):
        if not interaction.guild:
            return
        session = SessionLocal()
        try:
            config = session.query(LevelConfig).filter_by(guild_id=interaction.guild.id).first()
            if not config:
                config = LevelConfig(guild_id=interaction.guild.id)
                session.add(config)
                session.commit()

            guild_config = session.query(GuildConfig).filter_by(guild_id=interaction.guild.id).first()
            color_int = int(guild_config.embed_color) if guild_config and guild_config.embed_color else 0x3498db

            embed = discord.Embed(
                title="⚙️ Настройка уровней",
                description="Настройте систему уровней под свой сервер",
                color=discord.Color(color_int),
            )
            embed.add_field(name="Статус", value="✅ Включено" if config.enabled else "❌ Выключено", inline=True)
            embed.add_field(name="XP за сообщение", value=f"{config.xp_min}-{config.xp_max}", inline=True)
            embed.add_field(name="Задержка", value=f"{config.xp_cooldown} сек", inline=True)
            embed.add_field(name="База XP", value=str(config.level_base_xp), inline=True)
            embed.add_field(name="Множитель", value=f"x{config.level_multiplier}", inline=True)
            embed.add_field(name="Макс. уровень", value=str(config.max_level), inline=True)
            embed.add_field(name="Объявления", value="✅" if config.announce_levelup else "❌", inline=True)

            view = LevelConfigView(config)
            await interaction.response.send_message(embed=embed, view=view)
        finally:
            session.close()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if member.bot:
            return
        session = SessionLocal()
        try:
            config = session.query(LevelConfig).filter_by(guild_id=member.guild.id).first()
            if not config or not config.enabled or not config.xp_per_voice_minute:
                return
            user_lvl = session.query(UserLevel).filter_by(guild_id=member.guild.id, user_id=member.id).first()
            if not user_lvl:
                return
            if after.channel and not before.channel:
                user_lvl.last_voice_update = datetime.now(timezone.utc).replace(tzinfo=None)
                session.commit()
            elif not after.channel and before.channel and user_lvl.last_voice_update:
                now = datetime.now(timezone.utc).replace(tzinfo=None)
                minutes = int((now - user_lvl.last_voice_update).total_seconds() / 60)
                if minutes > 0:
                    user_lvl.voice_minutes = (user_lvl.voice_minutes or 0) + minutes
                    user_lvl.xp = (user_lvl.xp or 0) + minutes * config.xp_per_voice_minute
                user_lvl.last_voice_update = None
                session.commit()
        except Exception as e:
            logger.warning(f"voice xp error g={member.guild.id} u={member.id}: {e}")
        finally:
            session.close()


async def setup(bot):
    await bot.add_cog(Levels(bot))
