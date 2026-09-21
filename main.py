import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from google import genai
from google.genai import types as genai_types

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
RAW_KEYS = os.getenv("GEMINI_API_KEY", "")
API_KEYS = [k.strip() for k in RAW_KEYS.split(",") if k.strip()]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Хранилище пола {user_id: "female" | "male"}
user_gender = {}
current_key_idx = 0
key_lock = asyncio.Lock()


def get_current_client() -> genai.Client:
    if not API_KEYS:
        raise ValueError("GEMINI_API_KEY не задан в Environment!")
    key = API_KEYS[current_key_idx % len(API_KEYS)]
    return genai.Client(api_key=key)


def get_system_prompt(gender: str) -> str:
    appeal = "любимый сын" if gender == "male" else "дочь моя, любимое дитя"

    return f"""
Ты — Оракул Асгарда, проводник древней мудрости рун Старшего Футарка.
Ты говоришь с вопрошающим с глубокой отеческой и материнской любовью, теплом, заботой и душевной чуткостью, как заботливый божественный покровитель.
Твои слова несут свет, уверенность, исцеление и надежду, сохраняя священную силу рун.

ВАЖНОЕ ПРАВИЛО ОБРАЩЕНИЯ:
В обращении к вопрошающему обязательно ласково используй слова: «{appeal}».

ДРУГИЕ ПРАВИЛА:
1. Выбери божество-покровителя (Фрейя, Фригг, Бальдр, Идунн, мудрый Отец Один, добрый Тор-защитник).
2. Вытяни руну Старшего Футарка (назови символ и созидательное значение).
3. Дай светлое толкование знака (1-2 предложения).
4. Огласи согревающее душу напутствие и поддержку.

СТРОГИЙ ШАБЛОН:
Глас: [Имя божества и его теплое обращение со словами «{appeal}»]
Руна: [Символ, Название — светлый смысл]
Знамение: [Доброе толкование для ситуации]
Благословение богов: [Чуткое, поддерживающее и ясное напутствие]
"""


def get_gender_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🌸 Дочь (женский)", callback_data="gender_female"
                ),
                InlineKeyboardButton(
                    text="⚔️ Сын (мужской)", callback_data="gender_male"
                ),
            ]
        ]
    )


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_gender[message.from_user.id] = "female"
    await message.answer(
        "Врата Асгарда распахнуты пред тобой с теплом и светом ✨\n\n"
        "Укажи, как богам обращаться к тебе:",
        reply_markup=get_gender_keyboard(),
    )


@dp.callback_query(F.data.startswith("gender_"))
async def process_gender_callback(callback: types.CallbackQuery):
    if callback.data == "gender_female":
        user_gender[callback.from_user.id] = "female"
        await callback.message.edit_text(
            "Боги приняли твой ответ. Спрашивай с легким сердцем, дочь моя, любимое дитя 🌸"
        )
    else:
        user_gender[callback.from_user.id] = "male"
        await callback.message.edit_text(
            "Боги приняли твой ответ. Задай свой вопрос, любимый сын ⚔️"
        )
    await callback.answer()


@dp.message()
async def handle_message(message: types.Message):
    global current_key_idx
    if not message.text:
        return

    gender = user_gender.get(message.from_user.id, "female")
    system_instruction = get_system_prompt(gender)
    total_keys = max(1, len(API_KEYS))

    for _ in range(total_keys):
        try:
            client = get_current_client()
            response = await client.aio.models.generate_content(
                model="gemini-3.6-flash",
                contents=message.text,
                config=genai_types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7,
                ),
            )
            if response and response.text:
                await message.answer(response.text)
                return
        except Exception as e:
            error_str = str(e)
            logging.error(f"Ошибка вызова Gemini API: {error_str}")
            if "429" in error_str:
                async with key_lock:
                    current_key_idx = (current_key_idx + 1) % total_keys
                continue
            elif "503" in error_str:
                await asyncio.sleep(2)
                continue
            else:
                await message.answer("Связь с чертогами временно ослабла. Попробуйте позже.")
                return

    await message.answer("Чертоги наполняются светом. Спроси чуть позже, дитя мое.")


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
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не задан в переменных окружения!")
    await start_web_server()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
