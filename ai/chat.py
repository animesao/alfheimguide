import asyncio
import logging
import os
import json
from discord.ext import commands
from openai import OpenAI

ai_token = os.getenv("AI_TOKEN")

# Initialize OpenAI client for OpenRouter
client = None
if ai_token:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=ai_token,
    )

conversation_history = {}

class AIChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ask")
    async def ask_command(self, ctx, *, message):
        """Команда для общения с AI с поддержкой рассуждений (reasoning)"""
        # Re-initialize client to pick up latest env vars
        global client
        ai_token = os.getenv("AI_TOKEN")
        if ai_token and (not client or client.api_key != ai_token):
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=ai_token,
            )

        if not client or not client.api_key or client.api_key == "your_openrouter_token_here":
            await ctx.send("❌ AI_TOKEN не настроен или содержит значение по умолчанию в .env. Пожалуйста, вставьте ваш реальный токен OpenRouter.")
            return

        try:
            channel_id = ctx.channel.id
            if channel_id not in conversation_history:
                conversation_history[channel_id] = []

            # Add user message to history
            conversation_history[channel_id].append({
                "role": "user",
                "content": message
            })

            # Limit history to last 10 messages
            if len(conversation_history[channel_id]) > 10:
                conversation_history[channel_id] = conversation_history[channel_id][-10:]

            async with ctx.typing():
                try:
                    # Execute API call in a thread pool since openai-python is synchronous
                    def get_completion():
                        return client.chat.completions.create(
                            model="nvidia/nemotron-3-nano-30b-a3b:free",
                            messages=conversation_history[channel_id],
                            extra_body={"reasoning": {"enabled": True}}
                        )

                    response = await asyncio.get_event_loop().run_in_executor(None, get_completion)
                    
                    # Extract message and reasoning
                    assistant_msg = response.choices[0].message
                    content = assistant_msg.content
                    # OpenRouter specific: reasoning_details might be in the message object
                    reasoning = getattr(assistant_msg, 'reasoning_details', None)

                    # Update history with reasoning_details for context preservation
                    history_entry = {
                        "role": "assistant",
                        "content": content
                    }
                    if reasoning:
                        history_entry["reasoning_details"] = reasoning
                    
                    conversation_history[channel_id].append(history_entry)

                    # Handle long messages
                    if len(content) > 1900:
                        chunks = [content[i:i+1900] for i in range(0, len(content), 1900)]
                        for chunk in chunks:
                            await ctx.send(chunk)
                            await asyncio.sleep(0.5)
                    else:
                        await ctx.send(content)

                except Exception as api_error:
                    logging.error(f"Ошибка API: {str(api_error)}")
                    await ctx.send(f"❌ Ошибка при обращении к API: {str(api_error)}")

        except Exception as e:
            logging.error(f"Ошибка при обработке команды: {str(e)}")
            await ctx.send(f"❌ Произошла ошибка: {str(e)}")

    @commands.command(name="clear")
    async def clear_history(self, ctx):
        """Очистка истории беседы"""
        channel_id = ctx.channel.id
        if channel_id in conversation_history:
            conversation_history[channel_id] = []
            await ctx.send("🧹 История беседы очищена!")
        else:
            await ctx.send("История беседы уже пуста!")

    @commands.command(name="helpai")
    async def help_command(self, ctx):
        """Показать справку по AI"""
        help_text = (
            "**🤖 AI Помощник (Nemotron 30B):**\n"
            "Я поддерживаю сложные рассуждения и помню контекст диалога.\n\n"
            "**Команды:**\n"
            "`!ask [сообщение]` - Задать вопрос AI\n"
            "`!clear` - Забыть историю текущего канала\n"
            "`!helpai` - Показать это сообщение\n"
        )
        await ctx.send(help_text)

async def setup(bot):
    await bot.add_cog(AIChat(bot))