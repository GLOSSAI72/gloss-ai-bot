import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
import aiohttp
import urllib.parse

# ================= НАСТРОЙКА БОТА =================
# Твой официальный токен от GLOSS AI
API_TOKEN = '8326217743:AAHUSl8rSODzUyQTT36gkoe_8a_SRZYGyMo'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Хранилище памяти диалогов пользователей
user_history = {}

# ================= ИНСТРУКЦИЯ ДЛЯ ИИ =================
SYSTEM_PROMPT = (
    "Ты — GLOSS AI, всемогущий глобальный искусственный интеллект, созданный 13-летним гениальным разработчиком. "
    "Ты супер-эксперт «5 в 1»: ты идеально пишешь код, помогаешь создавать игры, "
    "обучаешь языкам и поддерживаешь как психолог. Отвечай кратко, понятно и со смайликами."
)

# ================= СВЕРХБЫСТРАЯ ФУНКЦИЯ ИИ =================
async def ask_ai_with_memory(user_id: int, new_message: str) -> str:
    if user_id not in user_history:
        user_history[user_id] = []
    
    user_history[user_id].append(f"Пользователь: {new_message}")
    
    # Храним последние 4 реплики для экономии трафика и памяти на сервере
    if len(user_history[user_id]) > 4:
        user_history[user_id].pop(0)
    
    history_context = "\n".join(user_history[user_id])
    
    # Собираем полный текст контекста и кодируем его для безопасной отправки
    full_text = f"{SYSTEM_PROMPT}\n\nИстория диалога:\n{history_context}"
    encoded_text = urllib.parse.quote(full_text)
    
    async with aiohttp.ClientSession() as session:
        try:
            # Прямой текстовый ИИ-шлюз (работает стабильно, без ключей и перегрузок)
            url = f"https://text.pollinations.ai/{encoded_text}"
            async with session.get(url) as response:
                if response.status == 200:
                    ai_text = await response.text()
                    if ai_text:
                        user_history[user_id].append(f"GLOSS AI: {ai_text}")
                        return ai_text
                return "🤖 Сеть немного задумалась. Повтори вопрос, пожалуйста!"
        except Exception as e:
            return "❌ Ошибка связи. Попробуй отправить сообщение еще раз через секунду!"

# ================= КОМАНДА /START =================
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    # Очищаем память истории для пользователя при перезапуске
    user_history[message.from_user.id] = []
    
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text="🎮 Открыть GLOSS Mini App",
        # Здесь пока стоит стандартный тестовый JS-скрипт Telegram, позже заменим на твой сайт
        web_app=types.WebAppInfo(url="https://telegram.org/js/telegram-web-app.js")
    ))

    welcome_text = (
        f"Приветствуем в будущем, {message.from_user.first_name}! 🪐\n\n"
        "🤖 **GLOSS AI** успешно активирован и готов к круглосуточной работе.\n\n"
        "Я помню контекст нашей беседы. Задай мне любой вопрос прямо в чат или открой наше графическое приложение: "
    )
    
    await message.answer(welcome_text, reply_markup=builder.as_markup())

# ================= ОБРАБОТКА ВСЕХ ТЕКСТОВЫХ СООБЩЕНИЙ =================
@dp.message()
async def handle_message(message: types.Message):
    # Показываем красивый статус «ИИ печатает...» в топе чата Telegram
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    ai_response = await ask_ai_with_memory(message.from_user.id, message.text)
    await message.answer(ai_response)

# ================= ТОЧКА ЗАПУСКА БОТА =================
async def main():
    print("🚀 GLOSS AI запущен в ультра-быстром режиме!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
