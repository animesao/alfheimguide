import discord
import asyncio
from discord.ext import commands
from discord import app_commands, ui
from database import SessionLocal, GuildConfig
from typing import Optional

class TicketReasonModal(ui.Modal, title='Причина открытия тикета'):
    reason = ui.TextInput(
        label='Опишите вашу проблему',
        style=discord.TextStyle.paragraph,
        placeholder='Например: Жалоба на игрока / Техническая ошибка',
        required=True,
        min_length=10,
        max_length=500
    )

    def __init__(self, category_name: str):
        super().__init__()
        self.category_name = category_name

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
            color=discord.Color.blue()
        )
        embed.set_footer(text="Нажмите на кнопку ниже, чтобы закрыть тикет.")
        view = ui.View(timeout=None)
        close_button = ui.Button(label="Закрыть тикет", style=discord.ButtonStyle.red, custom_id="close_ticket")
        async def close_callback(btn_interaction: discord.Interaction):
            await btn_interaction.response.send_message("Тикет будет закрыт через 5 секунд...")
            await asyncio.sleep(5)
            await btn_interaction.channel.delete()
        close_button.callback = close_callback
        view.add_item(close_button)
        await channel.send(embed=embed, view=view)
        await interaction.followup.send(f"Тикет открыт: {channel.mention}", ephemeral=True)

class TicketDropdown(ui.Select):
    def __init__(self, categories: list):
        options = [discord.SelectOption(label=cat, description=f"Открыть тикет в категории {cat}") for cat in categories]
        super().__init__(placeholder="Выберите категорию тикета...", min_values=1, max_values=1, options=options, custom_id="persistent_ticket_select")
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(TicketReasonModal(self.values[0]))

class TicketButton(ui.Button):
    def __init__(self, label: str):
        super().__init__(label=label, style=discord.ButtonStyle.primary, custom_id=f"ticket_btn_{label}")
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(TicketReasonModal(self.label))

class TicketPersistentView(ui.View):
    def __init__(self, categories: list, mode: str = "dropdown"):
        super().__init__(timeout=None)
        if mode == "dropdown":
            self.add_item(TicketDropdown(categories))
        else:
            for cat in categories:
                self.add_item(TicketButton(cat))

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.add_view(TicketPersistentView([], "dropdown"))
        self.bot.add_view(TicketPersistentView([], "buttons"))

    @app_commands.command(name="ticket_setup", description="Настроить систему тикетов")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.choices(style=[
        app_commands.Choice(name="Список (Dropdown)", value="dropdown"),
        app_commands.Choice(name="Кнопки (Buttons)", value="buttons")
    ])
    async def ticket_setup(self, interaction: discord.Interaction, 
                           title: str = "Система тикетов",
                           description: str = "Выберите категорию ниже, чтобы связаться с администрацией.",
                           categories: str = "Поддержка,Жалоба,Вопрос",
                           image_url: Optional[str] = None,
                           style: app_commands.Choice[str] = None):
        cat_list = [c.strip() for c in categories.split(',')]
        mode = style.value if style else "dropdown"
        embed = discord.Embed(title=title, description=description, color=discord.Color.green())
        if image_url:
            embed.set_image(url=image_url)
        view = TicketPersistentView(cat_list, mode)
        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message("✅ Сообщение для тикетов отправлено.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Tickets(bot))
