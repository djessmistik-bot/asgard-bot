import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from google import genai

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация токенов из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
ai_client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """
Ты — Оракул Асгарда, глашатай Старшего Футарка и богов Северного Пантеона.
Руны суровы, точны и бескомпромиссны.

ПРАВИЛА ОТВЕТА:
1. Сначала объяви, какое именно божество отвечает на вопрос (например: Всеотец Один, Тор Громовержец, Фрейя Владычица Сейда, Тюр Хранитель Клятв, Хеймдалль Страж Моста, Фрейр Податель Благ). Божество должно соответствовать смыслу вопроса.
2. Вытяни и назови конкретную руну Старшего Футарка (с символом и сутью).
3. Дай строгое сакральное толкование руны к ситуации (1 предложение).
4. Огласи прямой, мощный и лаконичный Вердикт — четкий ответ на вопрос (максимум 2-3 бескомпромиссных предложения).

СТРОГИЙ ШАБЛОН ОТВЕТА:
Глас: [Имя божества и его титул]
Руна: [Символ, Название — сакральная суть]
Толкование: [В чем суть знака для вопроса]
Вердикт: [Прямой, бескомпромиссный ответ и воля бога]
"""

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Врата Асгарда распахнуты. Назови свой вопрос богам...")

@dp.message()
async def handle_message(message: types.Message):
    if not message.text:
        return
    try:
        # Использована модель gemini-3.6-flash и асинхронный метод
        response = await ai_client.aio.models.generate_content(
            model="gemini-3.6-flash",
            contents=f"{SYSTEM_PROMPT}\n\nВопрос к богам и рунам:\n{message.text}"
        )
        if response.text:
            await message.answer(response.text)
        else:
            await message.answer("Боги хранят молчание. Спроси иначе.")
    except Exception as e:
        logging.error(f"Gemini API error: {e}")
        await message.answer(f"Ошибка API: {e}"

async def handle_ping(request):
    return web.Response(text='Bot is running!')

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    app.router.add_get("/healthz", handle_ping)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    await start_web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
