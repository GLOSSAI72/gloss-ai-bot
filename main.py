import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
import aiohttp
import urllib.parse

# ================= НАСТРОЙКА БОТА =================
API_TOKEN = '8326217743:AAHUSl8rSODzUyQTT36gkoe_8a_SRZYGyMo'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

user_history = {}

SYSTEM_PROMPT = (
    "Ты — GLOSS AI, всемогущий глобальный искусственный интеллект, созданный 13-летним гениальным разработчиком. "
    "Ты супер-эксперт «5 в 1»: ты идеально пишешь код, помогаешь создавать игры, "
    "обучаешь языкам и поддерживаешь как психолог. Отвечай кратко, понятно и со смайликами."
)

async def ask_ai_with_memory(user_id: int, new_message: str) -> str:
    if user_id not in user_history:
        user_history[user_id] = []
    
    user_history[user_id].append(f"Пользователь: {new_message}")
    
    if len(user_history[user_id]) > 4:
        user_history[user_id].pop(0)
    
    history_context = "\n".join(user_history[user_id])
    full_text = f"{SYSTEM_PROMPT}\n\nИстория диалога:\n{history_context}"
    encoded_text = urllib.parse.quote(full_text)
    
    async with aiohttp.ClientSession() as session:
        try:
            # Используем самый быстрый и свободный шлюз без блокировок
            url = f"https://moescape.pollinations.ai/{encoded_text}"
            async with session.get(url) as response:
                if response.status == 200:
                    ai_text = await response.text()
                    if ai_text:
                        # Убираем возможные систем
