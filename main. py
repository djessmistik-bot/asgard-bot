import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from google import genai

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
ai_client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """
Ты — мудрый и немногословный Оракул Асгарда, проводник воли скандинавских богов. 
Твой стиль: строгий, глубокий, проницательный, без эзотерической воды.
Отвечай точно на вопрос или выпавшие руны.
Каждое предложение пиши с новой строки.
Длина всего ответа строго до 10 коротких, емких предложений.
"""

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Врата Асгарда открыты. Задай свой сокровенный вопрос или назови выпавшие руны."
    )

@dp.message()
async def handle_message(message: Message):
    if not message.text:
        return
    try:
        response = ai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{SYSTEM_PROMPT}\n\nВопрос вопрошающего: {message.text}"
        )
        await message.answer(response.text)
    except Exception as e:
        await message.answer("Шепот богов затих в тумане. Попробуй задать вопрос снова.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from google import genai

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
ai_client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """
Ты — мудрый и немногословный Оракул Асгарда, проводник воли скандинавских богов. 
Твой стиль: строгий, глубокий, проницательный, без эзотерической воды.
Отвечай точно на вопрос или выпавшие руны.
Каждое предложение пиши с новой строки.
Длина всего ответа строго до 10 коротких, емких предложений.
"""

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Врата Асгарда открыты. Задай свой сокровенный вопрос или назови выпавшие руны."
    )

@dp.message()
async def handle_message(message: Message):
    if not message.text:
        return
    try:
        response = ai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{SYSTEM_PROMPT}\n\nВопрос вопрошающего: {message.text}"
        )
        await message.answer(response.text)
    except Exception as e:
        await message.answer("Шепот богов затих в тумане. Попробуй задать вопрос снова.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
