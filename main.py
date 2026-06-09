import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
import aiohttp

# ================= НАСТРОЙКА БОТА =================
API_TOKEN = '8326217743:AAHUSl8rSODzUyQTT36gkoe_8a_SRZYGyMo'
GEMINI_API_KEY = 'AIzaSyAQ.Ab8RN6KKMt6thZlExPRawRZjbFDek4WXcAYIF4cI-6lmlI_7Bg'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

user_history = {}

SYSTEM_PROMPT = (
    "Ты — GLOSS AI, всемогущий глобальный искусственный интеллект, созданный 13-летним гениальным разработчиком. "
    "Ты супер-эксперт «5 в 1»: идеально пишешь код, помогаешь создавать игры, "
    "обучаешь языкам и поддерживаешь как психолог. Отвечай кратко, понятно и со смайликами."
)

async def ask_gemini(user_id: int, new_message: str) -> str:
    if user_id not in user_history:
        user_history[user_id] = []
    
    user_history[user_id].append({"role": "user", "parts": [{"text": new_message}]})
    
    if len(user_history[user_id]) > 6:
        user_history[user_id].pop(0)
        
    contents = user_history[user_id].copy()
    contents.insert(0, {"role": "user", "parts": [{"text": f"Системная инструкция: {SYSTEM_PROMPT}"}]})

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json={"contents": contents}, timeout=15) as response:
                if response.status == 200:
                    res_json = await response.json()
                    ai_text = res_json['candidates'][0]['content']['parts'][0]['text']
                    user_history[user_id].append({"role": "model", "parts": [{"text": ai_text}]})
                    return ai_text
                else:
                    err_data = await response.text()
                    return f"🤖 Ошибка сервера Google (Код {response.status}). Попробуй позже!"
        except Exception as e:
            return f"❌ Ошибка сети: {str(e)}"

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    user_history[message.from_user.id] = []
    
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text="🎮 Открыть GLOSS Mini App",
        web_app=types.WebAppInfo(url="https://telegram.org/js/telegram-web-app.js")
    ))

    welcome_text = (
        f"Приветствуем в будущем, {message.from_user.first_name}! 🪐\n\n"
        "🤖 **GLOSS AI** успешно активирован и переведен на официальный движок Google Gemini.\n\n"
        "Задай мне любой вопрос прямо в чат: "
    )
    
    await message.answer(welcome_text, reply_markup=builder.as_markup())

@dp.message()
async def handle_message(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    ai_response = await ask_gemini(message.from_user.id, message.text)
    await message.answer(ai_response)

async def main():
    print("🚀 GLOSS AI на движке Gemini успешно запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
