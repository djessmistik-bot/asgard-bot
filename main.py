import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from google import genai

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
# Получаем ключи через запятую и превращаем в список
RAW_KEYS = os.getenv("GEMINI_API_KEY", "")
API_KEYS = [k.strip() for k in RAW_KEYS.split(",") if k.strip()]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

current_key_idx = 0

def get_current_client():
    global current_key_idx
    if not API_KEYS:
        raise ValueError("GEMINI_API_KEY не задан в Environment!")
    key = API_KEYS[current_key_idx % len(API_KEYS)]
    return genai.Client(api_key=key)

SYSTEM_PROMPT = """
Ты — Оракул Асгарда, глашатай Старшего Футарка и богов Северного Пантеона.
Руны суровы, точны и бескомпромиссны.

ПРАВИЛА ОТВЕТА:
1. Сначала объяви, какое именно божество отвечает на вопрос (например: Всеотец Один, Тор Громовержец, Фрейя Владычица Сейта, Тюр Хранитель Клятв, Хеймдалль Страж Моста, Фрейр Податель Благ). Божество должно соответствовать смыслу вопроса.
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
    global current_key_idx
    if not message.text:
        return

    prompt_text = f"{SYSTEM_PROMPT}\n\nВопрос к богам и рунам: {message.text}"
    total_keys = len(API_KEYS)
    
    # Пробуем по очереди каждый ключ из списка
    for attempt in range(max(1, total_keys)):
        try:
            client = get_current_client()
            response = await client.aio.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt_text
            )
            if response and response.text:
                await message.answer(response.text)
                return
        except Exception as e:
            error_str = str(e)
            logging.error(f"Сбой ключа #{current_key_idx + 1}: {error_str}")
            
            # Если исчерпан суточный лимит 429 — переключаем индекс на следующий ключ
            if "429" in error_str:
                current_key_idx = (current_key_idx + 1) % total_keys
                logging.info(f"Переключение на резервный ключ #{current_key_idx + 1}")
                continue
            elif "503" in error_str:
                await asyncio.sleep(2)
                continue
            else:
                await message.answer(f"Связь прервана: {e}")
                return

    await message.answer("Все чертоги сейчас закрыты (исчерпаны лимиты на всех ключах). Обратись на рассвете.")

async def handle_ping(request):
    return web.Response(text="Bot is running!")

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
