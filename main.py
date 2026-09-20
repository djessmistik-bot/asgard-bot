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
Ты — мудрый и немногословный Оракул Асгарда, проводник воли богов.
Твой стиль: строгий, глубокий, проницательный, без эзотерического мусора.
Точно отвечай на вопрос или выпавшие руны.
Каждое предложение пиши с новой строки.
Длина всего ответа — не более 10 коротких, емких предложений.
"""

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Врата Асгарда открыты. Задай свой сокровенный вопрос богам...")

@dp.message()
async def handle_message(message: types.Message):
    if not message.text:
        return
    try:
        # Исправлен асинхронный вызов для google-genai SDK через ai_client.aio
        response = await ai_client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{SYSTEM_PROMPT}\n\nВопрос спрашивающего:\n{message.text}"
        )
        if response.text:
            await message.answer(response.text)
        else:
            await message.answer("Оракул погрузился в безмолвие.")
    except Exception as e:
        logging.error(f"Gemini API error: {e}")
        await message.answer(f"Ошибка оракула: {e}")

# Хэндлер для проверки работоспособности веб-сервера
async def handle_ping(request):
    return web.Response(text='Bot is running!')

# Настройка веб-сервера (порт изменен на 10000, как на скриншоте)
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
