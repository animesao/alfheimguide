import os
import asyncio
import logging
import discord
from dotenv import load_dotenv
from discord.ext import commands, tasks

load_dotenv()

BOT_VERSION = "2026.6.6"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("alfheim_bot")

from github import Github, Auth
from database import (
    SessionLocal,
    TrackedUser,
    RepoSnapshot,
    ReleaseSnapshot,
    GuildConfig,
    TempBan,
    init_db,
)
from datetime import datetime, timezone
from typing import Optional
from functools import lru_cache

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

if GITHUB_TOKEN:
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)
else:
    g = None

MESSAGES = {
    "ru": {
        "unbanned_auto": "⏰ Автоматический разбан пользователя {user}",
        "set_channel": "✅ Канал для уведомлений установлен: {channel}",
        "user_not_found": "❌ Пользователь {username} не найден на GitHub.",
        "user_exists": "⚠️ Пользователь {username} уже отслеживается на этом сервере.",
        "tracking_started": "✅ Начато отслеживание {username} ({count} репозиториев).",
        "error_adding": "❌ Ошибка при добавлении: {error}",
        "lang_updated": "✅ Язык изменен на Русский.",
        "new_repo": "🚀 **Новый репозиторий**",
        "update": "🛠 **Обновление в репозитории**",
        "repo_deleted": "🗑️ **Репозиторий удален**",
        "last_push": "Последний пуш",
        "set_channel_first": "⚠️ Сначала установите канал уведомлений командой !set_channel",
        "kicked": "Исключен",
        "banned": "Забанен",
        "unbanned": "Разбанен",
        "muted": "Таймаут",
        "unmuted": "Размьючен",
        "warned": "Предупреждение",
        "kick_success": "✅ {member} исключен.",
        "ban_success": "✅ {member} забанен.",
        "unban_success": "✅ {user} разбанен.",
        "mute_success": "✅ {member} отправлен в таймаут на {minutes} мин.",
        "unmute_success": "✅ {member} больше не в таймауте.",
        "warn_success": "✅ {member} получил предупреждение: {reason}",
        "clear_success": "✅ Удалено {count} сообщений.",
        "automod_updated": "✅ Авто-модерация: {enabled}, ссылки: {anti_links}, действие: {action}.",
        "github_disabled": "⚠️ Отслеживание GitHub отключено на этом сервере.",
        "module_updated": "✅ Модуль **{module}** теперь **{state}**.",
        "enabled": "Включен",
        "disabled": "Выключен",
        "color_updated": "✅ Цвет эмбедов обновлен: `{color}`",
        "invalid_color": "❌ Неверный формат цвета Hex.",
        "reason": "Причина",
        "duration": "Длительность",
        "dm_kick": "Вы были исключены из **{server}**\nПричина: {reason}",
        "dm_ban": "Вы были забанены на **{server}**\nПричина: {reason}",
        "dm_mute": "Вам был выдан таймаут в **{server}** на {minutes} мин.\nПричина: {reason}",
        "dm_unmute": "С вас снят таймаут на **{server}**",
        "dm_unban": "Вы были разбанены на **{server}**\nПричина: {reason}",
        "dm_warn": "Вы получили предупреждение в **{server}**\nПричина: {reason}",
        "automod_bad_words": "⚠️ {user}, следите за языком!",
        "automod_links": "⚠️ {user}, ссылки запрещены!",
        "game_already_active": "⚠️ У вас уже есть активная игра!",
        "minesweeper_title": "Сапёр",
        "minesweeper_instructions": "Нажмите на клетку, чтобы открыть её",
        "minesweeper_won": "🎉 Вы выиграли!",
        "minesweeper_lost": "💥 Вы проиграли!",
        "snake_title": "Змейка",
        "snake_instructions": "Используйте кнопки для движения",
        "snake_game_over": "💥 Игра окончена!",
        "score": "Счёт",
        "anime_title": "🌸 Случайное Аниме",
        "user_not_tracked": "⚠️ Пользователь {username} не отслеживается.",
        "user_removed": "✅ Пользователь {username} удалён из отслеживания.",
        "automod_mute_reason": "Автоматический мьют за нарушение правил",
        "invalid_duration": "❌ Неверный формат. Используйте: 10s, 5m, 1h, 1d",
        "tempban_success": "✅ {member} забанен на {duration}.",
        "verify_setup_success": "✅ Верификация настроена в {channel}",
        "verify_button_added": "✅ Кнопка добавлена!",
        "verify_button_deleted": "✅ Кнопка удалена!",
        "verify_updated": "✅ Настройки обновлены!",
        "verify_not_setup": "❌ Верификация не настроена!",
        "economy_disabled": "💰 Экономическая система отключена",
        "insufficient_funds": "❌ Недостаточно средств! У вас {balance:,} монет",
        "transfer_success": "✅ Переведено {amount:,} монет пользователю {user}",
        "daily_claimed": "🎁 Вы получили ежедневную награду: {amount:,} монет!",
        "work_success": "💼 Вы {job} и заработали {amount:,} монет!",
        "reminder_set": "✅ Напоминание установлено на {time}",
        "poll_created": "📊 Опрос создан!",
        "report_submitted": "✅ Жалоба отправлена (ID: {id}). Модераторы скоро её рассмотрят.",
        "raid_detected": "🚨 ОБНАРУЖЕН РЕЙД! {count} входов за 60 секунд",
        "slowmode_set": "✅ Медленный режим установлен на {seconds} секунд",
        "giveaway_created": "🎉 **Розыгрыш создан!**",
        "giveaway_ended": "🎉 **Розыгрыш завершён!** Победитель: {winner}",
        "giveaway_enter": "🎉 Участвовать в розыгрыше",
        "ai_config_updated": "✅ Настройки AI обновлены!",
        "ai_channel_added": "✅ Канал {channel} добавлен для AI.",
        "ai_channel_removed": "✅ Канал {channel} удалён из AI.",
        "ai_dm_toggle": "✅ AI в ЛС теперь {state}.",
        "ai_auto_respond_toggle": "✅ Авто-ответ AI теперь {state}.",
        "ai_help": "Используйте `/ai` для настройки AI на сервере или просто напишите сообщение в настроенном канале.",
    },
    "en": {
        "unbanned_auto": "⏰ Auto-unbanned user {user}",
        "set_channel": "✅ Notification channel set to: {channel}",
        "user_not_found": "❌ User {username} not found on GitHub.",
        "user_exists": "⚠️ User {username} is already being tracked on this server.",
        "tracking_started": "✅ Started tracking {username} ({count} repositories).",
        "error_adding": "❌ Error adding user: {error}",
        "lang_updated": "✅ Language updated to English.",
        "new_repo": "🚀 **New Repository**",
        "update": "🛠 **Repository Update**",
        "repo_deleted": "🗑️ **Repository Deleted**",
        "last_push": "Last push",
        "set_channel_first": "⚠️ Please set a notification channel first using !set_channel",
        "kicked": "Kicked",
        "banned": "Banned",
        "unbanned": "Unbanned",
        "muted": "Muted",
        "unmuted": "Unmuted",
        "warned": "Warned",
        "kick_success": "✅ {member} kicked.",
        "ban_success": "✅ {member} banned.",
        "unban_success": "✅ {user} unbanned.",
        "mute_success": "✅ {member} muted for {minutes}m.",
        "unmute_success": "✅ {member} unmuted.",
        "warn_success": "✅ {member} warned for: {reason}",
        "clear_success": "✅ Deleted {count} messages.",
        "automod_updated": "✅ Automod: {enabled}, links: {anti_links}, action: {action}.",
        "github_disabled": "⚠️ GitHub tracking is disabled on this server.",
        "module_updated": "✅ Module **{module}** is now **{state}**.",
        "enabled": "Enabled",
        "disabled": "Disabled",
        "color_updated": "✅ Embed color updated to `{color}`",
        "invalid_color": "❌ Invalid Hex color format.",
        "reason": "Reason",
        "duration": "Duration",
        "dm_kick": "You were kicked from **{server}**\nReason: {reason}",
        "dm_ban": "You were banned from **{server}**\nReason: {reason}",
        "dm_mute": "You were muted in **{server}** for {minutes}m.\nReason: {reason}",
        "dm_unmute": "You were unmuted in **{server}**",
        "dm_unban": "You were unbanned from **{server}**\nReason: {reason}",
        "dm_warn": "You were warned in **{server}**\nReason: {reason}",
        "automod_bad_words": "⚠️ {user}, watch your language!",
        "automod_links": "⚠️ {user}, links are not allowed!",
        "game_already_active": "⚠️ You already have an active game!",
        "minesweeper_title": "Minesweeper",
        "minesweeper_instructions": "Click on a cell to reveal it",
        "minesweeper_won": "🎉 You won!",
        "minesweeper_lost": "💥 You lost!",
        "snake_title": "Snake",
        "snake_instructions": "Use buttons to move",
        "snake_game_over": "💥 Game over!",
        "score": "Score",
        "anime_title": "🌸 Random Anime",
        "user_not_tracked": "⚠️ User {username} is not being tracked.",
        "user_removed": "✅ User {username} removed from tracking.",
        "automod_mute_reason": "Automatic mute for rule violation",
        "invalid_duration": "❌ Invalid format. Use: 10s, 5m, 1h, 1d",
        "tempban_success": "✅ {member} banned for {duration}.",
        "verify_setup_success": "✅ Verification setup in {channel}",
        "verify_button_added": "✅ Button added!",
        "verify_button_deleted": "✅ Button deleted!",
        "verify_updated": "✅ Settings updated!",
        "verify_not_setup": "❌ Verification not setup!",
        "economy_disabled": "💰 Economy system is disabled",
        "insufficient_funds": "❌ Insufficient funds! You have {balance:,} coins",
        "transfer_success": "✅ Transferred {amount:,} coins to {user}",
        "daily_claimed": "🎁 You claimed your daily reward: {amount:,} coins!",
        "work_success": "💼 You {job} and earned {amount:,} coins!",
        "reminder_set": "✅ Reminder set for {time}",
        "poll_created": "📊 Poll created!",
        "report_submitted": "✅ Report submitted (ID: {id}). Moderators will review it soon.",
        "raid_detected": "🚨 RAID DETECTED! {count} joins in 60 seconds",
        "slowmode_set": "✅ Slowmode set to {seconds} seconds",
        "giveaway_created": "🎉 **Giveaway created!**",
        "giveaway_ended": "🎉 **Giveaway ended!** Winner: {winner}",
        "giveaway_enter": "🎉 Enter Giveaway",
        "ai_config_updated": "✅ AI settings updated!",
        "ai_channel_added": "✅ Channel {channel} added for AI.",
        "ai_channel_removed": "✅ Channel {channel} removed from AI.",
        "ai_dm_toggle": "✅ AI in DMs is now {state}.",
        "ai_auto_respond_toggle": "✅ AI auto-respond is now {state}.",
        "ai_help": "Use `/ai` to configure AI on this server, or just send a message in a configured channel.",
    },
}
bot.MESSAGES = MESSAGES


@lru_cache(maxsize=128)
def _get_cached_lang(guild_id: int) -> str:
    """Cache guild language to avoid DB calls on every message"""
    session = SessionLocal()
    try:
        config = session.query(GuildConfig).filter_by(guild_id=guild_id).first()
        if config and config.language:
            return str(config.language)
        return "ru"
    finally:
        session.close()


def invalidate_lang_cache(guild_id: int):
    _get_cached_lang.cache_clear()


def get_config(session, guild_id: int):
    config = session.query(GuildConfig).filter_by(guild_id=guild_id).first()
    if not config:
        config = GuildConfig(guild_id=guild_id)
        session.add(config)
        session.commit()
    return config


def get_msg(guild_id: int, key: str, **kwargs) -> str:
    lang = _get_cached_lang(guild_id)
    messages = MESSAGES.get(lang, MESSAGES["ru"])
    msg_template = messages.get(key, key)
    try:
        return msg_template.format(**kwargs)
    except KeyError:
        return msg_template


from discord import app_commands


async def async_commit(session):
    """Run session.commit() in a thread executor to avoid blocking the event loop"""
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, session.commit)


@tasks.loop(minutes=1)
async def check_temp_bans():
    session = SessionLocal()
    try:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        expired_bans = session.query(TempBan).filter(TempBan.unban_time <= now).all()
        for ban in expired_bans:
            guild = bot.get_guild(ban.guild_id)
            if guild:
                try:
                    user = await bot.fetch_user(ban.user_id)
                    await guild.unban(user, reason="Tempban expired")
                    config = get_config(session, guild.id)
                    if config.target_channel_id:
                        channel = bot.get_channel(config.target_channel_id)
                        if channel and hasattr(channel, "send"):
                            await channel.send(
                                get_msg(guild.id, "unbanned_auto", user=user.name)
                            )
                    try:
                        dm = discord.Embed(
                            title=get_msg(guild.id, "unbanned"),
                            description=get_msg(guild.id, "dm_unban", server=guild.name, reason="Tempban expired"),
                            color=discord.Color.green(),
                        )
                        await user.send(embed=dm)
                    except:
                        pass
                except Exception as e:
                    logger.error(f"Error unbanning user {ban.user_id}: {e}")
            session.delete(ban)
        await async_commit(session)
    except Exception as e:
        logger.error(f"Error checking temp bans: {e}")
    finally:
        session.close()


@tasks.loop(minutes=2)
async def update_status():
    session = SessionLocal()
    try:
        repo_count = session.query(RepoSnapshot).count()
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{repo_count} GitHub репозиториев | v{BOT_VERSION}",
        )
        await bot.change_presence(activity=activity, status=discord.Status.online)
    except Exception as e:
        logger.error(f"Error updating status: {e}")
    finally:
        session.close()


async def github_api_call(call_func, *args, max_retries=3, **kwargs):
    """Async wrapper for GitHub API with rate limiting"""
    for attempt in range(max_retries):
        try:
            return await asyncio.to_thread(call_func, *args, **kwargs)
        except Exception as e:
            if "rate limit" in str(e).lower() and attempt < max_retries - 1:
                wait = 60 * (attempt + 1)
                logger.warning(f"GitHub rate limited, waiting {wait}s...")
                await asyncio.sleep(wait)
                continue
            raise


@bot.event
async def on_ready():
    if bot.user:
        logger.info(f"Logged in as {bot.user.name}")
        logger.info(f"Bot Version: {BOT_VERSION}")

    try:
        from update_checker import check_and_update
        logger.info("🔍 Checking for updates...")
        update_info = await check_and_update(BOT_VERSION, auto_update=False)
        if update_info:
            logger.warning("=" * 60)
            logger.warning(f"🎉 NEW VERSION AVAILABLE: v{update_info.get('version')}")
            logger.warning(f"📝 Release: {update_info.get('name')}")
            logger.warning(f"🔗 URL: {update_info.get('html_url')}")
            logger.warning("=" * 60)
            logger.info("💡 To update, run: git pull origin main")
        else:
            logger.info("✅ Bot is up to date!")
    except Exception as e:
        logger.error(f"Failed to check for updates: {e}")

    init_db()

    if not update_status.is_running():
        update_status.start()

    for entry in os.listdir("./cogs"):
        path = os.path.join("./cogs", entry)
        if entry.startswith("__"):
            continue
        if entry.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{entry[:-3]}")
                logger.info(f"Loaded cog: {entry}")
            except Exception as e:
                logger.error(f"Failed to load cog {entry}: {e}")
        elif os.path.isdir(path):
            init_file = os.path.join(path, "__init__.py")
            if os.path.exists(init_file):
                try:
                    await bot.load_extension(f"cogs.{entry}")
                    logger.info(f"Loaded cog package: {entry}")
                except Exception as e:
                    logger.error(f"Failed to load cog package {entry}: {e}")

    from cogs.tickets import TicketPersistentView
    from cogs.verifications.verification import VerificationView
    from database import VerificationConfig, TicketCategory

    session = SessionLocal()
    try:
        ticket_guilds = session.query(TicketCategory.guild_id).distinct().all()
        for (tgid,) in ticket_guilds:
            cats = session.query(TicketCategory.name).filter_by(guild_id=tgid).all()
            cat_names = [c[0] for c in cats]
            mode = "dropdown"
            color = 0x2ecc71
            bot.add_view(TicketPersistentView(cat_names, mode, color))

        vconfigs = session.query(VerificationConfig).all()
        for vc in vconfigs:
            bot.add_view(VerificationView(vc.guild_id, "buttons"))
    finally:
        session.close()

    try:
        await bot.load_extension("ai.chat")
        logger.info("Loaded AI chat cog")
    except Exception as e:
        logger.error(f"Failed to load AI chat cog: {e}")

    if not check_temp_bans.is_running():
        check_temp_bans.start()

    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logger.error(f"Error syncing commands: {e}")

    if not check_github_updates.is_running():
        check_github_updates.start()


@bot.tree.command(name="set_channel", description="Sets the notification channel")
@app_commands.checks.has_permissions(administrator=True)
async def set_channel_slash(
    interaction: discord.Interaction, channel: discord.TextChannel
):
    if not interaction.guild:
        return
    session = SessionLocal()
    try:
        config = get_config(session, interaction.guild.id)
        config.target_channel_id = channel.id
        session.commit()
        await interaction.response.send_message(
            get_msg(interaction.guild.id, "set_channel", channel=channel.name)
        )
    finally:
        session.close()


@bot.tree.command(name="set_log_channel", description="Sets the log channel for message logs")
@app_commands.checks.has_permissions(administrator=True)
async def set_log_channel(
    interaction: discord.Interaction, channel: discord.TextChannel
):
    if not interaction.guild:
        return
    session = SessionLocal()
    try:
        config = get_config(session, interaction.guild.id)
        config.log_channel_id = channel.id
        session.commit()
        await interaction.response.send_message(
            f"✅ Log channel set to {channel.mention}"
        )
    finally:
        session.close()


@bot.tree.command(name="set_report_channel", description="Sets the report channel")
@app_commands.checks.has_permissions(administrator=True)
async def set_report_channel(
    interaction: discord.Interaction, channel: discord.TextChannel
):
    if not interaction.guild:
        return
    session = SessionLocal()
    try:
        config = get_config(session, interaction.guild.id)
        config.report_channel_id = channel.id
        session.commit()
        await interaction.response.send_message(
            f"✅ Report channel set to {channel.mention}"
        )
    finally:
        session.close()


@bot.tree.command(name="config", description="Configure bot modules and settings")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.choices(
    module=[
        app_commands.Choice(name="Levels", value="levels"),
        app_commands.Choice(name="GitHub Tracking", value="github"),
        app_commands.Choice(name="Welcome System", value="welcome"),
        app_commands.Choice(name="Economy", value="economy"),
        app_commands.Choice(name="Statistics", value="stats"),
        app_commands.Choice(name="AI Chat", value="ai"),
    ],
    action=[
        app_commands.Choice(name="Enable", value="enable"),
        app_commands.Choice(name="Disable", value="disable"),
    ],
)
async def config_slash(
    interaction: discord.Interaction,
    module: app_commands.Choice[str],
    action: app_commands.Choice[str],
):
    if not interaction.guild:
        return
    session = SessionLocal()
    try:
        config = get_config(session, interaction.guild.id)
        enabled = action.value == "enable"

        if module.value == "levels":
            config.levels_enabled = enabled
        elif module.value == "github":
            config.github_enabled = enabled
        elif module.value == "welcome":
            config.welcome_enabled = enabled
        elif module.value == "economy":
            config.economy_enabled = enabled
        elif module.value == "stats":
            config.stats_enabled = enabled
        elif module.value == "ai":
            config.ai_enabled = enabled

        session.commit()

        state_key = "enabled" if enabled else "disabled"
        state_text = get_msg(interaction.guild.id, state_key)
        await interaction.response.send_message(
            get_msg(
                interaction.guild.id,
                "module_updated",
                module=module.name,
                state=state_text,
            )
        )
    finally:
        session.close()


@bot.tree.command(name="set_color", description="Sets the default embed color (Hex)")
@app_commands.checks.has_permissions(administrator=True)
async def set_color_slash(interaction: discord.Interaction, hex_color: str):
    if not interaction.guild:
        return
    try:
        color_int = int(hex_color.lstrip("#"), 16)
        if not (0 <= color_int <= 0xFFFFFF):
            await interaction.response.send_message(
                get_msg(interaction.guild.id, "invalid_color"), ephemeral=True
            )
            return
        session = SessionLocal()
        try:
            config = get_config(session, interaction.guild.id)
            config.embed_color = color_int
            session.commit()
            await interaction.response.send_message(
                get_msg(interaction.guild.id, "color_updated", color=hex_color),
                embed=discord.Embed(
                    description="New color preview", color=discord.Color(color_int)
                ),
            )
        finally:
            session.close()
    except ValueError:
        await interaction.response.send_message(
            get_msg(interaction.guild.id, "invalid_color"), ephemeral=True
        )


@bot.tree.command(name="set_lang", description="Sets the bot language for this server")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.choices(
    language=[
        app_commands.Choice(name="Русский", value="ru"),
        app_commands.Choice(name="English", value="en"),
    ]
)
async def set_lang_slash(
    interaction: discord.Interaction, language: app_commands.Choice[str]
):
    if not interaction.guild:
        return
    session = SessionLocal()
    try:
        config = get_config(session, interaction.guild.id)
        config.language = language.value
        session.commit()
        invalidate_lang_cache(interaction.guild.id)
        await interaction.response.send_message(
            get_msg(interaction.guild.id, "lang_updated")
        )
    finally:
        session.close()

@bot.tree.command(
    name="status", description="Shows the current status and settings of the bot"
)
async def status_slash(interaction: discord.Interaction):
    if not interaction.guild:
        return
    session = SessionLocal()
    try:
        config = get_config(session, interaction.guild.id)
        tracked = (
            session.query(TrackedUser).filter_by(guild_id=interaction.guild.id).all()
        )

        embed_color = int(config.embed_color) if config.embed_color else 0x3498DB
        embed = discord.Embed(
            title=f"Server Settings - {interaction.guild.name}",
            color=discord.Color(embed_color),
        )
        embed.add_field(
            name="Language",
            value=str(config.language).upper() if config.language else "RU",
            inline=True,
        )
        embed.add_field(
            name="Notification Channel",
            value=f"<#{config.target_channel_id}>"
            if config.target_channel_id
            else "None",
            inline=True,
        )
        embed.add_field(
            name="Mod Log Channel",
            value=f"<#{config.mod_log_channel_id}>"
            if config.mod_log_channel_id
            else "None",
            inline=True,
        )
        embed.add_field(
            name="Message Log Channel",
            value=f"<#{config.log_channel_id}>"
            if config.log_channel_id
            else "None",
            inline=True,
        )
        embed.add_field(
            name="Report Channel",
            value=f"<#{config.report_channel_id}>"
            if config.report_channel_id
            else "None",
            inline=True,
        )

        modules = []
        modules.append(f"Levels {'✅' if config.levels_enabled else '❌'}")
        modules.append(f"GitHub {'✅' if config.github_enabled else '❌'}")
        modules.append(f"Welcome {'✅' if config.welcome_enabled else '❌'}")
        modules.append(f"Economy {'✅' if config.economy_enabled else '❌'}")
        modules.append(f"Statistics {'✅' if config.stats_enabled else '❌'}")
        modules.append(f"AI Chat {'✅' if config.ai_enabled else '❌'}")

        embed.add_field(name="Modules Status", value="\n".join(modules), inline=False)

        users_list = (
            ", ".join([str(u.github_username) for u in tracked]) if tracked else "None"
        )
        embed.add_field(name="Tracked GitHub Users", value=users_list, inline=False)
        embed.set_footer(text=f"Bot Version: {BOT_VERSION}")

        await interaction.response.send_message(embed=embed)
    finally:
        session.close()


@bot.tree.command(name="version", description="Shows bot version information")
async def version_slash(interaction: discord.Interaction):
    if not interaction.guild:
        return

    session = SessionLocal()
    try:
        config = session.query(GuildConfig).filter_by(guild_id=interaction.guild.id).first()
        color_int = int(config.embed_color) if config and config.embed_color else 0x3498db

        try:
            import json
            with open(".version", "r", encoding="utf-8") as f:
                version_data = json.load(f)
        except Exception as e:
            logger.warning(f"Could not load .version file: {e}")
            version_data = {"version": BOT_VERSION, "release_date": "2026-04-17"}

        release_date = version_data.get("release_date", "2026-04-17")
        try:
            date_obj = datetime.strptime(release_date, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%B %d, %Y")
        except:
            formatted_date = release_date

        embed = discord.Embed(
            title="🤖 Bot Version Information",
            description=f"**Alfheim Guide Bot**\nVersion `{version_data.get('version', BOT_VERSION)}`",
            color=discord.Color(color_int)
        )

        embed.add_field(
            name="📦 Release",
            value=f"Version: `{version_data.get('version', BOT_VERSION)}`\nCodename: `{version_data.get('codename', 'Unknown')}`\nDate: `{formatted_date}`",
            inline=False
        )

        features = version_data.get("features", [])
        feature_emojis = {
            "Level System with Modals": "📊",
            "Giveaway System": "🎁",
            "Code Verification": "🔐",
            "Enhanced Voice Channels": "🎤",
            "Advanced Moderation": "🛡️",
            "Customizable Welcome": "👋",
            "Economy System": "💰",
            "Auto-Update System": "🔄",
            "GitHub Tracking": "🐙",
        }

        features_text = "\n".join([
            f"• {feature_emojis.get(f, '✨')} {f}"
            for f in features[:8]
        ])

        embed.add_field(
            name="✨ Key Features",
            value=features_text or "• Multiple features available",
            inline=False
        )

        embed.add_field(
            name="📊 Statistics",
            value=f"• Commands: `60+`\n• Modules: `12+`\n• Languages: `RU/EN`",
            inline=True
        )

        embed.add_field(
            name="🔗 Links",
            value="[GitHub](https://github.com/animesao/alfheimguide)\n[Discord](https://dsc.gg/alfheimguide)\n[Website](http://animesao.spcfy.eu/)",
            inline=True
        )

        embed.set_footer(text=f"Alfheim Guide Bot v{version_data.get('version', BOT_VERSION)}")
        if interaction.client.user:
            embed.set_thumbnail(url=interaction.client.user.display_avatar.url)

        await interaction.response.send_message(embed=embed)
    finally:
        session.close()


@bot.tree.command(name="add_user", description="Adds a GitHub user to track")
async def add_user_slash(interaction: discord.Interaction, github_username: str):
    if not interaction.guild or not g:
        return
    await interaction.response.defer()
    session = SessionLocal()
    try:
        config = get_config(session, interaction.guild.id)
        if not config.github_enabled:
            await interaction.followup.send(
                get_msg(interaction.guild.id, "github_disabled")
            )
            return

        try:
            github_user = await asyncio.to_thread(g.get_user, github_username)
            username_to_store = github_user.login
        except:
            search_results = await asyncio.to_thread(g.search_users, github_username)
            if search_results.totalCount > 0:
                github_user = search_results[0]
                username_to_store = github_user.login
            else:
                await interaction.followup.send(
                    get_msg(interaction.guild.id, "user_not_found", username=github_username)
                )
                return

        existing = (
            session.query(TrackedUser)
            .filter_by(guild_id=interaction.guild.id, github_username=username_to_store)
            .first()
        )
        if existing:
            await interaction.followup.send(
                get_msg(interaction.guild.id, "user_exists", username=username_to_store)
            )
            return

        new_user = TrackedUser(
            guild_id=interaction.guild.id, github_username=username_to_store
        )
        session.add(new_user)
        session.flush()

        repo_count = 0
        repos = await asyncio.to_thread(list, github_user.get_repos())
        for repo in repos:
            pushed_at = repo.pushed_at
            if pushed_at.tzinfo is None:
                pushed_at = pushed_at.replace(tzinfo=timezone.utc)
            snapshot = RepoSnapshot(
                tracked_user_id=new_user.id,
                repo_name=repo.name,
                last_pushed_at=pushed_at,
            )
            session.add(snapshot)
            repo_count += 1

        session.commit()
        await interaction.followup.send(
            get_msg(interaction.guild.id, "tracking_started", username=username_to_store, count=repo_count)
        )
    finally:
        session.close()


@bot.tree.command(name="remove_user", description="Removes a GitHub user from tracking")
@app_commands.checks.has_permissions(administrator=True)
async def remove_user_slash(interaction: discord.Interaction, github_username: str):
    if not interaction.guild:
        return
    session = SessionLocal()
    try:
        tracked_user = (
            session.query(TrackedUser)
            .filter_by(guild_id=interaction.guild.id, github_username=github_username)
            .first()
        )
        if not tracked_user:
            await interaction.response.send_message(
                get_msg(interaction.guild.id, "user_not_tracked", username=github_username)
            )
            return

        session.query(RepoSnapshot).filter_by(tracked_user_id=tracked_user.id).delete()
        session.delete(tracked_user)
        session.commit()

        await interaction.response.send_message(
            get_msg(interaction.guild.id, "user_removed", username=github_username)
        )
    finally:
        session.close()


@tasks.loop(minutes=5)
async def check_github_updates():
    if not g:
        return
    session = SessionLocal()
    try:
        tracked_users = session.query(TrackedUser).all()
        for user_record in tracked_users:
            config = (
                session.query(GuildConfig)
                .filter_by(guild_id=user_record.guild_id)
                .first()
            )
            if not config or not config.github_enabled or not config.target_channel_id:
                continue

            channel = bot.get_channel(config.target_channel_id)
            if not channel or not hasattr(channel, "send"):
                continue

            lang = str(config.language or "ru")
            msgs = MESSAGES.get(lang, MESSAGES["ru"])

            try:
                github_user = await asyncio.to_thread(
                    g.get_user, user_record.github_username
                )
                repos = await asyncio.to_thread(list, github_user.get_repos())
                current_repos = {repo.name: repo for repo in repos}
                snapshots = {
                    s.repo_name: s
                    for s in session.query(RepoSnapshot)
                    .filter_by(tracked_user_id=user_record.id)
                    .all()
                }

                for repo_name in list(snapshots.keys()):
                    if repo_name not in current_repos:
                        embed = discord.Embed(
                            title="🗑️ Repository Deleted" if lang == "en" else "🗑️ Репозиторий удалён",
                            description=f"### {repo_name}\n*This repository has been deleted or made private*" if lang == "en" else f"### {repo_name}\n*Этот репозиторий был удалён или сделан приватным*",
                            color=discord.Color.from_rgb(237, 66, 69),
                            timestamp=datetime.now(timezone.utc)
                        )
                        embed.set_author(
                            name=f"{github_user.login} • GitHub",
                            icon_url=github_user.avatar_url,
                            url=github_user.html_url
                        )
                        embed.set_footer(
                            text="GitHub Tracker",
                            icon_url="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
                        )
                        await channel.send(embed=embed)
                        session.delete(snapshots[repo_name])
                        await async_commit(session)

                for repo_name, repo in current_repos.items():
                    snapshot = snapshots.get(repo_name)
                    repo_pushed_at = repo.pushed_at
                    if repo_pushed_at.tzinfo is None:
                        repo_pushed_at = repo_pushed_at.replace(tzinfo=timezone.utc)

                    embed_color = int(config.embed_color) if config.embed_color else 0x3498DB
                    embed = discord.Embed(color=discord.Color(embed_color))
                    embed.set_author(
                        name=github_user.login,
                        icon_url=github_user.avatar_url,
                        url=github_user.html_url,
                    )
                    embed.set_footer(
                        text=f"GitHub Tracker • {datetime.now(timezone.utc).strftime('%H:%M:%S')} UTC"
                    )

                    if not snapshot:
                        new_snapshot = RepoSnapshot(
                            tracked_user_id=user_record.id,
                            repo_name=repo.name,
                            last_pushed_at=repo_pushed_at,
                        )
                        session.add(new_snapshot)
                        await async_commit(session)

                        embed.title = "🚀 New Repository" if lang == "en" else "🚀 Новый репозиторий"
                        embed.description = f"### [{repo.name}]({repo.html_url})\n{repo.description or ('*No description provided*' if lang == 'en' else '*Описание отсутствует*')}"
                        embed.color = discord.Color.from_rgb(87, 242, 135)
                        embed.timestamp = datetime.now(timezone.utc)

                        stats_text = f"⭐ **{repo.stargazers_count:,}**  •  🍴 **{repo.forks_count:,}**  •  👁️ **{repo.watchers_count:,}**"
                        embed.add_field(name="📊 Stats" if lang == "en" else "📊 Статистика", value=stats_text, inline=False)

                        info_lines = []
                        if repo.language:
                            info_lines.append(f"💻 **Language:** `{repo.language}`" if lang == "en" else f"💻 **Язык:** `{repo.language}`")
                        info_lines.append(f"🔓 **Visibility:** {'Public' if not repo.private else 'Private'}" if lang == "en" else f"🔓 **Видимость:** {'Публичный' if not repo.private else 'Приватный'}")
                        if repo.license:
                            info_lines.append(f"📜 **License:** {repo.license.name}" if lang == "en" else f"📜 **Лицензия:** {repo.license.name}")

                        embed.add_field(name="ℹ️ Info" if lang == "en" else "ℹ️ Информация", value="\n".join(info_lines), inline=False)
                        embed.set_author(
                            name=f"{github_user.login} • GitHub",
                            icon_url=github_user.avatar_url,
                            url=github_user.html_url
                        )
                        embed.set_footer(
                            text="GitHub Tracker",
                            icon_url="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
                        )
                        await channel.send(embed=embed)

                    elif repo_pushed_at > snapshot.last_pushed_at.replace(tzinfo=timezone.utc):
                        old_push = snapshot.last_pushed_at.replace(tzinfo=timezone.utc)
                        snapshot.last_pushed_at = repo_pushed_at
                        await async_commit(session)

                        embed.title = "📝 Repository Update" if lang == "en" else "📝 Обновление репозитория"
                        embed.description = f"### [{repo.name}]({repo.html_url})\n{repo.description or ('*No description*' if lang == 'en' else '*Без описания*')}"
                        embed.color = discord.Color.from_rgb(88, 166, 255)
                        embed.timestamp = repo_pushed_at

                        try:
                            commits = await asyncio.to_thread(list, repo.get_commits(since=old_push))
                            commit_list = []
                            commit_count = 0

                            for c in commits:
                                if c.commit.author.date.replace(tzinfo=timezone.utc) > old_push:
                                    commit_count += 1
                                    msg = c.commit.message.split("\n")[0]
                                    if len(msg) > 60:
                                        msg = msg[:57] + "..."
                                    commit_list.append(
                                        f"[`{c.sha[:7]}`]({c.html_url}) {msg}"
                                    )

                            if commit_list:
                                branch_stats = f"🌿 `{repo.default_branch}`  •  📝 **{commit_count}** commit{'s' if commit_count != 1 else ''}"
                                embed.add_field(
                                    name="📌 Details" if lang == "en" else "📌 Детали",
                                    value=branch_stats,
                                    inline=False,
                                )

                                commits_to_show = commit_list[:5]
                                commits_text = "\n".join(commits_to_show)
                                if len(commit_list) > 5:
                                    commits_text += f"\n*...and {len(commit_list) - 5} more commit(s)*" if lang == "en" else f"\n*...и ещё {len(commit_list) - 5} коммит(ов)*"

                                embed.add_field(
                                    name=f"💬 Commits ({min(5, len(commit_list))})" if lang == "en" else f"💬 Коммиты ({min(5, len(commit_list))})",
                                    value=commits_text,
                                    inline=False,
                                )

                                embed.set_author(
                                    name=f"{github_user.login} • GitHub",
                                    icon_url=github_user.avatar_url,
                                    url=github_user.html_url
                                )
                                embed.set_footer(
                                    text="GitHub Tracker",
                                    icon_url="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
                                )
                                await channel.send(embed=embed)
                        except Exception as e:
                            logger.error(f"Error fetching commits for {repo.name}: {e}")

                for repo_name, repo in current_repos.items():
                    try:
                        releases = await asyncio.to_thread(list, repo.get_releases())
                        if not releases:
                            continue

                        release_snapshots = {
                            r.release_tag: r
                            for r in session.query(ReleaseSnapshot)
                            .filter_by(tracked_user_id=user_record.id, repo_name=repo.name)
                            .all()
                        }

                        for release in releases[:5]:
                            if release.tag_name not in release_snapshots:
                                published_at = release.published_at
                                if published_at.tzinfo is None:
                                    published_at = published_at.replace(tzinfo=timezone.utc)

                                new_release = ReleaseSnapshot(
                                    tracked_user_id=user_record.id,
                                    repo_name=repo.name,
                                    release_tag=release.tag_name,
                                    release_name=release.name,
                                    published_at=published_at,
                                    is_prerelease=release.prerelease,
                                    is_draft=release.draft,
                                )
                                session.add(new_release)
                                await async_commit(session)

                                if release.draft:
                                    continue

                                if release.prerelease:
                                    embed_color_rel = discord.Color.from_rgb(255, 191, 0)
                                    title = "🔶 Pre-Release" if lang == "en" else "🔶 Пре-релиз"
                                else:
                                    embed_color_rel = discord.Color.from_rgb(46, 204, 113)
                                    title = "🎉 New Release" if lang == "en" else "🎉 Новый релиз"

                                embed = discord.Embed(
                                    title=title,
                                    description=f"### [{repo.name}]({repo.html_url}) `{release.tag_name}`\n**{release.name or release.tag_name}**",
                                    color=embed_color_rel,
                                    timestamp=published_at,
                                )

                                info_lines = []
                                info_lines.append(f"🏷️ **Tag:** `{release.tag_name}`")
                                if release.target_commitish:
                                    info_lines.append(f"🌿 **Branch:** `{release.target_commitish}`")
                                if release.author:
                                    info_lines.append(f"👤 **Author:** [{release.author.login}]({release.author.html_url})")

                                embed.add_field(
                                    name="ℹ️ Info" if lang == "en" else "ℹ️ Информация",
                                    value="\n".join(info_lines),
                                    inline=False,
                                )

                                if release.body:
                                    body_lines = release.body.split("\n")
                                    body_preview = "\n".join(body_lines[:10])
                                    if len(body_preview) > 500:
                                        body_preview = body_preview[:497] + "..."
                                    elif len(body_lines) > 10:
                                        body_preview += f"\n\n*...and {len(body_lines) - 10} more lines*" if lang == "en" else f"\n\n*...и ещё {len(body_lines) - 10} строк*"

                                    embed.add_field(
                                        name="📝 Release Notes" if lang == "en" else "📝 Заметки о релизе",
                                        value=body_preview or ("*No release notes*" if lang == "en" else "*Нет заметок*"),
                                        inline=False,
                                    )

                                links = f"[🔗 Release Page]({release.html_url})"
                                embed.add_field(
                                    name="🔗 Links" if lang == "en" else "🔗 Ссылки",
                                    value=links,
                                    inline=False,
                                )

                                embed.set_author(
                                    name=f"{github_user.login} • GitHub",
                                    icon_url=github_user.avatar_url,
                                    url=github_user.html_url,
                                )
                                embed.set_footer(
                                    text="GitHub Tracker • Release",
                                    icon_url="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
                                )
                                await channel.send(embed=embed)

                    except Exception as e:
                        logger.error(f"Error checking releases for {repo.name}: {e}")

            except Exception as e:
                logger.error(f"Error checking {user_record.github_username}: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    if not DISCORD_TOKEN:
        logger.critical("Error: DISCORD_TOKEN must be set in .env")
    elif not GITHUB_TOKEN:
        logger.warning("GITHUB_TOKEN not set — GitHub tracking disabled")
        bot.run(DISCORD_TOKEN)
    else:
        bot.run(DISCORD_TOKEN)
