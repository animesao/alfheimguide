import discord
import asyncio
from discord.ext import commands
from discord import app_commands, ui
from database import SessionLocal, GuildConfig
from typing import Optional


class TicketColorModal(ui.Modal, title='Изменить цвет тикета'):
    color = ui.TextInput(
        label='Цвет (HEX код)',
        placeholder='Например: #FF5733 или FF5733',
        min_length=6,
        max_length=7,
        required=True
    )

    def __init__(self, channel: discord.TextChannel, message_id: int):
        super().__init__()
        self.channel = channel
        self.message_id = message_id

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
                await interaction.response.send_message(f"✅ Цвет тикета изменён на `#{color_str.upper()}`", ephemeral=True)
            else:
                await interaction.response.send_message("Не удалось найти embed сообщение.", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("Неверный HEX код. Используйте формат: FF5733", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Ошибка: {str(e)}", ephemeral=True)


class TicketControlView(ui.View):
    def __init__(self, message_id: int = None):
        super().__init__(timeout=None)
        self.message_id = message_id

    @ui.button(label="🎨 Изменить цвет", style=discord.ButtonStyle.secondary, custom_id="ticket_change_color")
    async def change_color(self, interaction: discord.Interaction, button: ui.Button):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("У вас нет прав для изменения цвета тикета.", ephemeral=True)
            return
        
        async for msg in interaction.channel.history(limit=50):
            if msg.embeds and msg.author == interaction.guild.me:
                modal = TicketColorModal(interaction.channel, msg.id)
                await interaction.response.send_modal(modal)
                return
        
        await interaction.response.send_message("Не найдено сообщение с embed для изменения цвета.", ephemeral=True)

    @ui.button(label="🔒 Закрыть тикет", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message("Тикет будет закрыт через 5 секунд...")
        await asyncio.sleep(5)
        await interaction.channel.delete()


class TicketReasonModal(ui.Modal, title='Причина открытия тикета'):
    reason = ui.TextInput(
        label='Опишите вашу проблему',
        style=discord.TextStyle.paragraph,
        placeholder='Например: Жалоба на игрока / Техническая ошибка',
        required=True,
        min_length=10,
        max_length=500
    )

    def __init__(self, category_name: str, embed_color: int = 0x3498db):
        super().__init__()
        self.category_name = category_name
        self.embed_color = embed_color

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        member = interaction.user
        category = discord.utils.get(guild.categories, name="Тикеты")
        if not category:
            category = await guild.create_category("Тикеты")
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True, embed_links=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        channel_name = f"ticket-{member.name}".lower()
        channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)
        embed = discord.Embed(
            title=f"Тикет: {self.category_name}",
            description=f"**Пользователь:** {member.mention}\n**Причина:** {self.reason.value}",
            color=discord.Color(self.embed_color)
        )
        embed.set_footer(text="Используйте кнопки ниже для управления тикетом.")
        
        view = TicketControlView()
        msg = await channel.send(embed=embed, view=view)
        await interaction.followup.send(f"Тикет открыт: {channel.mention}", ephemeral=True)


class TicketDropdown(ui.Select):
    def __init__(self, categories: list, embed_color: int = 0x3498db):
        options = [discord.SelectOption(label=cat, description=f"Открыть тикет в категории {cat}") for cat in categories]
        super().__init__(placeholder="Выберите категорию тикета...", min_values=1, max_values=1, options=options, custom_id="persistent_ticket_select")
        self.embed_color = embed_color

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(TicketReasonModal(self.values[0], self.embed_color))


class TicketButton(ui.Button):
    def __init__(self, label: str, embed_color: int = 0x3498db):
        super().__init__(label=label, style=discord.ButtonStyle.primary, custom_id=f"ticket_btn_{label}")
        self.embed_color = embed_color

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(TicketReasonModal(self.label, self.embed_color))


class TicketPersistentView(ui.View):
    def __init__(self, categories: list, mode: str = "dropdown", embed_color: int = 0x3498db):
        super().__init__(timeout=None)
        if mode == "dropdown":
            self.add_item(TicketDropdown(categories, embed_color))
        else:
            for cat in categories:
                self.add_item(TicketButton(cat, embed_color))


class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.add_view(TicketControlView())
        self.bot.add_view(TicketPersistentView([], "dropdown"))
        self.bot.add_view(TicketPersistentView([], "buttons"))

    @app_commands.command(name="ticket_setup", description="Настроить систему тикетов")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.choices(style=[
        app_commands.Choice(name="Список (Dropdown)", value="dropdown"),
        app_commands.Choice(name="Кнопки (Buttons)", value="buttons")
    ])
    @app_commands.choices(color=[
        app_commands.Choice(name="🔵 Синий", value="3498db"),
        app_commands.Choice(name="🟢 Зелёный", value="2ecc71"),
        app_commands.Choice(name="🔴 Красный", value="e74c3c"),
        app_commands.Choice(name="🟡 Жёлтый", value="f1c40f"),
        app_commands.Choice(name="🟣 Фиолетовый", value="9b59b6"),
        app_commands.Choice(name="🟠 Оранжевый", value="e67e22"),
        app_commands.Choice(name="⚪ Белый", value="ffffff"),
        app_commands.Choice(name="⬛ Чёрный", value="000000"),
        app_commands.Choice(name="🩵 Бирюзовый", value="1abc9c"),
        app_commands.Choice(name="🩷 Розовый", value="ff69b4")
    ])
    async def ticket_setup(self, interaction: discord.Interaction, 
                           title: str = "Система тикетов",
                           description: str = "Выберите категорию ниже, чтобы связаться с администрацией.",
                           categories: str = "Поддержка,Жалоба,Вопрос",
                           image_url: Optional[str] = None,
                           style: app_commands.Choice[str] = None,
                           color: app_commands.Choice[str] = None,
                           custom_color: Optional[str] = None):
        cat_list = [c.strip() for c in categories.split(',')]
        mode = style.value if style else "dropdown"
        
        if custom_color:
            try:
                embed_color = int(custom_color.replace('#', ''), 16)
            except ValueError:
                await interaction.response.send_message("Неверный HEX код цвета. Используйте формат: FF5733", ephemeral=True)
                return
        elif color:
            embed_color = int(color.value, 16)
        else:
            embed_color = 0x2ecc71
        
        embed = discord.Embed(title=title, description=description, color=discord.Color(embed_color))
        if image_url:
            embed.set_image(url=image_url)
        view = TicketPersistentView(cat_list, mode, embed_color)
        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message("✅ Сообщение для тикетов отправлено.", ephemeral=True)

    @app_commands.command(name="ticket_color", description="Изменить цвет текущего тикета")
    async def ticket_color(self, interaction: discord.Interaction, color: str):
        if not interaction.channel.name.startswith("ticket-"):
            await interaction.response.send_message("Эта команда работает только в каналах тикетов.", ephemeral=True)
            return
        
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("У вас нет прав для изменения цвета тикета.", ephemeral=True)
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
                    await interaction.response.send_message(f"✅ Цвет тикета изменён на `#{color_str.upper()}`", ephemeral=True)
                    return
            
            await interaction.response.send_message("Не найдено сообщение с embed.", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("Неверный HEX код. Используйте формат: FF5733 или #FF5733", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Tickets(bot))
