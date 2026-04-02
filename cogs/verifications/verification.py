import discord
import uuid
import datetime
from discord.ext import commands
from discord import app_commands, ui
from database import SessionLocal, VerificationConfig, VerificationButton
from typing import Optional, List


BUTTON_STYLES = {
    "primary": discord.ButtonStyle.primary,
    "secondary": discord.ButtonStyle.secondary,
    "success": discord.ButtonStyle.success,
    "danger": discord.ButtonStyle.danger,
}

ACTION_TYPES = {
    "role": "Выдача роли",
    "roles": "Выдача нескольких ролей",
    "removerole": "Удаление роли",
    "togglerole": "Переключение роли",
    "dm": "Отправка ЛС",
    "captcha": "Капча (текстовый ввод)",
    "number_captcha": "Числовая капча",
    "dropdown": "Dropdown меню",
    "timeout": "Выдача таймаута",
    "kick": "Кик пользователя",
    "ban": "Бан пользователя",
    "nothing": "Просто кнопка",
    "welcome": "Приветственное сообщение",
    "reaction": "Добавить реакцию",
    "redirect": "Перенаправление в канал",
    "confirm": "Подтверждение",
    "link": "Кнопка-ссылка",
}

BUTTON_STYLE_NAMES = {
    "primary": "🔵 Основной (синий)",
    "secondary": "⚪ Вторичный (серый)",
    "success": "🟢 Успех (зелёный)",
    "danger": "🔴 Опасность (красный)",
}

VERIFICATION_PRESETS = {
    "simple": {
        "name": "📋 Простая верификация",
        "description": "Одна кнопка, одна роль. Минимализм.",
        "title": "🔐 Верификация",
        "description_text": "Добро пожаловать! Нажмите кнопку ниже для верификации на сервере.",
        "buttons": [
            {
                "label": "✅ Верифицироваться",
                "emoji": "✅",
                "style": "success",
                "action_type": "role",
            }
        ],
    },
    "rules": {
        "name": "📜 С подтверждением правил",
        "description": "Сначала правила, потом согласие.",
        "title": "📜 Правила сервера",
        "description_text": "Пожалуйста, ознакомьтесь с правилами и подтвердите согласие.",
        "buttons": [
            {
                "label": "📜 Читать правила",
                "emoji": "📜",
                "style": "primary",
                "action_type": "redirect",
            },
            {
                "label": "✅ Я согласен с правилами",
                "emoji": "✅",
                "style": "success",
                "action_type": "role",
            },
        ],
    },
    "age": {
        "name": "🎂 Возрастная верификация",
        "description": "Выбор возрастной категории.",
        "title": "🎂 Укажите ваш возраст",
        "description_text": "Выберите вашу возрастную категорию для доступа к контенту.",
        "buttons": [
            {
                "label": "🧒 До 16",
                "emoji": "🧒",
                "style": "secondary",
                "action_type": "role",
            },
            {
                "label": "👨 16-18",
                "emoji": "👨",
                "style": "primary",
                "action_type": "role",
            },
            {
                "label": "👴 18+",
                "emoji": "👴",
                "style": "success",
                "action_type": "role",
            },
        ],
    },
    "gamergender": {
        "name": "🎮Игровая + Пол",
        "description": "Выбор игр и гендера.",
        "title": "🎮 Расскажите о себе",
        "description_text": "Выберите ваши предпочтения для персонализации опыта.",
        "buttons": [
            {
                "label": "🎮 PC",
                "emoji": "🖥️",
                "style": "primary",
                "action_type": "roles",
            },
            {
                "label": "🎮 PlayStation",
                "emoji": "🎮",
                "style": "primary",
                "action_type": "roles",
            },
            {
                "label": "🎮 Xbox",
                "emoji": "🎮",
                "style": "primary",
                "action_type": "roles",
            },
            {
                "label": "🕹️ Nintendo",
                "emoji": "🕹️",
                "style": "primary",
                "action_type": "roles",
            },
            {
                "label": "👨 Мужчина",
                "emoji": "👨",
                "style": "secondary",
                "action_type": "role",
            },
            {
                "label": "👩 Женщина",
                "emoji": "👩",
                "style": "secondary",
                "action_type": "role",
            },
        ],
    },
    "captcha": {
        "name": "🔐 Капча",
        "description": "Защита от ботов с капчей.",
        "title": "🔐 Подтвердите, что вы человек",
        "description_text": "Введите код с картинки для верификации.",
        "buttons": [
            {
                "label": "🔄 Получить код",
                "emoji": "🔄",
                "style": "primary",
                "action_type": "captcha",
            },
            {
                "label": "📋 Ввести код",
                "emoji": "📋",
                "style": "success",
                "action_type": "captcha",
            },
        ],
    },
    "multi": {
        "name": "📚 Множественный выбор",
        "description": "Выбор нескольких интересов.",
        "title": "📚 Выберите ваши интересы",
        "description_text": "Отметьте темы, которые вам интересны.",
        "buttons": [
            {
                "label": "🎨 Арт",
                "emoji": "🎨",
                "style": "secondary",
                "action_type": "togglerole",
            },
            {
                "label": "🎵 Музыка",
                "emoji": "🎵",
                "style": "secondary",
                "action_type": "togglerole",
            },
            {
                "label": "🎮 Игры",
                "emoji": "🎮",
                "style": "secondary",
                "action_type": "togglerole",
            },
            {
                "label": "📷 Фото",
                "emoji": "📷",
                "style": "secondary",
                "action_type": "togglerole",
            },
            {
                "label": "💻 Программирование",
                "emoji": "💻",
                "style": "secondary",
                "action_type": "togglerole",
            },
            {
                "label": "🎬 Кино",
                "emoji": "🎬",
                "style": "secondary",
                "action_type": "togglerole",
            },
        ],
    },
    "nsfw": {
        "name": "🔞 NSFW верификация",
        "description": "Подтверждение возраста 18+.",
        "title": "🔞 Возрастное подтверждение",
        "description_text": "Подтвердите, что вам 18+ для доступа к контенту.",
        "buttons": [
            {
                "label": "✅ Мне 18+",
                "emoji": "✅",
                "style": "success",
                "action_type": "role",
            },
            {
                "label": "❌ Мне нет 18",
                "emoji": "❌",
                "style": "danger",
                "action_type": "nothing",
            },
        ],
    },
    "welcome": {
        "name": "👋 Приветственная верификация",
        "description": "С автоматическим приветствием.",
        "title": "👋 Добро пожаловать!",
        "description_text": "Нажмите кнопку для вступления на сервер.",
        "buttons": [
            {
                "label": "👋 Войти на сервер",
                "emoji": "👋",
                "style": "success",
                "action_type": "welcome",
            }
        ],
    },
    "roleshop": {
        "name": "🛒 Магазин ролей",
        "description": "Покупка ролей за реакции.",
        "title": "🛒 Магазин ролей",
        "description_text": "Получите роли поддержки за вашу помощь!",
        "buttons": [
            {
                "label": "⭐ VIP",
                "emoji": "⭐",
                "style": "success",
                "action_type": "role",
            },
            {
                "label": "💎 Premium",
                "emoji": "💎",
                "style": "primary",
                "action_type": "role",
            },
            {
                "label": "👑 Sponsor",
                "emoji": "👑",
                "style": "danger",
                "action_type": "role",
            },
            {
                "label": "🎨 Artist",
                "emoji": "🎨",
                "style": "secondary",
                "action_type": "role",
            },
        ],
    },
}


class CaptchaModal(ui.Modal, title="🔐 Верификация"):
    captcha_answer = ui.TextInput(
        label="Введите код",
        placeholder="Введите код с картинки",
        required=True,
        min_length=1,
        max_length=20,
    )

    def __init__(self, correct_answer: str, button_config: VerificationButton, bot):
        super().__init__(title="🔐 Подтверждение")
        self.captcha_answer.placeholder = correct_answer
        self.correct_answer = correct_answer
        self.button_config = button_config
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        if self.captcha_answer.value.strip() == self.correct_answer.strip():
            await self.execute_verification(interaction)
        else:
            await interaction.response.send_message(
                "❌ Неверный код! Попробуйте ещё раз.", ephemeral=True
            )


class NumberCaptchaModal(ui.Modal, title="🔢 Решите пример"):
    answer = ui.TextInput(
        label="Ответ",
        placeholder="Введите число",
        required=True,
        min_length=1,
        max_length=10,
    )

    def __init__(self, num1: int, num2: int, button_config: VerificationButton):
        super().__init__(title=f"🔢 Сколько будет {num1} + {num2}?")
        self.num1 = num1
        self.num2 = num2
        self.correct = str(num1 + num2)
        self.button_config = button_config

    async def on_submit(self, interaction: discord.Interaction):
        if self.answer.value.strip() == self.correct:
            await self.execute_verification(interaction)
        else:
            await interaction.response.send_message(
                f"❌ Неверно! Правильный ответ: {self.correct}", ephemeral=True
            )


class VerificationSelect(ui.Select):
    def __init__(
        self, options: List[discord.SelectOption], config_id: int, custom_id: str
    ):
        super().__init__(
            placeholder="Выберите...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id=custom_id,
        )
        self.config_id = config_id

    async def callback(self, interaction: discord.Interaction):
        await self.execute_verification(interaction)


class CustomButton(ui.Button):
    def __init__(self, button_config: VerificationButton):
        self.button_config = button_config
        emoji = button_config.emoji
        style = BUTTON_STYLES.get(button_config.style, discord.ButtonStyle.primary)

        super().__init__(
            label=button_config.label or "Кнопка",
            style=style,
            emoji=emoji,
            custom_id=f"verify_btn_{button_config.button_id}",
            row=button_config.order // 5 if button_config.order else 0,
            url=button_config.action_value
            if button_config.action_type == "link"
            else None,
        )

    async def callback(self, interaction: discord.Interaction):
        btn = self.button_config
        session = SessionLocal()

        try:
            config = (
                session.query(VerificationConfig)
                .filter_by(guild_id=interaction.guild_id)
                .first()
            )
            color = config.embed_color if config and config.embed_color else 0x3498DB

            action_type = btn.action_type or "role"
            action_value = btn.action_value

            if action_type == "role":
                await self.give_role(interaction, action_value, session)

            elif action_type == "roles":
                role_ids = action_value.split(",") if action_value else []
                for rid in role_ids:
                    rid = rid.strip()
                    if rid:
                        role = discord.utils.get(interaction.guild.roles, id=int(rid))
                        if role and role not in interaction.user.roles:
                            await interaction.user.add_roles(role)
                await interaction.response.send_message(
                    "✅ Роли выданы!", ephemeral=True
                )

            elif action_type == "removerole":
                role = (
                    discord.utils.get(interaction.guild.roles, id=int(action_value))
                    if action_value
                    else None
                )
                if role and role in interaction.user.roles:
                    await interaction.user.remove_roles(role)
                    await interaction.response.send_message(
                        f"✅ Роль {role.name} удалена!", ephemeral=True
                    )
                else:
                    await interaction.response.send_message(
                        "ℹ️ Роль не найдена или уже отсутствует!", ephemeral=True
                    )

            elif action_type == "togglerole":
                role = (
                    discord.utils.get(interaction.guild.roles, id=int(action_value))
                    if action_value
                    else None
                )
                if role:
                    if role in interaction.user.roles:
                        await interaction.user.remove_roles(role)
                        await interaction.response.send_message(
                            f"✅ Роль {role.name} удалена!", ephemeral=True
                        )
                    else:
                        await interaction.user.add_roles(role)
                        await interaction.response.send_message(
                            f"✅ Роль {role.name} выдана!", ephemeral=True
                        )

            elif action_type == "captcha":
                correct = action_value or "VERIFY"
                modal = CaptchaModal(correct, btn, interaction.client)
                await interaction.response.send_modal(modal)
                return

            elif action_type == "number_captcha":
                import random

                num1 = random.randint(1, 20)
                num2 = random.randint(1, 20)
                modal = NumberCaptchaModal(num1, num2, btn)
                await interaction.response.send_modal(modal)
                return

            elif action_type == "dropdown":
                await self.show_dropdown(interaction, action_value, session)
                return

            elif action_type == "dm":
                dm_text = btn.dm_text or "Вы успешно прошли верификацию!"
                try:
                    await interaction.user.send(dm_text)
                except:
                    pass
                await interaction.response.send_message(
                    "✅ Сообщение отправлено в ЛС!", ephemeral=True
                )

            elif action_type == "welcome":
                welcome_text = (
                    btn.dm_text
                    or f"Добро пожаловать на сервер {interaction.guild.name}!"
                )
                try:
                    await interaction.user.send(welcome_text)
                except:
                    pass

                if action_value:
                    role = discord.utils.get(
                        interaction.guild.roles, id=int(action_value)
                    )
                    if role and role not in interaction.user.roles:
                        await interaction.user.add_roles(role)

                await interaction.response.send_message(
                    "👋 Добро пожаловать!", ephemeral=True
                )

            elif action_type == "redirect":
                channel_id = (
                    int(action_value)
                    if action_value
                    else config.welcome_channel_id
                    if config
                    else None
                )
                if channel_id:
                    channel = interaction.guild.get_channel(channel_id)
                    if channel:
                        msg = (
                            btn.message_text
                            or f"Пользователь {interaction.user.mention} перенаправлен с верификации."
                        )
                        await channel.send(msg)
                await interaction.response.send_message(
                    f"📍 Перенаправление в <#{channel_id or 'канал'}>...",
                    ephemeral=True,
                )

            elif action_type == "confirm":
                confirm_view = ConfirmActionView(btn, interaction.user.id)
                await interaction.response.send_message(
                    btn.message_text or "Подтвердите действие:",
                    view=confirm_view,
                    ephemeral=True,
                )
                return

            elif action_type == "timeout":
                duration = int(action_value) if action_value else 60
                await interaction.user.timeout(
                    datetime.timedelta(seconds=duration), reason="Верификация"
                )
                await interaction.response.send_message(
                    f"⏱️ Таймаут на {duration} сек.", ephemeral=True
                )

            elif action_type == "kick":
                if (
                    interaction.user.guild_permissions.kick_members
                    or interaction.guild.owner_id == interaction.user.id
                ):
                    await interaction.user.kick(reason="Нажата кнопка кика")
                    await interaction.response.send_message(
                        "👢 Пользователь кикнут.", ephemeral=True
                    )
                else:
                    await interaction.response.send_message(
                        "❌ Недостаточно прав!", ephemeral=True
                    )

            elif action_type == "ban":
                if (
                    interaction.user.guild_permissions.ban_members
                    or interaction.guild.owner_id == interaction.user.id
                ):
                    await interaction.user.ban(reason="Нажата кнопка бана")
                    await interaction.response.send_message(
                        "🔨 Пользователь забанен.", ephemeral=True
                    )
                else:
                    await interaction.response.send_message(
                        "❌ Недостаточно прав!", ephemeral=True
                    )

            elif action_type == "link":
                await interaction.response.send_message(
                    "🔗 Используйте кнопку ниже для перехода!", ephemeral=True
                )

            elif action_type == "nothing":
                msg = btn.message_text or "✅ Кнопка нажата!"
                await interaction.response.send_message(msg, ephemeral=True)

            else:
                await interaction.response.send_message(
                    "✅ Действие выполнено!", ephemeral=True
                )

        except Exception as e:
            await interaction.response.send_message(
                f"❌ Ошибка: {str(e)}", ephemeral=True
            )
        finally:
            session.close()

    async def give_role(
        self, interaction: discord.Interaction, role_id: str, session: SessionLocal
    ):
        if not role_id:
            await interaction.response.send_message(
                "❌ Роль не настроена!", ephemeral=True
            )
            return

        role = discord.utils.get(interaction.guild.roles, id=int(role_id))
        if not role:
            await interaction.response.send_message(
                "❌ Роль не найдена!", ephemeral=True
            )
            return

        if role in interaction.user.roles:
            await interaction.response.send_message(
                f"ℹ️ У вас уже есть роль {role.mention}!", ephemeral=True
            )
            return

        try:
            await interaction.user.add_roles(role)

            config = (
                session.query(VerificationConfig)
                .filter_by(guild_id=interaction.guild_id)
                .first()
            )
            if config and config.welcome_channel_id:
                welcome_channel = interaction.guild.get_channel(
                    config.welcome_channel_id
                )
                if welcome_channel:
                    color = config.embed_color if config.embed_color else 0x3498DB
                    embed = discord.Embed(
                        description=f"✅ {interaction.user.mention} получил роль {role.mention}",
                        color=color,
                    )
                    embed.set_author(
                        name=str(interaction.user),
                        icon_url=interaction.user.display_avatar.url,
                    )
                    await welcome_channel.send(embed=embed)

            await interaction.response.send_message(
                f"✅ Роль {role.mention} выдана!", ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Бот не может выдать эту роль!", ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Ошибка: {str(e)}", ephemeral=True
            )

    async def show_dropdown(
        self, interaction: discord.Interaction, role_ids: str, session: SessionLocal
    ):
        if not role_ids:
            await interaction.response.send_message(
                "❌ Роли не настроены!", ephemeral=True
            )
            return

        options = []
        for rid in role_ids.split(","):
            rid = rid.strip()
            if rid:
                try:
                    role = discord.utils.get(interaction.guild.roles, id=int(rid))
                    if role:
                        emoji = getattr(role, "emoji", None) or ""
                        options.append(
                            discord.SelectOption(
                                label=role.name, value=rid, emoji=str(emoji)
                            )
                        )
                except:
                    pass

        if not options:
            await interaction.response.send_message(
                "❌ Роли не найдены!", ephemeral=True
            )
            return

        if len(options) == 1:
            await self.give_role(interaction, options[0].value, session)
            return

        dropdown = VerificationSelect(
            options,
            self.button_config.config_id,
            f"verify_dropdown_{self.button_config.button_id}",
        )
        view = ui.View()
        view.add_item(dropdown)
        await interaction.response.send_message(
            "Выберите роль:", view=view, ephemeral=True
        )

    async def execute_verification(self, interaction: discord.Interaction):
        btn = self.button_config
        session = SessionLocal()

        try:
            role = (
                discord.utils.get(interaction.guild.roles, id=int(btn.action_value))
                if btn.action_value
                else None
            )
            if role and role not in interaction.user.roles:
                await interaction.user.add_roles(role)

            await interaction.response.send_message(
                "✅ Верификация пройдена!", ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"✅ Действие выполнено!", ephemeral=True
            )
        finally:
            session.close()


class ConfirmActionView(ui.View):
    def __init__(self, button_config: VerificationButton, user_id: int):
        super().__init__(timeout=60)
        self.button_config = button_config
        self.user_id = user_id

    @ui.button(label="✅ Подтвердить", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ Это не ваше подтверждение!", ephemeral=True
            )
            return

        btn = self.button_config
        action_value = btn.action_value

        if btn.action_type == "redirect":
            from database import GuildConfig

            config = (
                SessionLocal()
                .query(GuildConfig)
                .filter_by(guild_id=interaction.guild_id)
                .first()
            )
            channel_id = (
                int(action_value)
                if action_value
                else (config.welcome_channel_id if config else None)
            )
            if channel_id:
                channel = interaction.guild.get_channel(channel_id)
                if channel:
                    msg = (
                        btn.message_text
                        or f"Пользователь {interaction.user.mention} подтвердил действие."
                    )
                    await channel.send(msg)

        await interaction.message.delete()
        await interaction.response.send_message(
            "✅ Действие подтверждено!", ephemeral=True
        )

    @ui.button(label="❌ Отмена", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ Это не ваше подтверждение!", ephemeral=True
            )
            return
        await interaction.message.delete()
        await interaction.response.send_message("❌ Отменено.", ephemeral=True)


class VerificationView(ui.View):
    def __init__(self, guild_id: int, style: str = "buttons"):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self.style = style
        self.load_buttons()

    def load_buttons(self):
        session = SessionLocal()
        try:
            config = (
                session.query(VerificationConfig)
                .filter_by(guild_id=self.guild_id)
                .first()
            )
            if not config:
                return

            buttons = (
                session.query(VerificationButton)
                .filter_by(config_id=config.id)
                .order_by(VerificationButton.order)
                .all()
            )

            if self.style == "dropdown" and buttons:
                options = [
                    discord.SelectOption(
                        label=b.label, value=b.button_id, emoji=b.emoji
                    )
                    for b in buttons
                ]
                dropdown = VerificationSelect(
                    options, config.id, f"verify_main_dropdown_{config.id}"
                )
                self.add_item(dropdown)
            else:
                for btn in buttons:
                    self.add_item(CustomButton(btn))
        finally:
            session.close()


class PresetSelectView(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot

        options = [
            discord.SelectOption(
                label=preset["name"], value=key, description=preset["description"]
            )
            for key, preset in VERIFICATION_PRESETS.items()
        ]
        select = ui.Select(
            placeholder="Выберите пресет...",
            options=options,
            custom_id="verify_preset_select",
        )
        self.add_item(select)
        self.select_callback = self.make_callback(select)
        select.callback = self.select_callback

    def make_callback(self, select):
        async def callback(interaction: discord.Interaction):
            preset_key = select.values[0]
            preset = VERIFICATION_PRESETS.get(preset_key)

            if not preset:
                await interaction.response.send_message(
                    "❌ Пресет не найден!", ephemeral=True
                )
                return

            session = SessionLocal()
            try:
                config = (
                    session.query(VerificationConfig)
                    .filter_by(guild_id=interaction.guild_id)
                    .first()
                )
                if not config:
                    config = VerificationConfig(guild_id=interaction.guild_id)
                    session.add(config)

                config.title = preset.get("title", "🔐 Верификация")
                config.description = preset.get(
                    "description_text", "Нажмите кнопку для верификации."
                )
                config.embed_color = 0x3498DB
                config.style = "buttons"
                config.enabled = True
                session.commit()

                for old_btn in (
                    session.query(VerificationButton)
                    .filter_by(config_id=config.id)
                    .all()
                ):
                    session.delete(old_btn)
                session.commit()

                for i, btn_data in enumerate(preset.get("buttons", [])):
                    btn = VerificationButton(
                        config_id=config.id,
                        button_id=str(uuid.uuid4())[:8],
                        label=btn_data.get("label", "Кнопка"),
                        emoji=btn_data.get("emoji"),
                        style=btn_data.get("style", "primary"),
                        action_type=btn_data.get("action_type", "role"),
                        action_value=btn_data.get("action_value"),
                        order=i,
                    )
                    session.add(btn)

                session.commit()

                embed = discord.Embed(
                    title=config.title,
                    description=config.description,
                    color=config.embed_color,
                )
                view = VerificationView(interaction.guild_id, config.style)
                await interaction.channel.send(embed=embed, view=view)

                await interaction.response.send_message(
                    f"✅ Пресет '{preset.get('name')}' применён!", ephemeral=True
                )
            finally:
                session.close()

        return callback


class VerifyMainMenuView(ui.View):
    def __init__(self, config: VerificationConfig, bot):
        super().__init__(timeout=300)
        self.config = config
        self.bot = bot

    @ui.button(
        label="📝 Основные настройки",
        style=discord.ButtonStyle.primary,
        custom_id="ver_main_settings",
        row=0,
    )
    async def main_settings(self, interaction: discord.Interaction, button: ui.Button):
        modal = VerifyMainSettingsModal(self.config)
        await interaction.response.send_modal(modal)

    @ui.button(
        label="🎨 Внешний вид",
        style=discord.ButtonStyle.secondary,
        custom_id="ver_appearance",
        row=0,
    )
    async def appearance(self, interaction: discord.Interaction, button: ui.Button):
        modal = VerifyAppearanceModal(self.config)
        await interaction.response.send_modal(modal)

    @ui.button(
        label="🖼️ Баннер и миниатюра",
        style=discord.ButtonStyle.secondary,
        custom_id="ver_images",
        row=0,
    )
    async def images(self, interaction: discord.Interaction, button: ui.Button):
        modal = VerifyImagesModal(self.config)
        await interaction.response.send_modal(modal)

    @ui.button(
        label="🛠️ Добавить кнопку",
        style=discord.ButtonStyle.success,
        custom_id="ver_add_btn",
        row=1,
    )
    async def add_button(self, interaction: discord.Interaction, button: ui.Button):
        modal = AddButtonModal(self.config)
        await interaction.response.send_modal(modal)

    @ui.button(
        label="📋 Список кнопок",
        style=discord.ButtonStyle.secondary,
        custom_id="ver_buttons_list",
        row=1,
    )
    async def buttons_list(self, interaction: discord.Interaction, button: ui.Button):
        embed = await self.get_buttons_embed(interaction)
        view = VerifyButtonsListView(self.config, self.bot)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @ui.button(
        label="📦 Готовые пресеты",
        style=discord.ButtonStyle.primary,
        custom_id="ver_presets",
        row=1,
    )
    async def presets(self, interaction: discord.Interaction, button: ui.Button):
        embed = self.get_presets_embed()
        view = PresetSelectView(self.bot)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @ui.button(
        label="🔄 Обновить",
        style=discord.ButtonStyle.primary,
        custom_id="ver_refresh",
        row=2,
    )
    async def refresh(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer(ephemeral=True)
        await self.refresh_message(interaction)
        await interaction.followup.send("✅ Сообщение обновлено!", ephemeral=True)

    @ui.button(
        label="👁️ Предпросмотр",
        style=discord.ButtonStyle.secondary,
        custom_id="ver_preview",
        row=2,
    )
    async def preview(self, interaction: discord.Interaction, button: ui.Button):
        embed = self.create_embed(self.config)
        view = VerificationView(interaction.guild_id, self.config.style or "buttons")
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @ui.button(
        label="🗑️ Удалить",
        style=discord.ButtonStyle.danger,
        custom_id="ver_delete",
        row=3,
    )
    async def delete(self, interaction: discord.Interaction, button: ui.Button):
        confirm_view = ConfirmDeleteView(self.config)
        await interaction.response.send_message(
            "⚠️ Удалить верификацию?", view=confirm_view, ephemeral=True
        )

    async def refresh_message(self, interaction: discord.Interaction):
        session = SessionLocal()
        try:
            config = (
                session.query(VerificationConfig)
                .filter_by(guild_id=interaction.guild_id)
                .first()
            )
            if not config or not config.channel_id:
                return

            channel = self.bot.get_channel(config.channel_id)
            if channel and config.message_id:
                try:
                    message = await channel.fetch_message(config.message_id)
                    embed = self.create_embed(config)
                    view = VerificationView(
                        interaction.guild_id, config.style or "buttons"
                    )
                    await message.edit(embed=embed, view=view)
                except:
                    pass
        finally:
            session.close()

    async def get_buttons_embed(
        self, interaction: discord.Interaction
    ) -> discord.Embed:
        session = SessionLocal()
        try:
            buttons = (
                session.query(VerificationButton)
                .filter_by(config_id=self.config.id)
                .order_by(VerificationButton.order)
                .all()
            )
            color = self.config.embed_color or 0x3498DB
            embed = discord.Embed(
                title="🔘 Кнопки верификации", color=discord.Color(color)
            )

            if not buttons:
                embed.description = "Кнопок пока нет."
            else:
                for i, btn in enumerate(buttons, 1):
                    style_name = BUTTON_STYLE_NAMES.get(btn.style, btn.style)
                    action_name = ACTION_TYPES.get(btn.action_type, btn.action_type)
                    role_info = ""
                    if (
                        btn.action_type in ["role", "roles", "removerole", "togglerole"]
                        and btn.action_value
                    ):
                        try:
                            role = interaction.guild.get_role(
                                int(btn.action_value.split(",")[0].strip())
                            )
                            if role:
                                role_info = f"\n**Роль:** {role.mention}"
                        except:
                            pass
                    embed.add_field(
                        name=f"{i}. {btn.emoji or ''} {btn.label}".strip(),
                        value=f"**ID:** `{btn.button_id}`\n**Стиль:** {style_name}\n**Действие:** {action_name}{role_info}",
                        inline=False,
                    )
            return embed
        finally:
            session.close()

    def create_embed(self, config: VerificationConfig) -> discord.Embed:
        color = config.embed_color or 0x3498DB
        embed = discord.Embed(
            title=config.title or "🔐 Верификация",
            description=config.description or "Нажмите кнопку для верификации.",
            color=discord.Color(color),
        )
        if config.footer_text:
            embed.set_footer(text=config.footer_text)
        if config.thumbnail_url:
            embed.set_thumbnail(url=config.thumbnail_url)
        if config.banner_url:
            embed.set_image(url=config.banner_url)
        return embed

    def get_presets_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title="📦 Готовые пресеты верификации",
            description="Выберите пресет для быстрой настройки:",
            color=0x3498DB,
        )
        for key, preset in VERIFICATION_PRESETS.items():
            embed.add_field(
                name=preset["name"], value=f"_{preset['description']}_", inline=False
            )
        return embed


class VerifyButtonsListView(ui.View):
    def __init__(self, config: VerificationConfig, bot):
        super().__init__(timeout=300)
        self.config = config
        self.bot = bot

        session = SessionLocal()
        try:
            buttons = (
                session.query(VerificationButton)
                .filter_by(config_id=config.id)
                .order_by(VerificationButton.order)
                .all()
            )
        finally:
            session.close()

        if buttons:
            options = [
                discord.SelectOption(
                    label=btn.label, value=btn.button_id, emoji=btn.emoji
                )
                for btn in buttons
            ]

            class DynamicSelect(ui.Select):
                def __init__(self):
                    super().__init__(
                        placeholder="Выберите кнопку...",
                        options=options,
                        custom_id="ver_btn_select",
                    )

                async def callback(self, interaction: discord.Interaction):
                    session = SessionLocal()
                    try:
                        btn = (
                            session.query(VerificationButton)
                            .filter_by(config_id=config.id, button_id=self.values[0])
                            .first()
                        )
                        if btn:
                            modal = EditButtonModal(config, btn)
                            await interaction.response.send_modal(modal)
                    finally:
                        session.close()

            self.add_item(DynamicSelect())

    @ui.button(
        label="➕ Добавить",
        style=discord.ButtonStyle.success,
        custom_id="ver_add_btn_list",
    )
    async def add_button(self, interaction: discord.Interaction, button: ui.Button):
        modal = AddButtonModal(self.config)
        await interaction.response.send_modal(modal)


class ConfirmDeleteView(ui.View):
    def __init__(self, config: VerificationConfig):
        super().__init__(timeout=60)
        self.config = config

    @ui.button(label="✅ Удалить", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: ui.Button):
        session = SessionLocal()
        try:
            buttons = (
                session.query(VerificationButton)
                .filter_by(config_id=self.config.id)
                .all()
            )
            for btn in buttons:
                session.delete(btn)
            session.delete(self.config)
            session.commit()
            await interaction.response.send_message(
                "✅ Верификация удалена!", ephemeral=True
            )
        finally:
            session.close()

    @ui.button(label="❌ Отмена", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message("Отменено.", ephemeral=True)


class VerifyMainSettingsModal(ui.Modal, title="📝 Основные настройки"):
    title_input = ui.TextInput(
        label="Заголовок",
        placeholder="🔐 Верификация",
        default="🔐 Верификация",
        required=True,
        max_length=200,
        style=discord.TextStyle.short,
    )
    desc_input = ui.TextInput(
        label="Описание",
        placeholder="Текст приветствия...",
        default="Добро пожаловать!",
        required=True,
        max_length=1000,
        style=discord.TextStyle.paragraph,
    )
    footer_input = ui.TextInput(
        label="Footer",
        placeholder="Текст внизу",
        required=False,
        max_length=200,
        style=discord.TextStyle.short,
    )
    channel_input = ui.TextInput(
        label="ID канала",
        placeholder="123456789",
        required=False,
        max_length=20,
        style=discord.TextStyle.short,
    )
    style_input = ui.TextInput(
        label="Стиль (buttons/dropdown)",
        placeholder="buttons",
        default="buttons",
        required=True,
        max_length=20,
        style=discord.TextStyle.short,
    )

    def __init__(self, config: VerificationConfig):
        super().__init__(title="📝 Основные настройки")
        self.config = config
        self.title_input.default = config.title or "🔐 Верификация"
        self.desc_input.default = config.description or "Добро пожаловать!"
        self.footer_input.default = config.footer_text or ""
        self.channel_input.default = str(config.channel_id) if config.channel_id else ""
        self.style_input.default = config.style or "buttons"

    async def on_submit(self, interaction: discord.Interaction):
        session = SessionLocal()
        try:
            config = (
                session.query(VerificationConfig)
                .filter_by(guild_id=interaction.guild_id)
                .first()
            )
            if not config:
                config = VerificationConfig(guild_id=interaction.guild_id)
                session.add(config)

            config.title = self.title_input.value
            config.description = self.desc_input.value
            config.footer_text = self.footer_input.value or None
            config.style = self.style_input.value.lower()
            if self.channel_input.value:
                try:
                    config.channel_id = int(self.channel_input.value)
                except:
                    pass
            session.commit()
            await interaction.response.send_message("✅ Сохранено!", ephemeral=True)
        finally:
            session.close()


class VerifyAppearanceModal(ui.Modal, title="🎨 Внешний вид"):
    color_input = ui.TextInput(
        label="Цвет (HEX)",
        placeholder="3498db",
        required=True,
        max_length=6,
        style=discord.TextStyle.short,
    )
    enabled_input = ui.TextInput(
        label="Включить (true/false)",
        placeholder="true",
        default="true",
        required=True,
        max_length=5,
        style=discord.TextStyle.short,
    )

    def __init__(self, config: VerificationConfig):
        super().__init__(title="🎨 Внешний вид")
        self.config = config
        self.color_input.default = hex(config.embed_color or 0x3498DB)[2:]
        self.enabled_input.default = "true" if config.enabled else "false"

    async def on_submit(self, interaction: discord.Interaction):
        session = SessionLocal()
        try:
            config = (
                session.query(VerificationConfig)
                .filter_by(guild_id=interaction.guild_id)
                .first()
            )
            if not config:
                await interaction.response.send_message(
                    "❌ Не найдено!", ephemeral=True
                )
                return
            try:
                config.embed_color = int(self.color_input.value.replace("#", ""), 16)
            except:
                await interaction.response.send_message(
                    "❌ Неверный HEX!", ephemeral=True
                )
                return
            config.enabled = self.enabled_input.value.lower() == "true"
            session.commit()
            await interaction.response.send_message("✅ Сохранено!", ephemeral=True)
        finally:
            session.close()


class VerifyImagesModal(ui.Modal, title="🖼️ Изображения"):
    banner_input = ui.TextInput(
        label="URL баннера",
        placeholder="https://...",
        required=False,
        max_length=500,
        style=discord.TextStyle.short,
    )
    thumbnail_input = ui.TextInput(
        label="URL миниатюры",
        placeholder="https://...",
        required=False,
        max_length=500,
        style=discord.TextStyle.short,
    )

    def __init__(self, config: VerificationConfig):
        super().__init__(title="🖼️ Изображения")
        self.config = config
        self.banner_input.default = config.banner_url or ""
        self.thumbnail_input.default = config.thumbnail_url or ""

    async def on_submit(self, interaction: discord.Interaction):
        session = SessionLocal()
        try:
            config = (
                session.query(VerificationConfig)
                .filter_by(guild_id=interaction.guild_id)
                .first()
            )
            if not config:
                await interaction.response.send_message(
                    "❌ Не найдено!", ephemeral=True
                )
                return
            config.banner_url = self.banner_input.value or None
            config.thumbnail_url = self.thumbnail_input.value or None
            session.commit()
            await interaction.response.send_message("✅ Сохранено!", ephemeral=True)
        finally:
            session.close()


class AddButtonModal(ui.Modal, title="➕ Добавить кнопку"):
    label_input = ui.TextInput(
        label="Название",
        placeholder="✅ Верифицироваться",
        required=True,
        max_length=100,
        style=discord.TextStyle.short,
    )
    emoji_input = ui.TextInput(
        label="Эмодзи",
        placeholder="✅",
        required=False,
        max_length=100,
        style=discord.TextStyle.short,
    )
    style_input = ui.TextInput(
        label="Стиль (primary/success/danger/secondary)",
        placeholder="primary",
        default="primary",
        required=True,
        max_length=20,
        style=discord.TextStyle.short,
    )
    action_type_input = ui.TextInput(
        label="Тип (role/dm/captcha/togglerole/welcome)",
        placeholder="role",
        default="role",
        required=True,
        max_length=30,
        style=discord.TextStyle.short,
    )
    action_value_input = ui.TextInput(
        label="ID роли / текст",
        placeholder="123456789 или текст",
        required=False,
        max_length=200,
        style=discord.TextStyle.short,
    )

    def __init__(self, config: VerificationConfig):
        super().__init__(title="➕ Добавить кнопку")
        self.config = config

    async def on_submit(self, interaction: discord.Interaction):
        session = SessionLocal()
        try:
            config = (
                session.query(VerificationConfig)
                .filter_by(guild_id=interaction.guild_id)
                .first()
            )
            if not config:
                await interaction.response.send_message(
                    "❌ Верификация не найдена!", ephemeral=True
                )
                return

            btn = VerificationButton(
                config_id=config.id,
                button_id=str(uuid.uuid4())[:8],
                label=self.label_input.value,
                emoji=self.emoji_input.value or None,
                style=self.style_input.value.lower(),
                action_type=self.action_type_input.value.lower(),
                action_value=self.action_value_input.value or None,
                dm_text=self.action_value_input.value
                if self.action_type_input.value.lower() == "dm"
                else None,
                order=0,
            )
            session.add(btn)
            session.commit()
            await interaction.response.send_message(
                f'✅ Кнопка "{btn.label}" добавлена!', ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(f"❌ Ошибка: {e}", ephemeral=True)
        finally:
            session.close()


class EditButtonModal(ui.Modal, title="✏️ Редактировать"):
    label_input = ui.TextInput(
        label="Название",
        placeholder="✅ Верифицироваться",
        required=True,
        max_length=100,
        style=discord.TextStyle.short,
    )
    emoji_input = ui.TextInput(
        label="Эмодзи",
        placeholder="✅",
        required=False,
        max_length=100,
        style=discord.TextStyle.short,
    )
    style_input = ui.TextInput(
        label="Стиль (primary/success/danger/secondary)",
        placeholder="primary",
        required=True,
        max_length=20,
        style=discord.TextStyle.short,
    )
    action_type_input = ui.TextInput(
        label="Тип (role/dm/captcha/togglerole/welcome)",
        placeholder="role",
        required=True,
        max_length=30,
        style=discord.TextStyle.short,
    )
    action_value_input = ui.TextInput(
        label="ID роли / текст",
        placeholder="123456789 или текст",
        required=False,
        max_length=200,
        style=discord.TextStyle.short,
    )

    def __init__(self, config: VerificationConfig, button: VerificationButton):
        super().__init__(title=f"✏️ {button.label[:20]}")
        self.config = config
        self.button_id = button.button_id
        self.label_input.default = button.label
        self.emoji_input.default = button.emoji or ""
        self.style_input.default = button.style
        self.action_type_input.default = button.action_type
        self.action_value_input.default = button.action_value or button.dm_text or ""

    async def on_submit(self, interaction: discord.Interaction):
        session = SessionLocal()
        try:
            btn = (
                session.query(VerificationButton)
                .filter_by(config_id=self.config.id, button_id=self.button_id)
                .first()
            )
            if not btn:
                await interaction.response.send_message(
                    "❌ Кнопка не найдена!", ephemeral=True
                )
                return

            btn.label = self.label_input.value
            btn.emoji = self.emoji_input.value or None
            btn.style = self.style_input.value.lower()
            btn.action_type = self.action_type_input.value.lower()
            btn.action_value = self.action_value_input.value or None
            if btn.action_type == "dm":
                btn.dm_text = self.action_value_input.value
            session.commit()
            await interaction.response.send_message("✅ Обновлено!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Ошибка: {e}", ephemeral=True)
        finally:
            session.close()


class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_msg(self, guild_id: int, key: str, **kwargs) -> str:
        from main import get_msg as main_get_msg

        return main_get_msg(guild_id, key, **kwargs)

    def get_config(self, guild_id: int) -> Optional[VerificationConfig]:
        session = SessionLocal()
        try:
            return (
                session.query(VerificationConfig).filter_by(guild_id=guild_id).first()
            )
        finally:
            session.close()

    def create_embed(self, config: VerificationConfig) -> discord.Embed:
        color = config.embed_color or 0x3498DB
        embed = discord.Embed(
            title=config.title or "🔐 Верификация",
            description=config.description or "Нажмите кнопку для верификации.",
            color=discord.Color(color),
        )
        if config.footer_text:
            embed.set_footer(text=config.footer_text)
        if config.thumbnail_url:
            embed.set_thumbnail(url=config.thumbnail_url)
        if config.banner_url:
            embed.set_image(url=config.banner_url)
        return embed

    @commands.Cog.listener()
    async def on_ready(self):
        session = SessionLocal()
        try:
            configs = session.query(VerificationConfig).filter_by(enabled=True).all()
            for config in configs:
                self.bot.add_view(
                    VerificationView(config.guild_id, config.style or "buttons")
                )
        finally:
            session.close()

    @app_commands.command(name="verify", description="Главное меню верификации")
    @app_commands.checks.has_permissions(administrator=True)
    async def verify_menu(self, interaction: discord.Interaction):
        if not interaction.guild:
            return

        session = SessionLocal()
        try:
            config = (
                session.query(VerificationConfig)
                .filter_by(guild_id=interaction.guild_id)
                .first()
            )

            if not config:
                config = VerificationConfig(
                    guild_id=interaction.guild_id,
                    title="🔐 Верификация",
                    description="Добро пожаловать! Нажмите кнопку ниже для верификации.",
                    embed_color=0x3498DB,
                    style="buttons",
                    enabled=False,
                )
                session.add(config)
                session.commit()

            color = config.embed_color or 0x3498DB
            embed = discord.Embed(
                title="🔐 Меню верификации",
                description="Выберите действие:",
                color=discord.Color(color),
            )

            status = "✅ Включена" if config.enabled else "❌ Выключена"
            channel = f"<#{config.channel_id}>" if config.channel_id else "Не указан"
            buttons_count = (
                session.query(VerificationButton).filter_by(config_id=config.id).count()
            )

            embed.add_field(
                name="📊 Статус",
                value=f"**Верификация:** {status}\n**Канал:** {channel}\n**Кнопок:** {buttons_count}",
                inline=False,
            )

            view = VerifyMainMenuView(config, self.bot)
            await interaction.response.send_message(
                embed=embed, view=view, ephemeral=True
            )
        finally:
            session.close()

    @app_commands.command(name="verify_setup", description="Быстрая настройка")
    @app_commands.checks.has_permissions(administrator=True)
    async def verify_setup(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        title: str = "🔐 Верификация",
        description: str = "Добро пожаловать!",
        embed_color: str = "3498db",
    ):
        if not interaction.guild:
            return

        session = SessionLocal()
        try:
            config = (
                session.query(VerificationConfig)
                .filter_by(guild_id=interaction.guild_id)
                .first()
            )
            if not config:
                config = VerificationConfig(guild_id=interaction.guild_id)
                session.add(config)

            try:
                color_int = int(embed_color.replace("#", ""), 16)
            except:
                color_int = 0x3498DB

            config.channel_id = channel.id
            config.title = title
            config.description = description
            config.embed_color = color_int
            config.enabled = True

            session.commit()

            embed = self.create_embed(config)
            view = VerificationView(interaction.guild_id, "buttons")
            message = await channel.send(embed=embed, view=view)

            config.message_id = message.id
            session.commit()

            await interaction.response.send_message(
                f"✅ Готово в {channel.mention}!\n💡 Используйте `/verify` для настроек.",
                ephemeral=True,
            )
        finally:
            session.close()

    @app_commands.command(name="verify_presets", description="Готовые пресеты")
    @app_commands.checks.has_permissions(administrator=True)
    async def verify_presets(self, interaction: discord.Interaction):
        if not interaction.guild:
            return

        embed = discord.Embed(
            title="📦 Готовые пресеты", description="Выберите пресет:", color=0x3498DB
        )
        for key, preset in VERIFICATION_PRESETS.items():
            embed.add_field(
                name=preset["name"], value=preset["description"], inline=False
            )

        view = PresetSelectView(self.bot)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="verify_preview", description="Предпросмотр")
    @app_commands.checks.has_permissions(administrator=True)
    async def verify_preview(self, interaction: discord.Interaction):
        if not interaction.guild:
            return

        config = self.get_config(interaction.guild_id)
        if not config:
            await interaction.response.send_message(
                "❌ Верификация не настроена!", ephemeral=True
            )
            return

        embed = self.create_embed(config)
        view = VerificationView(interaction.guild_id, config.style or "buttons")
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="verify_actions", description="Типы действий кнопок")
    @app_commands.checks.has_permissions(administrator=True)
    async def verify_actions(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🔧 Типы действий", color=0x3498DB)
        for action, desc in ACTION_TYPES.items():
            embed.add_field(name=f"`{action}`", value=desc, inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)
