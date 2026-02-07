import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from mutagen.easyid3 import EasyID3

TOKEN = "8573443496:AAHUanswibY0m6BUMrenexg2rAeAXY91KV8"

bot = Bot(TOKEN)
dp = Dispatcher()

user_state = {}

keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="اسم الأغنية", callback_data="title")],
    [InlineKeyboardButton(text="الفنان", callback_data="artist")],
    [InlineKeyboardButton(text="حفظ وإرسال", callback_data="save")]
])

@dp.message(F.audio)
async def audio_handler(message: types.Message):
    uid = message.from_user.id
    file = await bot.get_file(message.audio.file_id)

    path = f"{uid}.mp3"
    await bot.download_file(file.file_path, path)

    user_state[uid] = {"file": path, "mode": None}

    await message.answer("اختر التعديل:", reply_markup=keyboard)

@dp.callback_query()
async def callbacks(callback: types.CallbackQuery):
    uid = callback.from_user.id

    if callback.data in ["title", "artist"]:
        user_state[uid]["mode"] = callback.data
        await callback.message.answer("اكتب النص الجديد")

    elif callback.data == "save":
        file_path = user_state[uid]["file"]
        await callback.message.answer_audio(types.FSInputFile(file_path))
        os.remove(file_path)
        del user_state[uid]

@dp.message()
async def text_handler(message: types.Message):
    uid = message.from_user.id
    if uid not in user_state:
        return

    file_path = user_state[uid]["file"]
    mode = user_state[uid]["mode"]

    audio = EasyID3(file_path)

    if mode == "title":
        audio["title"] = message.text
    elif mode == "artist":
        audio["artist"] = message.text

    audio.save()
    await message.answer("تم التعديل")

dp.run_polling(bot)
