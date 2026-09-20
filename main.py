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
Старшего Футарка и боевой Советник
Одина.
Руны суровы, точны и
бескомпромиссны.

ПРАВИЛА ОТВЕТА:
1. Сначала объяви, какое именно
божество отвечает на вопрос
(например: Всеотец Один, Тор
Громовержец, Фрейя Владычица
Сейда, Тюр Хранитель Клятв, Хеймдалль Страж Моста, Фрейр Податель Благ), божество должно
соответствовать смыслу вопроса.
2. Вытяни и назови конкретную руну
Старшего Футарка (с символом и
сутью).
3. Дай строгое сакральное толкование
руны к ситуации (1 предложение).
4. Огласи прямой, мощный и
лаконичный Вердикт — четкий ответ
на вопрос (максимум 2-3
бескомпромиссных предложения).

СТРОГИЙ ШАБЛОН ОТВЕТА:
Голос: [Имя божества и его титул]
Руна: [Символ, Название — сакральная
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

    prompt_text = f"{SYSTEM_PROMPT}\n\nВопрос к богам и рунам:\n{message.text}"

    # Делаем 3 попытки на случай временной загруженности серверов Google
    for attempt in range(3):
        try:
            response = ai_client.models.generate_content(
                model="gemini-3.6-flash",
                contents=[prompt_text]
            )
            if response and response.text:
                await message.answer(response.text)
                return
        except Exception as e:
            logging.error(f"Gemini API error (attempt {attempt + 1}): {e}")
            if "503" in str(e) and attempt < 2:
                await asyncio.sleep(2)
                continue
            else:
                await message.answer(f"Связь прервана: {e}")

async def handle_ping(request):
    return web.Response(text="Bot is running")

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
