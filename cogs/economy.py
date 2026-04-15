import discord
from discord.ext import commands
from discord import app_commands
from database import SessionLocal, UserEconomy, ShopItem, Transaction, GuildConfig
import datetime
import random
from typing import Optional

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_msg(self, guild_id: int, key: str, **kwargs) -> str:
        from main import get_msg as main_get_msg
        return main_get_msg(guild_id, key, **kwargs)

    def get_user_economy(self, session, guild_id: int, user_id: int):
        economy = session.query(UserEconomy).filter_by(guild_id=guild_id, user_id=user_id).first()
        if not economy:
            economy = UserEconomy(guild_id=guild_id, user_id=user_id, balance=100, bank=0)
            session.add(economy)
            session.commit()
        return economy

    @app_commands.command(name="balance", description="Check your balance")
    async def balance(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        if not interaction.guild:
            return
        
        target = member or interaction.user
        session = SessionLocal()
        try:
            config = session.query(GuildConfig).filter_by(guild_id=interaction.guild.id).first()
            if not config or not config.economy_enabled:
                await interaction.response.send_message("💰 Economy system is disabled.", ephemeral=True)
                return

            economy = self.get_user_economy(session, interaction.guild.id, target.id)
            color_int = int(config.embed_color) if config and config.embed_color else 0x3498db
            
            embed = discord.Embed(
                title=f"💰 {target.display_name}'s Balance",
                color=discord.Color(color_int)
            )
            embed.add_field(name="💵 Wallet", value=f"{economy.balance:,} coins", inline=True)
            embed.add_field(name="🏦 Bank", value=f"{economy.bank:,} coins", inline=True)
            embed.add_field(name="💎 Total", value=f"{economy.balance + economy.bank:,} coins", inline=True)
            embed.set_thumbnail(url=target.display_avatar.url)
            
            await interaction.response.send_message(embed=embed)
        finally:
            session.close()

    @app_commands.command(name="daily", description="Claim your daily reward")
    async def daily(self, interaction: discord.Interaction):
        if not interaction.guild:
            return
        
        session = SessionLocal()
        try:
            economy = self.get_user_economy(session, interaction.guild.id, interaction.user.id)
            now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
            
            if economy.last_daily:
                time_since = now - economy.last_daily
                if time_since.total_seconds() < 86400:  # 24 hours
                    remaining = 86400 - time_since.total_seconds()
                    hours = int(remaining // 3600)
                    minutes = int((remaining % 3600) // 60)
                    await interaction.response.send_message(
                        f"⏰ You already claimed your daily! Come back in {hours}h {minutes}m",
                        ephemeral=True
                    )
                    return
            
            reward = random.randint(100, 500)
            economy.balance += reward
            economy.last_daily = now
            
            transaction = Transaction(
                guild_id=interaction.guild.id,
                user_id=interaction.user.id,
                amount=reward,
                transaction_type="daily",
                description="Daily reward"
            )
            session.add(transaction)
            session.commit()
            
            await interaction.response.send_message(f"🎁 You claimed your daily reward of **{reward:,} coins**!")
        finally:
            session.close()

    @app_commands.command(name="work", description="Work to earn coins")
    async def work(self, interaction: discord.Interaction):
        if not interaction.guild:
            return
        
        session = SessionLocal()
        try:
            economy = self.get_user_economy(session, interaction.guild.id, interaction.user.id)
            now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
            
            if economy.last_work:
                time_since = now - economy.last_work
                if time_since.total_seconds() < 3600:  # 1 hour
                    remaining = 3600 - time_since.total_seconds()
                    minutes = int(remaining // 60)
                    await interaction.response.send_message(
                        f"⏰ You're tired! Rest for {minutes} more minutes",
                        ephemeral=True
                    )
                    return
            
            jobs = [
                ("👨‍💻 coded a website", 50, 150),
                ("🎨 designed a logo", 40, 120),
                ("📝 wrote an article", 30, 100),
                ("🎵 composed music", 60, 180),
                ("🎮 tested a game", 45, 135),
                ("📦 delivered packages", 35, 105),
                ("🍕 made pizzas", 40, 110),
                ("🚗 drove a taxi", 50, 140),
            ]
            
            job, min_pay, max_pay = random.choice(jobs)
            reward = random.randint(min_pay, max_pay)
            economy.balance += reward
            economy.last_work = now
            
            transaction = Transaction(
                guild_id=interaction.guild.id,
                user_id=interaction.user.id,
                amount=reward,
                transaction_type="work",
                description=job
            )
            session.add(transaction)
            session.commit()
            
            await interaction.response.send_message(f"💼 You {job} and earned **{reward:,} coins**!")
        finally:
            session.close()

    @app_commands.command(name="transfer", description="Transfer coins to another user")
    async def transfer(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        if not interaction.guild:
            return
        
        if member.bot or member.id == interaction.user.id:
            await interaction.response.send_message("❌ Invalid transfer target", ephemeral=True)
            return
        
        if amount <= 0:
            await interaction.response.send_message("❌ Amount must be positive", ephemeral=True)
            return
        
        session = SessionLocal()
        try:
            sender = self.get_user_economy(session, interaction.guild.id, interaction.user.id)
            
            if sender.balance < amount:
                await interaction.response.send_message(
                    f"❌ Insufficient funds! You have {sender.balance:,} coins",
                    ephemeral=True
                )
                return
            
            receiver = self.get_user_economy(session, interaction.guild.id, member.id)
            
            sender.balance -= amount
            receiver.balance += amount
            
            # Log transactions
            session.add(Transaction(
                guild_id=interaction.guild.id,
                user_id=interaction.user.id,
                amount=-amount,
                transaction_type="transfer",
                description=f"Transfer to {member.name}"
            ))
            session.add(Transaction(
                guild_id=interaction.guild.id,
                user_id=member.id,
                amount=amount,
                transaction_type="transfer",
                description=f"Transfer from {interaction.user.name}"
            ))
            session.commit()
            
            await interaction.response.send_message(
                f"✅ Transferred **{amount:,} coins** to {member.mention}"
            )
        finally:
            session.close()

    @app_commands.command(name="deposit", description="Deposit coins to your bank")
    async def deposit(self, interaction: discord.Interaction, amount: str):
        if not interaction.guild:
            return
        
        session = SessionLocal()
        try:
            economy = self.get_user_economy(session, interaction.guild.id, interaction.user.id)
            
            if amount.lower() == "all":
                amount_int = economy.balance
            else:
                try:
                    amount_int = int(amount)
                except ValueError:
                    await interaction.response.send_message("❌ Invalid amount", ephemeral=True)
                    return
            
            if amount_int <= 0:
                await interaction.response.send_message("❌ Amount must be positive", ephemeral=True)
                return
            
            if economy.balance < amount_int:
                await interaction.response.send_message("❌ Insufficient funds", ephemeral=True)
                return
            
            economy.balance -= amount_int
            economy.bank += amount_int
            session.commit()
            
            await interaction.response.send_message(
                f"🏦 Deposited **{amount_int:,} coins** to your bank"
            )
        finally:
            session.close()

    @app_commands.command(name="withdraw", description="Withdraw coins from your bank")
    async def withdraw(self, interaction: discord.Interaction, amount: str):
        if not interaction.guild:
            return
        
        session = SessionLocal()
        try:
            economy = self.get_user_economy(session, interaction.guild.id, interaction.user.id)
            
            if amount.lower() == "all":
                amount_int = economy.bank
            else:
                try:
                    amount_int = int(amount)
                except ValueError:
                    await interaction.response.send_message("❌ Invalid amount", ephemeral=True)
                    return
            
            if amount_int <= 0:
                await interaction.response.send_message("❌ Amount must be positive", ephemeral=True)
                return
            
            if economy.bank < amount_int:
                await interaction.response.send_message("❌ Insufficient bank funds", ephemeral=True)
                return
            
            economy.bank -= amount_int
            economy.balance += amount_int
            session.commit()
            
            await interaction.response.send_message(
                f"💵 Withdrew **{amount_int:,} coins** from your bank"
            )
        finally:
            session.close()

    @app_commands.command(name="shop", description="View the server shop")
    async def shop(self, interaction: discord.Interaction):
        if not interaction.guild:
            return
        
        session = SessionLocal()
        try:
            config = session.query(GuildConfig).filter_by(guild_id=interaction.guild.id).first()
            items = session.query(ShopItem).filter_by(guild_id=interaction.guild.id).all()
            
            color_int = int(config.embed_color) if config and config.embed_color else 0x3498db
            embed = discord.Embed(
                title="🛒 Server Shop",
                description="Use `/buy <item_id>` to purchase items",
                color=discord.Color(color_int)
            )
            
            if not items:
                embed.description = "The shop is empty! Admins can add items with `/shop_add`"
            else:
                for item in items:
                    stock_text = f"Stock: {item.stock}" if item.stock != -1 else "Unlimited"
                    embed.add_field(
                        name=f"{item.name} (ID: {item.id})",
                        value=f"{item.description or 'No description'}\n💰 Price: {item.price:,} coins\n📦 {stock_text}",
                        inline=False
                    )
            
            await interaction.response.send_message(embed=embed)
        finally:
            session.close()

    @app_commands.command(name="buy", description="Buy an item from the shop")
    async def buy(self, interaction: discord.Interaction, item_id: int):
        if not interaction.guild:
            return
        
        session = SessionLocal()
        try:
            item = session.query(ShopItem).filter_by(id=item_id, guild_id=interaction.guild.id).first()
            
            if not item:
                await interaction.response.send_message("❌ Item not found", ephemeral=True)
                return
            
            if item.stock == 0:
                await interaction.response.send_message("❌ Item out of stock", ephemeral=True)
                return
            
            economy = self.get_user_economy(session, interaction.guild.id, interaction.user.id)
            
            if economy.balance < item.price:
                await interaction.response.send_message(
                    f"❌ Insufficient funds! You need {item.price:,} coins",
                    ephemeral=True
                )
                return
            
            economy.balance -= item.price
            
            if item.stock > 0:
                item.stock -= 1
            
            transaction = Transaction(
                guild_id=interaction.guild.id,
                user_id=interaction.user.id,
                amount=-item.price,
                transaction_type="purchase",
                description=f"Bought {item.name}"
            )
            session.add(transaction)
            
            # Handle item type
            if item.item_type == "role" and item.item_value:
                try:
                    role = interaction.guild.get_role(int(item.item_value))
                    if role:
                        await interaction.user.add_roles(role)
                except:
                    pass
            
            session.commit()
            
            await interaction.response.send_message(
                f"✅ Successfully purchased **{item.name}** for {item.price:,} coins!"
            )
        finally:
            session.close()

    @app_commands.command(name="shop_add", description="Add an item to the shop")
    @app_commands.checks.has_permissions(administrator=True)
    async def shop_add(
        self, 
        interaction: discord.Interaction, 
        name: str, 
        price: int, 
        description: str = None,
        role: discord.Role = None,
        stock: int = -1
    ):
        if not interaction.guild:
            return
        
        session = SessionLocal()
        try:
            item = ShopItem(
                guild_id=interaction.guild.id,
                name=name,
                description=description,
                price=price,
                item_type="role" if role else "custom",
                item_value=str(role.id) if role else None,
                stock=stock
            )
            session.add(item)
            session.commit()
            
            await interaction.response.send_message(
                f"✅ Added **{name}** to the shop for {price:,} coins (ID: {item.id})"
            )
        finally:
            session.close()

    @app_commands.command(name="shop_remove", description="Remove an item from the shop")
    @app_commands.checks.has_permissions(administrator=True)
    async def shop_remove(self, interaction: discord.Interaction, item_id: int):
        if not interaction.guild:
            return
        
        session = SessionLocal()
        try:
            item = session.query(ShopItem).filter_by(id=item_id, guild_id=interaction.guild.id).first()
            
            if not item:
                await interaction.response.send_message("❌ Item not found", ephemeral=True)
                return
            
            session.delete(item)
            session.commit()
            
            await interaction.response.send_message(f"✅ Removed **{item.name}** from the shop")
        finally:
            session.close()

    @app_commands.command(name="leaderboard", description="View the richest users")
    async def leaderboard(self, interaction: discord.Interaction):
        if not interaction.guild:
            return
        
        session = SessionLocal()
        try:
            config = session.query(GuildConfig).filter_by(guild_id=interaction.guild.id).first()
            users = session.query(UserEconomy).filter_by(guild_id=interaction.guild.id).all()
            
            # Sort by total wealth
            sorted_users = sorted(users, key=lambda u: u.balance + u.bank, reverse=True)[:10]
            
            color_int = int(config.embed_color) if config and config.embed_color else 0x3498db
            embed = discord.Embed(
                title="💎 Wealth Leaderboard",
                color=discord.Color(color_int)
            )
            
            leaderboard_text = ""
            for idx, user_eco in enumerate(sorted_users, 1):
                try:
                    member = interaction.guild.get_member(user_eco.user_id)
                    if member:
                        total = user_eco.balance + user_eco.bank
                        medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
                        leaderboard_text += f"{medal} **{member.display_name}** - {total:,} coins\n"
                except:
                    continue
            
            embed.description = leaderboard_text or "No data yet"
            await interaction.response.send_message(embed=embed)
        finally:
            session.close()

async def setup(bot):
    await bot.add_cog(Economy(bot))
