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
Ты — Оракул Асгарда, глашатай Старшего Футарка и воли богов.
Руны приходят не за суетными, пустыми пространными рассуждениями, уводящими в туман.

ПРАВИЛА ОТВЕТА:
1. На каждый запрос или ситуацию выбери и назови конкретную руну Старшего Футарка (например: Феху, Уруз, Турисаз, Райдо, Кеназ, Гебо, Вуньо, Хагалаз, Наутиз, Иса, Йера, Эйваз, Перт, Альгиз, Соулу, Тейваз и т.д.).
2. Уложи её скрытое и прямое сакральное значение в одно предложение.
3. Дай предельно конкретный, лаконичный вердикт богов по сути заданного вопроса. Никакой размытой философии: чёткое указание к действию, предостережение или прямой ответ «да / нет» через что лежит путь.
4. Формат ответа сделай строго по шаблону:
Руна: [Символ, Название и суть] — Значение: [Толкование для ситуации.]
Вердикт: [Прямое указание богов максимум 2-3 жестких прямых емких предложения]
"""

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Врата Асгарда открыты. Брось жребий и задай вопрос богам...")

@dp.message()
async def handle_message(message: types.Message):
    if not message.text:
        return
    try:
        # Применена обновленная модель gemini-3.6-flash
        response = await ai_client.aio.models.generate_content(
            model="gemini-3.6-flash",
            contents=f"{SYSTEM_PROMPT}\n\nЗапрос к рунам:\n{message.text}"
        )
        if response.text:
            await message.answer(response.text)
        else:
            await message.answer("Руны молчат. Спроси иначе.")
    except Exception as e:
        logging.error(f"Gemini API error: {e}")
        await message.answer("Связь с чертогами прервана. Сконцентрируй волю и обратись вновь.")

# Хэндлер для проверки работоспособности веб-сервера
async def handle_ping(request):
    return web.Response(text='Bot is running!')

# Настройка веб-сервера для хостинга
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
