import asyncio
import logging
import os
from discord.ext import commands
from discord import app_commands
import discord
from openai import OpenAI
from database import SessionLocal, GuildConfig

ai_token = os.getenv("AI_TOKEN")

client = None
if ai_token:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=ai_token,
    )

conversation_history = {}


def _get_msg(guild_id: int | None, key: str, **kwargs) -> str:
    lang = "ru"
    if guild_id:
        session = SessionLocal()
        try:
            config = session.query(GuildConfig).filter_by(guild_id=guild_id).first()
            if config and config.language:
                lang = str(config.language)
        finally:
            session.close()
    messages = {
        "ru": {
            "ai_disabled": "❌ AI модуль отключён на этом сервере.",
            "ai_no_token": "❌ AI_TOKEN не настроен в .env",
            "ai_dm_disabled": "❌ AI в ЛС отключён на этом сервере.",
            "ai_channel_added": "✅ Канал {channel} добавлен для AI.",
            "ai_channel_removed": "✅ Канал {channel} удалён из AI.",
            "ai_channel_list": "📋 Настроенные каналы AI:\n{channels}",
            "ai_no_channels": "⚠️ Нет настроенных каналов. Используйте `!ask [сообщение]` для общения.",
            "ai_dm_toggle": "✅ AI в ЛС теперь {state}.",
            "ai_auto_respond_toggle": "✅ Авто-ответ AI теперь {state}.",
            "ai_config_title": "🤖 Настройка AI",
            "ai_config_desc": "Настройте работу AI на сервере.",
            "ai_auto_respond": "Авто-ответ",
            "ai_auto_respond_desc": "Отвечать на сообщения в настроенных каналах",
            "ai_dm": "ЛС",
            "ai_dm_desc": "Разрешить общение с AI в ЛС",
            "ai_channels": "Каналы",
            "ai_channels_desc": "Количество настроенных каналов: {count}",
            "ai_status_enabled": "Включён",
            "ai_status_disabled": "Выключен",
            "ai_reset": "🧹 История беседы очищена!",
            "ai_help": "**🤖 AI Помощник (Nemotron 30B):**\nНапишите сообщение в настроенном канале или используйте `!ask [сообщение]`\n`!clear` — очистить историю\n`/ai ask` — спросить AI\n`/ai channel` — управление каналами\n`/ai toggle` — вкл/выкл авто-ответ и ЛС\n`/ai reset` — сбросить историю\n`/help` — все команды бота",
            "ai_thinking": "🤔 Думаю...",
        },
        "en": {
            "ai_disabled": "❌ AI module is disabled on this server.",
            "ai_no_token": "❌ AI_TOKEN is not configured in .env",
            "ai_dm_disabled": "❌ AI in DMs is disabled on this server.",
            "ai_channel_added": "✅ Channel {channel} added for AI.",
            "ai_channel_removed": "✅ Channel {channel} removed from AI.",
            "ai_channel_list": "📋 Configured AI channels:\n{channels}",
            "ai_no_channels": "⚠️ No channels configured. Use `!ask [message]` to chat.",
            "ai_dm_toggle": "✅ AI in DMs is now {state}.",
            "ai_auto_respond_toggle": "✅ AI auto-respond is now {state}.",
            "ai_config_title": "🤖 AI Settings",
            "ai_config_desc": "Configure AI settings for this server.",
            "ai_auto_respond": "Auto-Respond",
            "ai_auto_respond_desc": "Reply to messages in configured channels",
            "ai_dm": "DMs",
            "ai_dm_desc": "Allow AI chat in Direct Messages",
            "ai_channels": "Channels",
            "ai_channels_desc": "Configured channels count: {count}",
            "ai_status_enabled": "Enabled",
            "ai_status_disabled": "Disabled",
            "ai_reset": "🧹 Conversation history cleared!",
            "ai_help": "**🤖 AI Assistant (Nemotron 30B):**\nSend a message in a configured channel or use `!ask [message]`\n`!clear` — clear history\n`/ai ask` — ask AI\n`/ai channel` — manage channels\n`/ai toggle` — toggle auto-respond & DMs\n`/ai reset` — reset history\n`/help` — all bot commands",
            "ai_thinking": "🤔 Thinking...",
        },
    }
    msg_map = messages.get(lang, messages["ru"])
    template = msg_map.get(key, key)
    try:
        return template.format(**kwargs)
    except KeyError:
        return template


def _get_conversation_key(channel_id: int, guild_id: int | None = None) -> str:
    if guild_id:
        return f"{guild_id}:{channel_id}"
    return f"dm:{channel_id}"


_ai_cleanup_counter = 0

async def _get_ai_response(conv_key: str, message_text: str) -> str | None:
    global client, _ai_cleanup_counter
    ai_token = os.getenv("AI_TOKEN")
    if ai_token and (not client or client.api_key != ai_token):
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=ai_token,
        )
    if not client or not client.api_key or client.api_key == "your_openrouter_token_here":
        return None

    _ai_cleanup_counter += 1
    if _ai_cleanup_counter % 100 == 0:
        limit = len(conversation_history) - 500
        if limit > 0:
            for k in list(conversation_history.keys())[:limit]:
                del conversation_history[k]

    if conv_key not in conversation_history:
        conversation_history[conv_key] = []

    conversation_history[conv_key].append({
        "role": "user",
        "content": message_text
    })

    if len(conversation_history[conv_key]) > 10:
        conversation_history[conv_key] = conversation_history[conv_key][-10:]

    try:
        def get_completion():
            return client.chat.completions.create(
                model="nvidia/nemotron-3-nano-30b-a3b:free",
                messages=conversation_history[conv_key],
                extra_body={"reasoning": {"enabled": True}}
            )
        response = await asyncio.get_event_loop().run_in_executor(None, get_completion)
        assistant_msg = response.choices[0].message
        content = assistant_msg.content
        reasoning = getattr(assistant_msg, 'reasoning_details', None)

        history_entry = {"role": "assistant", "content": content}
        if reasoning:
            history_entry["reasoning_details"] = reasoning
        conversation_history[conv_key].append(history_entry)
        return content
    except Exception as e:
        logging.error(f"AI API error: {e}")
        return f"❌ Ошибка API: {str(e)}"


async def _send_long(ctx_or_interaction, content: str, is_slash: bool = False):
    if is_slash and hasattr(ctx_or_interaction, "followup"):
        if len(content) > 1900:
            chunks = [content[i:i+1900] for i in range(0, len(content), 1900)]
            for chunk in chunks:
                await ctx_or_interaction.followup.send(chunk)
                await asyncio.sleep(0.5)
        else:
            if not ctx_or_interaction.response.is_done():
                await ctx_or_interaction.response.send_message(content)
            else:
                await ctx_or_interaction.followup.send(content)
    else:
        if len(content) > 1900:
            chunks = [content[i:i+1900] for i in range(0, len(content), 1900)]
            for chunk in chunks:
                await ctx_or_interaction.send(chunk)
                await asyncio.sleep(0.5)
        else:
            await ctx_or_interaction.send(content)


class AIChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _get_config(self, guild_id: int | None):
        if not guild_id:
            return None
        session = SessionLocal()
        try:
            return session.query(GuildConfig).filter_by(guild_id=guild_id).first()
        finally:
            session.close()

    def _can_respond_in_channel(self, guild_id: int, channel_id: int) -> bool:
        config = self._get_config(guild_id)
        if not config or not config.ai_enabled:
            return False
        if not config.ai_auto_respond:
            return False
        if not config.ai_channel_ids:
            return False
        channel_ids = [int(cid.strip()) for cid in config.ai_channel_ids.split(",") if cid.strip()]
        return channel_id in channel_ids

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if isinstance(message.channel, discord.DMChannel):
            config = self._get_config(None)
            await self._handle_dm(message)
            return

        guild_id = message.guild.id if message.guild else None
        if not guild_id:
            return

        if not self._can_respond_in_channel(guild_id, message.channel.id):
            return

        async with message.channel.typing():
            conv_key = _get_conversation_key(message.channel.id, guild_id)
            response = await _get_ai_response(conv_key, message.content)
            if response:
                await _send_long(message.channel, response)

    async def _handle_dm(self, message: discord.Message):
        if message.author.bot:
            return

        guild_id = None
        mutual = message.author.mutual_guilds
        if mutual:
            guild_id = mutual[0].id

        if guild_id:
            config = self._get_config(guild_id)
            if config and not config.ai_enabled:
                return
            if config and not config.ai_dm_enabled:
                return

        async with message.channel.typing():
            conv_key = _get_conversation_key(message.channel.id, None)
            response = await _get_ai_response(conv_key, message.content)
            if response:
                await _send_long(message.channel, response)

    @commands.command(name="ask")
    async def ask_command(self, ctx, *, message: str):
        guild_id = ctx.guild.id if ctx.guild else None
        config = self._get_config(guild_id) if guild_id else None
        if guild_id and config and not config.ai_enabled:
            await ctx.send(_get_msg(guild_id, "ai_disabled"))
            return

        async with ctx.typing():
            conv_key = _get_conversation_key(ctx.channel.id, guild_id)
            response = await _get_ai_response(conv_key, message)
            if response is None:
                await ctx.send(_get_msg(guild_id, "ai_no_token"))
            else:
                await _send_long(ctx, response)

    @commands.command(name="clear")
    async def clear_history(self, ctx):
        guild_id = ctx.guild.id if ctx.guild else None
        conv_key = _get_conversation_key(ctx.channel.id, guild_id)
        if conv_key in conversation_history:
            conversation_history[conv_key] = []
        await ctx.send(_get_msg(guild_id, "ai_reset"))

    @commands.command(name="helpai")
    async def helpai_command(self, ctx):
        guild_id = ctx.guild.id if ctx.guild else None
        await ctx.send(_get_msg(guild_id, "ai_help"))

    ai_group = app_commands.Group(name="ai", description="AI Chat settings and commands")

    @ai_group.command(name="ask", description="Ask AI a question")
    @app_commands.describe(message="Your question for the AI")
    async def ai_ask_slash(self, interaction: discord.Interaction, message: str):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command is not available in DMs.", ephemeral=True)
            return
        config = self._get_config(interaction.guild.id)
        if config and not config.ai_enabled:
            await interaction.response.send_message(_get_msg(interaction.guild.id, "ai_disabled"), ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        conv_key = _get_conversation_key(interaction.channel_id, interaction.guild.id)
        response = await _get_ai_response(conv_key, message)
        if response is None:
            await interaction.followup.send(_get_msg(interaction.guild.id, "ai_no_token"))
        else:
            await _send_long(interaction, response, is_slash=True)

    @ai_group.command(name="channel", description="Manage AI response channels")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(action="Add, remove, or list channels", channel="Channel to add/remove")
    @app_commands.choices(action=[
        app_commands.Choice(name="Add", value="add"),
        app_commands.Choice(name="Remove", value="remove"),
        app_commands.Choice(name="List", value="list"),
    ])
    async def ai_channel_slash(
        self,
        interaction: discord.Interaction,
        action: app_commands.Choice[str],
        channel: Optional[discord.TextChannel] = None,
    ):
        if not interaction.guild:
            return
        guild_id = interaction.guild.id
        session = SessionLocal()
        try:
            config = session.query(GuildConfig).filter_by(guild_id=guild_id).first()
            if not config:
                config = GuildConfig(guild_id=guild_id)
                session.add(config)
                session.commit()

            channel_ids = [int(cid.strip()) for cid in config.ai_channel_ids.split(",") if cid.strip()]

            if action.value == "add":
                if not channel:
                    await interaction.response.send_message("❌ Укажите канал.", ephemeral=True)
                    return
                if channel.id in channel_ids:
                    await interaction.response.send_message("⚠️ Канал уже добавлен.", ephemeral=True)
                    return
                channel_ids.append(channel.id)
                config.ai_channel_ids = ",".join(str(cid) for cid in channel_ids)
                session.commit()
                await interaction.response.send_message(
                    _get_msg(guild_id, "ai_channel_added", channel=channel.mention)
                )

            elif action.value == "remove":
                if not channel:
                    await interaction.response.send_message("❌ Укажите канал.", ephemeral=True)
                    return
                if channel.id not in channel_ids:
                    await interaction.response.send_message("⚠️ Канал не найден в списке.", ephemeral=True)
                    return
                channel_ids.remove(channel.id)
                config.ai_channel_ids = ",".join(str(cid) for cid in channel_ids)
                session.commit()
                await interaction.response.send_message(
                    _get_msg(guild_id, "ai_channel_removed", channel=channel.mention)
                )

            elif action.value == "list":
                if not channel_ids:
                    await interaction.response.send_message(
                        _get_msg(guild_id, "ai_no_channels"), ephemeral=True
                    )
                    return
                channels_text = "\n".join(f"<#{cid}>" for cid in channel_ids)
                await interaction.response.send_message(
                    _get_msg(guild_id, "ai_channel_list", channels=channels_text), ephemeral=True
                )
        finally:
            session.close()

    @ai_group.command(name="toggle", description="Toggle AI settings")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(setting="Setting to toggle")
    @app_commands.choices(setting=[
        app_commands.Choice(name="Auto-Respond", value="auto_respond"),
        app_commands.Choice(name="DMs", value="dm"),
    ])
    async def ai_toggle_slash(
        self,
        interaction: discord.Interaction,
        setting: app_commands.Choice[str],
    ):
        if not interaction.guild:
            return
        guild_id = interaction.guild.id
        session = SessionLocal()
        try:
            config = session.query(GuildConfig).filter_by(guild_id=guild_id).first()
            if not config:
                config = GuildConfig(guild_id=guild_id)
                session.add(config)
                session.commit()

            if setting.value == "auto_respond":
                config.ai_auto_respond = not config.ai_auto_respond
                session.commit()
                state = _get_msg(guild_id, "ai_status_enabled") if config.ai_auto_respond else _get_msg(guild_id, "ai_status_disabled")
                await interaction.response.send_message(
                    _get_msg(guild_id, "ai_auto_respond_toggle", state=state)
                )
            elif setting.value == "dm":
                config.ai_dm_enabled = not config.ai_dm_enabled
                session.commit()
                state = _get_msg(guild_id, "ai_status_enabled") if config.ai_dm_enabled else _get_msg(guild_id, "ai_status_disabled")
                await interaction.response.send_message(
                    _get_msg(guild_id, "ai_dm_toggle", state=state)
                )
        finally:
            session.close()

    @ai_group.command(name="reset", description="Reset conversation history in this channel")
    async def ai_reset_slash(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id if interaction.guild else None
        conv_key = _get_conversation_key(interaction.channel_id, guild_id)
        if conv_key in conversation_history:
            conversation_history[conv_key] = []
        await interaction.response.send_message(_get_msg(guild_id, "ai_reset"), ephemeral=True)


async def setup(bot):
    await bot.add_cog(AIChat(bot))
