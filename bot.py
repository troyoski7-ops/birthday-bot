import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

# Telegram Bot Token
API_TOKEN = "8854916574:AAHhpQWzOOH7IKjuitJfS_yspUoWy0z2So4"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Netlify Web App Link
NETLIFY_URL = "https://earnest-jelly-986463.netlify.app"


# Define states
class BirthdayForm(StatesGroup):
  year = State()
  month = State()
  date = State()
  time = State()
  am_pm = State()
  photo = State()
  video = State()
  song = State()
  voice = State()
  audio = State()


# Skip button helper
def get_skip_keyboard():
  return InlineKeyboardMarkup(
      inline_keyboard=[
          [InlineKeyboardButton(text="⏭️ Skip", callback_data="skip_step")]
      ]
  )


# /start command
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
  web_app_kb = InlineKeyboardMarkup(
      inline_keyboard=[[
          InlineKeyboardButton(
              text="🎉 Open Birthday Web App",
              web_app=WebAppInfo(url=NETLIFY_URL),
          )
      ]]
  )
  await message.answer(
      "Hello! Click the button below to open the birthday website:",
      reply_markup=web_app_kb,
  )
  await message.answer(
      "1. Please provide the **Year** (or tap Skip):",
      reply_markup=get_skip_keyboard(),
  )
  await state.set_state(BirthdayForm.year)


# Skip button handler
@dp.callback_query(F.data == "skip_step")
async def process_skip(callback: types.CallbackQuery, state: FSMContext):
  current_state = await state.get_state()

  if current_state == BirthdayForm.year.state:
    await callback.message.answer(
        "2. Please provide the **Month**:", reply_markup=get_skip_keyboard()
    )
    await state.set_state(BirthdayForm.month)
  elif current_state == BirthdayForm.month.state:
    await callback.message.answer(
        "3. Please provide the **Date**:", reply_markup=get_skip_keyboard()
    )
    await state.set_state(BirthdayForm.date)
  elif current_state == BirthdayForm.date.state:
    await callback.message.answer(
        "4. Please provide the **Time**:", reply_markup=get_skip_keyboard()
    )
    await state.set_state(BirthdayForm.time)
  elif current_state == BirthdayForm.time.state:
    await callback.message.answer(
        "5. Please provide **AM or PM**:", reply_markup=get_skip_keyboard()
    )
    await state.set_state(BirthdayForm.am_pm)
  elif current_state == BirthdayForm.am_pm.state:
    await callback.message.answer(
        "6. Please send a **Photo**:", reply_markup=get_skip_keyboard()
    )
    await state.set_state(BirthdayForm.photo)
  elif current_state == BirthdayForm.photo.state:
    await callback.message.answer(
        "7. Please send a **Video**:", reply_markup=get_skip_keyboard()
    )
    await state.set_state(BirthdayForm.video)
  elif current_state == BirthdayForm.video.state:
    await callback.message.answer(
        "8. Please send a **Song**:", reply_markup=get_skip_keyboard()
    )
    await state.set_state(BirthdayForm.song)
  elif current_state == BirthdayForm.song.state:
    await callback.message.answer(
        "9. Please send a **Voice message**:", reply_markup=get_skip_keyboard()
    )
    await state.set_state(BirthdayForm.voice)
  elif current_state == BirthdayForm.voice.state:
    await callback.message.answer(
        "10. Please send an **Audio**:", reply_markup=get_skip_keyboard()
    )
    await state.set_state(BirthdayForm.audio)
  elif current_state == BirthdayForm.audio.state:
    await callback.message.answer("All information has been completed! Thank you! 🎉")
    await state.clear()

  await callback.answer("Skipped!")


# Message handlers for each state
@dp.message(BirthdayForm.year)
async def process_year(message: types.Message, state: FSMContext):
  await state.update_data(year=message.text)
  await message.answer(
      "2. Please provide the **Month**:", reply_markup=get_skip_keyboard()
  )
  await state.set_state(BirthdayForm.month)


@dp.message(BirthdayForm.month)
async def process_month(message: types.Message, state: FSMContext):
  await state.update_data(month=message.text)
  await message.answer(
      "3. Please provide the **Date**:", reply_markup=get_skip_keyboard()
  )
  await state.set_state(BirthdayForm.date)


@dp.message(BirthdayForm.date)
async def process_date(message: types.Message, state: FSMContext):
  await state.update_data(date=message.text)
  await message.answer(
      "4. Please provide the **Time**:", reply_markup=get_skip_keyboard()
  )
  await state.set_state(BirthdayForm.time)


@dp.message(BirthdayForm.time)
async def process_time(message: types.Message, state: FSMContext):
  await state.update_data(time=message.text)
  await message.answer(
      "5. Please provide **AM or PM**:", reply_markup=get_skip_keyboard()
  )
  await state.set_state(BirthdayForm.am_pm)


@dp.message(BirthdayForm.am_pm)
async def process_am_pm(message: types.Message, state: FSMContext):
  await state.update_data(am_pm=message.text)
  await message.answer(
      "6. Please send a **Photo**:", reply_markup=get_skip_keyboard()
  )
  await state.set_state(BirthdayForm.photo)


@dp.message(BirthdayForm.photo, F.photo)
async def process_photo(message: types.Message, state: FSMContext):
  await state.update_data(photo=message.photo[-1].file_id)
  await message.answer(
      "7. Please send a **Video**:", reply_markup=get_skip_keyboard()
  )
  await state.set_state(BirthdayForm.video)


@dp.message(BirthdayForm.video, F.video)
async def process_video(message: types.Message, state: FSMContext):
  await state.update_data(video=message.video.file_id)
  await message.answer(
      "8. Please send a **Song**:", reply_markup=get_skip_keyboard()
  )
  await state.set_state(BirthdayForm.song)


@dp.message(BirthdayForm.song)
async def process_song(message: types.Message, state: FSMContext):
  await state.update_data(song=message.text)
  await message.answer(
      "9. Please send a **Voice message**:", reply_markup=get_skip_keyboard()
  )
  await state.set_state(BirthdayForm.voice)


@dp.message(BirthdayForm.voice, F.voice)
async def process_voice(message: types.Message, state: FSMContext):
  await state.update_data(voice=message.voice.file_id)
  await message.answer(
      "10. Please send an **Audio**:", reply_markup=get_skip_keyboard()
  )
  await state.set_state(BirthdayForm.audio)


@dp.message(BirthdayForm.audio, F.audio)
async def process_audio(message: types.Message, state: FSMContext):
  await state.update_data(audio=message.audio.file_id)
  await message.answer("All information has been successfully saved! 🎉")
  await state.clear()


async def main():
  await dp.start_polling(bot)


if __name__ == "__main__":
  asyncio.run(main())
