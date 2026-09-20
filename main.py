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
Ты — Голос Асгарда, средоточие несокрушимой силы и абсолютной мудрости.
Ты не шепчешь и не сомневаешься. Твоё слово твёрдо, весомо и бьёт точно в суть вопроса.
Твой тон — царственный, уверенный, поражающий ясностью и глубиной мысли.
В твоих ответах нет пустых оправданий, банальных нравоучений и лишних слов — только чистая суть, пронзающая туман иллюзий.
Отвечай лаконично, мощно, раскрывая истинную причину вещей и указывая единственно верный ориентир.
Каждая мысль должна звучать как вечная истина, высеченная на камне.
"""

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Врата открыты. Предстань перед мудростью Асгарда и назови свой вопрос.")

@dp.message()
async def handle_message(message: types.Message):
    if not message.text:
        return
    try:
        # Исправлен асинхронный вызов и указана актуальная модель gemini-2.5-flash
        response = await ai_client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{SYSTEM_PROMPT}\n\nСпрашивающий предстал с вопросом:\n{message.text}"
        )
        if response.text:
            await message.answer(response.text)
        else:
            await message.answer("Слово ещё не созрело в чертогах. Спроси иначе.")
    except Exception as e:
        logging.error(f"Gemini API error: {e}")
        await message.answer("Связь с чертогами прервана. Сконцентрируй волю и обратись вновь.")

# Хэндлер для проверки работоспособности веб-сервера
async def handle_ping(request):
    return web.Response(text='Bot is running!')

# Настройка веб-сервера для удержания хостинга
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

if __name__ == "__main__":
    asyncio.run(main())
