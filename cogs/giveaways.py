import discord
import asyncio
import random
import datetime
from discord.ext import commands, tasks
from discord import app_commands, ui
from database import SessionLocal, Giveaway, GiveawayEntry, LevelConfig, UserLevel
from typing import Optional


class GiveawayCreateModal(ui.Modal, title="🎁 Создание розыгрыша"):
    prize = ui.TextInput(label="Приз", placeholder="Nitro Classic", required=True, max_length=100)
    description = ui.TextInput(label="Описание", placeholder="Разыгрываем подписку!", required=False, max_length=500, style=discord.TextStyle.paragraph)
    winners = ui.TextInput(label="Кол-во победителей", placeholder="1", default="1", required=True, max_length=2)
    duration = ui.TextInput(label="Длительность (в минутах)", placeholder="1440", default="1440", required=True, max_length=5)
    required_role = ui.TextInput(label="ID требуемой роли (0 - нет)", placeholder="0", default="0", required=True, max_length=20)
    required_level = ui.TextInput(label="Мин. уровень (0 - нет)", placeholder="0", default="0", required=True, max_length=5)
    image_url = ui.TextInput(label="URL изображения", placeholder="https://...", required=False, max_length=300)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            winners = max(1, min(50, int(self.winners.value)))
            duration = max(1, int(self.duration.value))
            req_role = int(self.required_role.value) if self.required_role.value and self.required_role.value != "0" else None
            req_level = int(self.required_level.value) if self.required_level.value and self.required_level.value != "0" else 0
        except ValueError:
            await interaction.response.send_message("❌ Неверный формат чисел!", ephemeral=True)
            return

        ends_at = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + datetime.timedelta(minutes=duration)

        session = SessionLocal()
        try:
            giveaway = Giveaway(
                guild_id=interaction.guild_id,
                channel_id=interaction.channel_id,
                prize=self.prize.value,
                description=self.description.value or None,
                winners_count=winners,
                ends_at=ends_at,
                creator_id=interaction.user.id,
                required_role_id=req_role,
                required_level=req_level,
                image_url=self.image_url.value or None,
            )
            session.add(giveaway)
            session.commit()

            embed = discord.Embed(
                title=f"🎁 {self.prize.value}",
                description=self.description.value or "Нажмите кнопку, чтобы участвовать!",
                color=discord.Color.purple(),
                timestamp=ends_at,
            )
            embed.add_field(name="🏆 Победителей", value=str(winners), inline=True)
            embed.add_field(name="👤 Организатор", value=interaction.user.mention, inline=True)
            embed.add_field(name="⏰ Заканчивается", value=f"<t:{int(ends_at.timestamp())}:R>", inline=False)
            if req_role:
                embed.add_field(name="🔒 Требуется роль", value=f"<@&{req_role}>", inline=True)
            if req_level:
                embed.add_field(name="📊 Мин. уровень", value=str(req_level), inline=True)
            if self.image_url.value:
                embed.set_image(url=self.image_url.value)

            view = GiveawayJoinView(giveaway.id)
            msg = await interaction.channel.send(embed=embed, view=view)
            giveaway.message_id = msg.id
            session.commit()

            await interaction.response.send_message(f"✅ Розыгрыш **{self.prize.value}** создан!", ephemeral=True)
        finally:
            session.close()


class GiveawayJoinView(ui.View):
    def __init__(self, giveaway_id: int):
        super().__init__(timeout=None)
        self.giveaway_id = giveaway_id

    @ui.button(label="🎉 Участвовать", style=discord.ButtonStyle.success, emoji="🎉")
    async def join_button(self, interaction: discord.Interaction, button: ui.Button):
        session = SessionLocal()
        try:
            giveaway = session.query(Giveaway).filter_by(id=self.giveaway_id).first()
            if not giveaway or giveaway.ended:
                await interaction.response.send_message("❌ Розыгрыш уже завершён!", ephemeral=True)
                return

            if giveaway.required_role_id:
                role = interaction.guild.get_role(giveaway.required_role_id)
                if role and role not in interaction.user.roles:
                    await interaction.response.send_message(f"❌ Требуется роль <@&{giveaway.required_role_id}>!", ephemeral=True)
                    return

            if giveaway.required_level > 0:
                user_lvl = session.query(UserLevel).filter_by(
                    guild_id=interaction.guild_id, user_id=interaction.user.id
                ).first()
                if not user_lvl or (user_lvl.level or 1) < giveaway.required_level:
                    await interaction.response.send_message(f"❌ Требуется уровень **{giveaway.required_level}**!", ephemeral=True)
                    return

            existing = session.query(GiveawayEntry).filter_by(
                giveaway_id=self.giveaway_id, user_id=interaction.user.id
            ).first()
            if existing:
                await interaction.response.send_message("❌ Вы уже участвуете!", ephemeral=True)
                return

            entry = GiveawayEntry(giveaway_id=self.giveaway_id, user_id=interaction.user.id)
            session.add(entry)
            session.commit()

            total = session.query(GiveawayEntry).filter_by(giveaway_id=self.giveaway_id).count()
            await interaction.response.send_message(f"✅ Вы участвуете в розыгрыше **{giveaway.prize}**! (Участников: {total})", ephemeral=True)
        finally:
            session.close()


class Giveaways(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_giveaways.start()

    def cog_unload(self):
        self.check_giveaways.cancel()

    @tasks.loop(seconds=30)
    async def check_giveaways(self):
        session = SessionLocal()
        try:
            now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
            ended = session.query(Giveaway).filter(
                Giveaway.ends_at <= now, Giveaway.ended == False
            ).all()

            for giveaway in ended:
                await self.end_giveaway(giveaway, session)
        except:
            pass
        finally:
            session.close()

    async def end_giveaway(self, giveaway, session):
        entries = session.query(GiveawayEntry).filter_by(giveaway_id=giveaway.id).all()
        giveaway.ended = True
        session.commit()

        channel = self.bot.get_channel(giveaway.channel_id)
        if channel:
            try:
                msg = await channel.fetch_message(giveaway.message_id)
            except:
                msg = None

            if entries:
                winners = random.sample(entries, min(giveaway.winners_count, len(entries)))
                winner_mentions = []
                for w in winners:
                    winner_mentions.append(f"<@{w.user_id}>")

                embed = discord.Embed(
                    title=f"🎁 Розыгрыш завершён!",
                    description=f"**Приз:** {giveaway.prize}\n**Победители:** {', '.join(winner_mentions)}",
                    color=discord.Color.gold(),
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                )
                await channel.send(
                    f"🎉 Поздравляем! {', '.join(winner_mentions)} вы выиграли **{giveaway.prize}**!",
                    embed=embed,
                )

                if msg:
                    new_embed = msg.embeds[0]
                    new_embed.color = discord.Color.gold()
                    new_embed.add_field(name="🏆 Завершён", value=f"Победители: {', '.join(winner_mentions)}", inline=False)
                    old_view = GiveawayJoinView(giveaway.id)
                    old_view.join_button.disabled = True
                    await msg.edit(embed=new_embed, view=old_view)
            else:
                embed = discord.Embed(
                    title="😢 Розыгрыш завершён",
                    description=f"**Приз:** {giveaway.prize}\nНет участников",
                    color=discord.Color.red(),
                )
                await channel.send(embed=embed)

    @check_giveaways.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

    @app_commands.command(name="giveaway", description="Создать розыгрыш")
    @app_commands.checks.has_permissions(administrator=True)
    async def giveaway_create(self, interaction: discord.Interaction):
        await interaction.response.send_modal(GiveawayCreateModal())

    @app_commands.command(name="giveaway_reroll", description="Перерозыгрыш победителя")
    @app_commands.checks.has_permissions(administrator=True)
    async def giveaway_reroll(self, interaction: discord.Interaction, giveaway_id: int):
        session = SessionLocal()
        try:
            giveaway = session.query(Giveaway).filter_by(id=giveaway_id, guild_id=interaction.guild_id).first()
            if not giveaway:
                await interaction.response.send_message("❌ Розыгрыш не найден!", ephemeral=True)
                return

            entries = session.query(GiveawayEntry).filter_by(giveaway_id=giveaway.id).all()
            if not entries:
                await interaction.response.send_message("❌ Нет участников для перерозыгрыша!", ephemeral=True)
                return

            winner = random.choice(entries)
            await interaction.response.send_message(f"🎉 Новый победитель: <@{winner.user_id}> выигрывает **{giveaway.prize}**!")
        finally:
            session.close()

    @app_commands.command(name="giveaway_end", description="Принудительно завершить розыгрыш")
    @app_commands.checks.has_permissions(administrator=True)
    async def giveaway_end(self, interaction: discord.Interaction, giveaway_id: int):
        session = SessionLocal()
        try:
            giveaway = session.query(Giveaway).filter_by(id=giveaway_id, guild_id=interaction.guild_id).first()
            if not giveaway:
                await interaction.response.send_message("❌ Розыгрыш не найден!", ephemeral=True)
                return
            giveaway.ends_at = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
            session.commit()
            await self.end_giveaway(giveaway, session)
            await interaction.response.send_message("✅ Розыгрыш завершён!", ephemeral=True)
        finally:
            session.close()

    @app_commands.command(name="giveaway_list", description="Список активных розыгрышей")
    @app_commands.checks.has_permissions(administrator=True)
    async def giveaway_list(self, interaction: discord.Interaction):
        session = SessionLocal()
        try:
            giveaways = session.query(Giveaway).filter_by(guild_id=interaction.guild_id, ended=False).all()
            if not giveaways:
                await interaction.response.send_message("📭 Нет активных розыгрышей", ephemeral=True)
                return
            embed = discord.Embed(title="🎁 Активные розыгрыши", color=discord.Color.purple())
            for g in giveaways:
                count = session.query(GiveawayEntry).filter_by(giveaway_id=g.id).count()
                embed.add_field(
                    name=f"#{g.id} - {g.prize}",
                    value=f"Участников: {count}\nЗаканчивается: <t:{int(g.ends_at.timestamp())}:R>",
                    inline=False,
                )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        finally:
            session.close()


async def setup(bot):
    await bot.add_cog(Giveaways(bot))
