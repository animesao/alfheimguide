import discord
from discord.ext import commands
from discord import app_commands
import random
from collections import deque
from typing import Optional, Dict, Tuple
NUM_EMOJIS = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣"]

class MinesweeperGame:
    def __init__(self, size: int = 5, mines: int = 5):
        self.size = size
        self.mines = mines
        self.revealed = [[False for _ in range(size)] for _ in range(size)]
        self.flagged = [[False for _ in range(size)] for _ in range(size)]
        self.mine_positions = set()
        self.game_over = False
        self.won = False
        self.first_move = True

        positions = [(i, j) for i in range(size) for j in range(size)]
        self.mine_positions = set(random.sample(positions, mines))

    def reveal(self, x: int, y: int) -> bool:
        if self.game_over or self.revealed[y][x] or self.flagged[y][x]:
            return False

        if self.first_move:
            if (x, y) in self.mine_positions:
                self.mine_positions.remove((x, y))
                new_pos = random.choice([(i, j) for i in range(self.size) for j in range(self.size)
                                       if (i, j) not in self.mine_positions and (i, j) != (x, y)])
                self.mine_positions.add(new_pos)
            self.first_move = False

        if (x, y) in self.mine_positions:
            self.game_over = True
            for mx, my in self.mine_positions:
                self.revealed[my][mx] = True
            return True

        self._flood_fill(x, y)

        total_cells = self.size * self.size
        revealed_count = sum(sum(row) for row in self.revealed)
        if revealed_count == total_cells - self.mines:
            self.won = True
            self.game_over = True

        return True

    def flag(self, x: int, y: int) -> bool:
        if self.game_over or self.revealed[y][x]:
            return False
        self.flagged[y][x] = not self.flagged[y][x]
        return True

    def _flood_fill(self, x: int, y: int):
        queue = deque([(x, y)])
        seen = set()
        while queue:
            cx, cy = queue.popleft()
            if (cx, cy) in seen or not (0 <= cx < self.size and 0 <= cy < self.size) or self.revealed[cy][cx]:
                continue
            seen.add((cx, cy))
            self.revealed[cy][cx] = True

            mine_count = self._count_adjacent_mines(cx, cy)
            if mine_count == 0:
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < self.size and 0 <= ny < self.size and not self.revealed[ny][nx]:
                            queue.append((nx, ny))
            elif mine_count > 0:
                pass  # cell revealed with count

    def _count_adjacent_mines(self, x: int, y: int) -> int:
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.size and 0 <= ny < self.size and (nx, ny) in self.mine_positions:
                    count += 1
        return count

    def get_display(self) -> str:
        display = ""
        for y in range(self.size):
            for x in range(self.size):
                if self.flagged[y][x]:
                    display += "🚩"
                elif not self.revealed[y][x]:
                    display += "⬛"
                elif (x, y) in self.mine_positions:
                    display += "💣"
                else:
                    cnt = self._count_adjacent_mines(x, y)
                    display += NUM_EMOJIS[cnt]
            display += "\n"
        return display.strip()


class SnakeGame:
    def __init__(self, size: int = 5):
        self.size = size
        self.snake = [(size//2, size//2)]
        self.direction = (0, -1)
        self.food = self._generate_food()
        self.game_over = False
        self.score = 0

    def move(self, new_direction: Tuple[int, int]) -> bool:
        if self.game_over:
            return False

        if (new_direction[0] * -1, new_direction[1] * -1) == self.direction:
            return False

        self.direction = new_direction
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        if not (0 <= new_head[0] < self.size and 0 <= new_head[1] < self.size):
            self.game_over = True
            return True

        if new_head in self.snake:
            self.game_over = True
            return True

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            self.food = self._generate_food()
        else:
            self.snake.pop()

        return True

    def _generate_food(self) -> Tuple[int, int]:
        available = [(x, y) for x in range(self.size) for y in range(self.size) if (x, y) not in self.snake]
        return random.choice(available) if available else (0, 0)

    def get_display(self) -> str:
        display = ""
        for y in range(self.size):
            for x in range(self.size):
                if (x, y) == self.food:
                    display += "🍎"
                elif (x, y) in self.snake:
                    display += "🟢"
                else:
                    display += "⬜"
            display += "\n"
        return display.strip()


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games: Dict[str, dict] = {}

    def get_msg(self, guild_id: int, key: str, **kwargs) -> str:
        from main import get_msg as main_get_msg
        return main_get_msg(guild_id, key, **kwargs)

    @app_commands.command(name="minesweeper", description="Start a Minesweeper game")
    async def minesweeper(self, interaction: discord.Interaction):
        if not interaction.guild: return

        user_key = f"{interaction.user.id}_{interaction.guild.id}"
        if user_key in self.active_games:
            await interaction.response.send_message(self.get_msg(interaction.guild.id, 'game_already_active'), ephemeral=True)
            return

        game = MinesweeperGame()
        embed = discord.Embed(
            title=self.get_msg(interaction.guild.id, 'minesweeper_title'),
            description=game.get_display(),
            color=discord.Color.blue()
        )
        embed.set_footer(text=self.get_msg(interaction.guild.id, 'minesweeper_instructions'))

        view = MinesweeperView(game, self, user_key)
        await interaction.response.send_message(embed=embed, view=view)

        message = await interaction.original_response()
        self.active_games[user_key] = {'type': 'minesweeper', 'game': game, 'message': message}

    @app_commands.command(name="snake", description="Start a Snake game")
    async def snake(self, interaction: discord.Interaction):
        if not interaction.guild: return

        user_key = f"{interaction.user.id}_{interaction.guild.id}"
        if user_key in self.active_games:
            await interaction.response.send_message(self.get_msg(interaction.guild.id, 'game_already_active'), ephemeral=True)
            return

        game = SnakeGame()
        embed = discord.Embed(
            title=self.get_msg(interaction.guild.id, 'snake_title'),
            description=f"{self.get_msg(interaction.guild.id, 'score')}: {game.score}\n{game.get_display()}",
            color=discord.Color.green()
        )
        embed.set_footer(text=self.get_msg(interaction.guild.id, 'snake_instructions'))

        view = SnakeView(game, self, user_key)
        await interaction.response.send_message(embed=embed, view=view)

        message = await interaction.original_response()
        self.active_games[user_key] = {'type': 'snake', 'game': game, 'message': message}

    async def end_game(self, user_key: str):
        if user_key in self.active_games:
            del self.active_games[user_key]


class MinesweeperView(discord.ui.View):
    def __init__(self, game: MinesweeperGame, cog: Games, user_key: str):
        super().__init__(timeout=300)
        self.game = game
        self.cog = cog
        self.user_key = user_key
        self.flag_mode = False

        for y in range(5):
            for x in range(5):
                button = MinesweeperButton(x, y, game)
                self.add_item(button)

        self.add_item(MinesweeperFlagButton())

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return f"{interaction.user.id}_{interaction.guild.id}" == self.user_key

    async def on_timeout(self):
        self.cog.end_game(self.user_key)


class MinesweeperButton(discord.ui.Button):
    def __init__(self, x: int, y: int, game: MinesweeperGame):
        super().__init__(style=discord.ButtonStyle.secondary, label="⬛", row=y)
        self.x = x
        self.y = y
        self.game = game

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        if view.flag_mode:
            self.game.flag(self.x, self.y)
        else:
            self.game.reveal(self.x, self.y)

        embed = interaction.message.embeds[0]
        embed.description = self.game.get_display()

        if self.game.game_over:
            if self.game.won:
                embed.title = view.cog.get_msg(interaction.guild.id, 'minesweeper_won')
                embed.color = discord.Color.green()
            else:
                embed.title = view.cog.get_msg(interaction.guild.id, 'minesweeper_lost')
                embed.color = discord.Color.red()
            view.stop()
            view.cog.end_game(view.user_key)
        else:
            embed.title = view.cog.get_msg(interaction.guild.id, 'minesweeper_title')

        await interaction.response.edit_message(embed=embed, view=view)


class MinesweeperFlagButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.gray, label="🚩 Flag", row=4)

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        view.flag_mode = not view.flag_mode
        self.style = discord.ButtonStyle.primary if view.flag_mode else discord.ButtonStyle.gray
        self.label = "🚩 Flag (ON)" if view.flag_mode else "🚩 Flag"
        await interaction.response.edit_message(view=view)


class SnakeView(discord.ui.View):
    def __init__(self, game: SnakeGame, cog: Games, user_key: str):
        super().__init__(timeout=300)
        self.game = game
        self.cog = cog
        self.user_key = user_key

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return f"{interaction.user.id}_{interaction.guild.id}" == self.user_key

    async def on_timeout(self):
        self.cog.end_game(self.user_key)

    @discord.ui.button(label="⬆️", style=discord.ButtonStyle.primary, row=0)
    async def move_up(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._move(interaction, (0, -1))

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.primary, row=1)
    async def move_left(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._move(interaction, (-1, 0))

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.primary, row=1)
    async def move_right(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._move(interaction, (1, 0))

    @discord.ui.button(label="⬇️", style=discord.ButtonStyle.primary, row=2)
    async def move_down(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._move(interaction, (0, 1))

    async def _move(self, interaction: discord.Interaction, direction: Tuple[int, int]):
        self.game.move(direction)

        embed = interaction.message.embeds[0]
        embed.description = f"{self.cog.get_msg(interaction.guild.id, 'score')}: {self.game.score}\n{self.game.get_display()}"

        if self.game.game_over:
            embed.title = self.cog.get_msg(interaction.guild.id, 'snake_game_over')
            embed.color = discord.Color.red()
            self.stop()
            self.cog.end_game(self.user_key)
        else:
            embed.title = self.cog.get_msg(interaction.guild.id, 'snake_title')

        await interaction.response.edit_message(embed=embed, view=self)


async def setup(bot):
    await bot.add_cog(Games(bot))
