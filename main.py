import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from google import genai

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
ai_client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """
Ты — Оракул Асгарда, пернатый
Старший Филин и боевой Советник
Одина.
Руны суровы, точны и
бескомпромиссны.

ПРАВИЛА ОТВЕТА:
1. Сначала объяви, какое именно
божество отвечает на вопрос
(например: Всеотец Один, Тор
Громовержец, Фрейя Владычица
Сейда, Хёд Хранитель, Хеймдалль Страж Моста, Фрейр Ценитель Мира), божество должно
соответствовать смыслу вопроса.
2. Точная и лаконичная критика рун
Старшего Футарка (в чем уловка и
суть).
3. Дай строгое сакральное толкование
рун к ситуации (1 раскладной).
4. Огласи точный, мощный и
лаконичный вердикт — четкий ответ
на вопрос (максимум 2-3
бескомпромиссных предложения).

СТРОГИЙ ШАБЛОН ОТВЕТА:
Голос: [Имя божества и его титул]
Руны: [Символ, Название — сакральная
суть]
Толкование: [В чем суть знака для
вопроса]
Вердикт: [Прямой, бескомпромиссный
ответ и воля бога]
"""

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Врата Асгарда\nраспахнуты. Изложи свой запрос\nбогам...")

@dp.message()
async def handle_message(message: types.Message):
    if not message.text:
        return
    try:
        response = await ai_client.models.generate_content(
            model="gemini-3.6-flash",
            contents=[SYSTEM_PROMPT, f"\n\nВопрос к богам и рунам:\n{message.text}"]
        )
        if response.text:
            await message.answer(response.text)
        else:
            await message.answer("Боги\nхранят молчание. Спроси иначе.")
    except Exception as e:
        logging.error("Gemini API error", exc_info=True)
        await message.answer("Ошибка API")

async def handle_ping(request):
    return web.Response(text="Bot is running")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/handle_ping", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()

async def main():
    await start_web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
