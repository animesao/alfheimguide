import discord
import asyncio
from discord.ext import commands
from discord import app_commands, ui
from database import SessionLocal, GuildConfig, TicketCategory
from typing import Optional


class TicketColorModal(ui.Modal):
    def __init__(self, channel: discord.TextChannel, message_id: int, lang: str = "ru"):
        super().__init__(title="Изменить цвет тикета" if lang == "ru" else "Change ticket color")
        self.channel = channel
        self.message_id = message_id
        self.lang = lang
        self.color = ui.TextInput(
            label="Цвет (HEX код)" if lang == "ru" else "Color (HEX code)",
            placeholder="#FF5733" if lang == "en" else "Например: #FF5733 или FF5733",
            min_length=6, max_length=7, required=True
        )
        self.add_item(self.color)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            color_str = self.color.value.strip().replace('#', '')
            color_int = int(color_str, 16)

            message = await self.channel.fetch_message(self.message_id)
            if message.embeds:
                old_embed = message.embeds[0]
                new_embed = discord.Embed(
                    title=old_embed.title,
                    description=old_embed.description,
                    color=discord.Color(color_int)
                )
                if old_embed.footer:
                    new_embed.set_footer(text=old_embed.footer.text)
                if old_embed.image:
                    new_embed.set_image(url=old_embed.image.url)
                if old_embed.thumbnail:
                    new_embed.set_thumbnail(url=old_embed.thumbnail.url)
                for field in old_embed.fields:
                    new_embed.add_field(name=field.name, value=field.value, inline=field.inline)

                await message.edit(embed=new_embed)
                msg = f"✅ Цвет тикета изменён на `#{color_str.upper()}`" if self.lang == "ru" else f"✅ Ticket color changed to `#{color_str.upper()}`"
                await interaction.response.send_message(msg, ephemeral=True)
            else:
                msg = "Не удалось найти embed сообщение." if self.lang == "ru" else "Could not find embed message."
                await interaction.response.send_message(msg, ephemeral=True)
        except ValueError:
            msg = "Неверный HEX код. Используйте формат: FF5733" if self.lang == "ru" else "Invalid HEX code. Use format: FF5733"
            await interaction.response.send_message(msg, ephemeral=True)
        except Exception as e:
            msg = f"Ошибка: {str(e)}" if self.lang == "ru" else f"Error: {str(e)}"
            await interaction.response.send_message(msg, ephemeral=True)


class TicketControlView(ui.View):
    def __init__(self, message_id: int = None, lang: str = "ru"):
        super().__init__(timeout=None)
        self.message_id = message_id
        self.lang = lang
        # Localize button labels after super().__init__() creates them
        for child in self.children:
            if isinstance(child, ui.Button) and child.custom_id == "ticket_change_color":
                child.label = "🎨 Изменить цвет" if lang == "ru" else "🎨 Change color"
            elif isinstance(child, ui.Button) and child.custom_id == "close_ticket":
                child.label = "🔒 Закрыть тикет" if lang == "ru" else "🔒 Close ticket"

    @ui.button(label="🎨 Изменить цвет", style=discord.ButtonStyle.secondary, custom_id="ticket_change_color")
    async def change_color(self, interaction: discord.Interaction, button: ui.Button):
        if not interaction.user.guild_permissions.manage_channels:
            msg = "У вас нет прав для изменения цвета тикета." if self.lang == "ru" else "You don't have permission to change the ticket color."
            await interaction.response.send_message(msg, ephemeral=True)
            return

        async for msg in interaction.channel.history(limit=50):
            if msg.embeds and msg.author == interaction.guild.me:
                modal = TicketColorModal(interaction.channel, msg.id, self.lang)
                await interaction.response.send_modal(modal)
                return

        msg = "Не найдено сообщение с embed для изменения цвета." if self.lang == "ru" else "No embed message found to change color."
        await interaction.response.send_message(msg, ephemeral=True)

    @ui.button(label="🔒 Закрыть тикет", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: ui.Button):
        msg = "Тикет будет закрыт через 5 секунд..." if self.lang == "ru" else "Ticket will close in 5 seconds..."
        await interaction.response.send_message(msg)
        await asyncio.sleep(5)
        await interaction.channel.delete()


class TicketReasonModal(ui.Modal):
    def __init__(self, category_name: str, embed_color: int = 0x3498db, lang: str = "ru",
                 modal_title: str = None, modal_label: str = None, modal_placeholder: str = None):
        if not modal_title:
            modal_title = "Причина открытия тикета" if lang == "ru" else "Ticket opening reason"
        super().__init__(title=modal_title)
        self.category_name = category_name
        self.embed_color = embed_color
        self.lang = lang

        if not modal_label:
            modal_label = "Опишите вашу проблему" if lang == "ru" else "Describe your issue"
        if not modal_placeholder:
            modal_placeholder = "Например: Жалоба на игрока / Техническая ошибка" if lang == "ru" else "e.g. Player report / Technical issue"

        self.reason = ui.TextInput(
            label=modal_label,
            style=discord.TextStyle.paragraph,
            placeholder=modal_placeholder,
            required=True,
            min_length=10,
            max_length=500
        )
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        member = interaction.user
        cat_name = "Тикеты" if self.lang == "ru" else "Tickets"
        category = discord.utils.get(guild.categories, name=cat_name)
        if not category:
            category = await guild.create_category(cat_name)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True, embed_links=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        channel_name = f"ticket-{member.name}".lower()
        channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)
        embed = discord.Embed(
            title=f"{'Тикет' if self.lang == 'ru' else 'Ticket'}: {self.category_name}",
            description=f"**{'Пользователь' if self.lang == 'ru' else 'User'}:** {member.mention}\n**{'Причина' if self.lang == 'ru' else 'Reason'}:** {self.reason.value}",
            color=discord.Color(self.embed_color)
        )
        footer_text = "Используйте кнопки ниже для управления тикетом." if self.lang == "ru" else "Use buttons below to manage the ticket."
        embed.set_footer(text=footer_text)

        view = TicketControlView(lang=self.lang)
        msg = await channel.send(embed=embed, view=view)
        open_msg = f"Тикет открыт: {channel.mention}" if self.lang == "ru" else f"Ticket opened: {channel.mention}"
        await interaction.followup.send(open_msg, ephemeral=True)


class TicketDropdown(ui.Select):
    def __init__(self, categories: list, embed_color: int = 0x3498db, lang: str = "ru"):
        desc_tpl = "Открыть тикет в категории {cat}" if lang == "ru" else "Open ticket in category {cat}"
        options = [discord.SelectOption(label=cat, description=desc_tpl.format(cat=cat)) for cat in categories]
        placeholder_text = "Выберите категорию тикета..." if lang == "ru" else "Select a ticket category..."
        super().__init__(placeholder=placeholder_text, min_values=1, max_values=1, options=options, custom_id="persistent_ticket_select")
        self.embed_color = embed_color
        self.lang = lang

    async def callback(self, interaction: discord.Interaction):
        session = SessionLocal()
        try:
            category_config = session.query(TicketCategory).filter_by(
                guild_id=interaction.guild_id,
                name=self.values[0]
            ).first()

            if category_config:
                modal = TicketReasonModal(
                    self.values[0], self.embed_color, lang=self.lang,
                    modal_title=category_config.modal_title,
                    modal_label=category_config.modal_label,
                    modal_placeholder=category_config.modal_placeholder
                )
            else:
                modal = TicketReasonModal(self.values[0], self.embed_color, lang=self.lang)
        finally:
            session.close()

        await interaction.response.send_modal(modal)


class TicketButton(ui.Button):
    def __init__(self, label: str, embed_color: int = 0x3498db, lang: str = "ru"):
        super().__init__(label=label, style=discord.ButtonStyle.primary, custom_id=f"ticket_btn_{label}")
        self.embed_color = embed_color
        self.lang = lang

    async def callback(self, interaction: discord.Interaction):
        session = SessionLocal()
        try:
            category_config = session.query(TicketCategory).filter_by(
                guild_id=interaction.guild_id,
                name=self.label
            ).first()

            if category_config:
                modal = TicketReasonModal(
                    self.label, self.embed_color, lang=self.lang,
                    modal_title=category_config.modal_title,
                    modal_label=category_config.modal_label,
                    modal_placeholder=category_config.modal_placeholder
                )
            else:
                modal = TicketReasonModal(self.label, self.embed_color, lang=self.lang)
        finally:
            session.close()

        await interaction.response.send_modal(modal)


class TicketPersistentView(ui.View):
    def __init__(self, categories: list, mode: str = "dropdown", embed_color: int = 0x3498db, lang: str = "ru"):
        super().__init__(timeout=None)
        self.lang = lang
        if mode == "dropdown":
            self.add_item(TicketDropdown(categories, embed_color, lang))
        else:
            for cat in categories:
                self.add_item(TicketButton(cat, embed_color, lang))


_COLOR_CHOICES_RU = [
    app_commands.Choice(name="🔵 Синий", value="3498db"),
    app_commands.Choice(name="🟢 Зелёный", value="2ecc71"),
    app_commands.Choice(name="🔴 Красный", value="e74c3c"),
    app_commands.Choice(name="🟡 Жёлтый", value="f1c40f"),
    app_commands.Choice(name="🟣 Фиолетовый", value="9b59b6"),
    app_commands.Choice(name="🟠 Оранжевый", value="e67e22"),
    app_commands.Choice(name="⚪ Белый", value="ffffff"),
    app_commands.Choice(name="⬛ Чёрный", value="000000"),
    app_commands.Choice(name="🩵 Бирюзовый", value="1abc9c"),
    app_commands.Choice(name="🩷 Розовый", value="ff69b4"),
]
_COLOR_CHOICES_EN = [
    app_commands.Choice(name="🔵 Blue", value="3498db"),
    app_commands.Choice(name="🟢 Green", value="2ecc71"),
    app_commands.Choice(name="🔴 Red", value="e74c3c"),
    app_commands.Choice(name="🟡 Yellow", value="f1c40f"),
    app_commands.Choice(name="🟣 Purple", value="9b59b6"),
    app_commands.Choice(name="🟠 Orange", value="e67e22"),
    app_commands.Choice(name="⚪ White", value="ffffff"),
    app_commands.Choice(name="⬛ Black", value="000000"),
    app_commands.Choice(name="🩵 Cyan", value="1abc9c"),
    app_commands.Choice(name="🩷 Pink", value="ff69b4"),
]


class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ticket_setup", description="Set up ticket system")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.choices(style=[
        app_commands.Choice(name="Dropdown / Список", value="dropdown"),
        app_commands.Choice(name="Buttons / Кнопки", value="buttons")
    ])
    @app_commands.choices(color=_COLOR_CHOICES_RU + _COLOR_CHOICES_EN)
    async def ticket_setup(self, interaction: discord.Interaction,
                           title: str = None,
                           description: str = None,
                           categories: str = None,
                           image_url: Optional[str] = None,
                           style: app_commands.Choice[str] = None,
                           color: app_commands.Choice[str] = None,
                           custom_color: Optional[str] = None):
        session = SessionLocal()
        try:
            gc = session.query(GuildConfig).filter_by(guild_id=interaction.guild_id).first()
            lang = str(gc.language) if gc and gc.language else "ru"
        finally:
            session.close()

        is_ru = lang == "ru"
        if title is None:
            title = "Система тикетов" if is_ru else "Ticket System"
        if description is None:
            description = "Выберите категорию ниже, чтобы связаться с администрацией." if is_ru else "Select a category below to contact staff."
        if categories is None:
            categories = "Поддержка,Жалоба,Вопрос" if is_ru else "Support,Report,Question"

        cat_list = [c.strip() for c in categories.split(',')]
        mode = style.value if style else "dropdown"

        session = SessionLocal()
        try:
            for cat_name in cat_list:
                exists = session.query(TicketCategory).filter_by(guild_id=interaction.guild_id, name=cat_name).first()
                if not exists:
                    new_cat = TicketCategory(guild_id=interaction.guild_id, name=cat_name)
                    session.add(new_cat)
            session.commit()
        finally:
            session.close()

        if custom_color:
            try:
                embed_color = int(custom_color.replace('#', ''), 16)
            except ValueError:
                msg = "Неверный HEX код цвета. Используйте формат: FF5733" if is_ru else "Invalid HEX color code. Use format: FF5733"
                await interaction.response.send_message(msg, ephemeral=True)
                return
        elif color:
            embed_color = int(color.value, 16)
        else:
            embed_color = 0x2ecc71

        embed = discord.Embed(title=title, description=description, color=discord.Color(embed_color))
        if image_url:
            embed.set_image(url=image_url)
        view = TicketPersistentView(cat_list, mode, embed_color, lang)
        await interaction.channel.send(embed=embed, view=view)
        succ_msg = "✅ Сообщение для тикетов отправлено." if is_ru else "✅ Ticket message sent."
        await interaction.response.send_message(succ_msg, ephemeral=True)

    @app_commands.command(name="ticket_config_category", description="Configure ticket category modal")
    @app_commands.checks.has_permissions(administrator=True)
    async def ticket_config_category(self, interaction: discord.Interaction,
                                    category_name: str,
                                    modal_title: Optional[str] = None,
                                    modal_label: Optional[str] = None,
                                    modal_placeholder: Optional[str] = None):
        session = SessionLocal()
        try:
            gc = session.query(GuildConfig).filter_by(guild_id=interaction.guild_id).first()
            lang = str(gc.language) if gc and gc.language else "ru"
            cat = session.query(TicketCategory).filter_by(guild_id=interaction.guild_id, name=category_name).first()
            if not cat:
                cat = TicketCategory(guild_id=interaction.guild_id, name=category_name)
                session.add(cat)

            if modal_title: cat.modal_title = modal_title
            if modal_label: cat.modal_label = modal_label
            if modal_placeholder: cat.modal_placeholder = modal_placeholder

            session.commit()
        finally:
            session.close()
        msg = f"✅ Настройки для категории `{category_name}` обновлены." if lang == "ru" else f"✅ Settings for category `{category_name}` updated."
        await interaction.response.send_message(msg, ephemeral=True)

    @app_commands.command(name="ticket_color", description="Change current ticket color")
    async def ticket_color(self, interaction: discord.Interaction, color: str):
        session = SessionLocal()
        try:
            gc = session.query(GuildConfig).filter_by(guild_id=interaction.guild_id).first()
            lang = str(gc.language) if gc and gc.language else "ru"
        finally:
            session.close()
        is_ru = lang == "ru"

        if not interaction.channel.name.startswith("ticket-"):
            msg = "Эта команда работает только в каналах тикетов." if is_ru else "This command only works in ticket channels."
            await interaction.response.send_message(msg, ephemeral=True)
            return

        if not interaction.user.guild_permissions.manage_channels:
            msg = "У вас нет прав для изменения цвета тикета." if is_ru else "You don't have permission to change the ticket color."
            await interaction.response.send_message(msg, ephemeral=True)
            return

        try:
            color_str = color.strip().replace('#', '')
            color_int = int(color_str, 16)

            async for msg in interaction.channel.history(limit=50):
                if msg.embeds and msg.author == interaction.guild.me:
                    old_embed = msg.embeds[0]
                    new_embed = discord.Embed(
                        title=old_embed.title,
                        description=old_embed.description,
                        color=discord.Color(color_int)
                    )
                    if old_embed.footer:
                        new_embed.set_footer(text=old_embed.footer.text)

                    await msg.edit(embed=new_embed)
                    succ_msg = f"✅ Цвет тикета изменён на `#{color_str.upper()}`" if is_ru else f"✅ Ticket color changed to `#{color_str.upper()}`"
                    await interaction.response.send_message(succ_msg, ephemeral=True)
                    return

            not_found_msg = "Не найдено сообщение с embed." if is_ru else "No embed message found."
            await interaction.response.send_message(not_found_msg, ephemeral=True)
        except ValueError:
            err_msg = "Неверный HEX код. Используйте формат: FF5733 или #FF5733" if is_ru else "Invalid HEX code. Use format: FF5733 or #FF5733"
            await interaction.response.send_message(err_msg, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Tickets(bot))
