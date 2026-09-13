import asyncio
import os
import urllib.parse
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LabeledPrice,
    WebAppInfo,
)
from aiohttp import web

# Telegram Bot Token
API_TOKEN = "8854916574:AAEgxWmPyP4OPNSsLfsBbXXFu5W6LiFcq0o"

# Owner ID (നിങ്ങൾക്ക് ഫ്രീ ആയി ഉപയോഗിക്കാൻ)
OWNER_ID = 1689374364

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Netlify Web App Link
NETLIFY_URL = "https://earnest-jelly-986463.netlify.app"


# Define states
class BirthdayForm(StatesGroup):
  name = State()
  wish = State()
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


# Helper keyboard with Skip and Change options
def get_action_keyboard():
  return InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(text="⏭️ Skip", callback_data="skip_step"),
              InlineKeyboardButton(text="✏️ Change / Back", callback_data="change_step"),
          ]
      ]
  )


# /start command with Welcome & Explanation
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
  user_id = message.from_user.id

  welcome_text = (
      "👋 **Welcome to Birthday Surprise Bot!** 🎉\n\n"
      "Create a special, luxury birthday surprise web app for your loved ones.\n\n"
      "🔸 **How to use:**\n"
      "1. Provide Name, Wish, Date, Time, Photo, Video, Song, and Voice message.\n"
      "2. Use **Skip** for optional steps or **Change / Back** to fix mistakes.\n"
      "3. Once finished, get instant preview and direct sharing options!\n"
  )
  await message.answer(welcome_text, parse_mode="Markdown")

  # Owner ആണെങ്കിൽ payment ഇല്ലാതെ നേരിട്ട് തുടങ്ങാം
  if user_id == OWNER_ID:
    await message.answer(
        "👑 **Owner Mode Active:** Free unlimited access granted!\n\n"
        "1. Please provide the **Name**:",
        reply_markup=get_action_keyboard(),
    )
    await state.set_state(BirthdayForm.name)
  else:
    # സാധാരണ യൂസർമാർക്ക് Telegram Stars invoice കാണിക്കുന്നു (1 Star)
    await message.answer(
        "⭐ Please unlock full access by paying with Telegram Stars (1 Star)"
        " below:"
    )
    await message.answer_invoice(
        title="Birthday Surprise Bot Access",
        description=(
            "Unlock full access to create custom birthday surprise web apps."
        ),
        payload="birthday_bot_stars_access",
        currency="XTR",  # Telegram Stars currency code
        prices=[LabeledPrice(label="Access Fee", amount=1)],  # 1 Star
    )


# Pre-checkout query handler for Telegram Stars
@dp.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
  await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


# Successful payment handler -> Start form for normal users
@dp.message(F.successful_payment)
async def process_successful_payment(message: types.Message, state: FSMContext):
  await message.answer(
      "✅ **Payment Successful!** Thank you.\n"
      "Now let's build your birthday surprise step by step.\n\n"
      "1. Please provide the **Name**:",
      reply_markup=get_action_keyboard(),
  )
  await state.set_state(BirthdayForm.name)


# State order list for navigation (Change/Skip)
STATE_SEQUENCE = [
    BirthdayForm.name,
    BirthdayForm.wish,
    BirthdayForm.year,
    BirthdayForm.month,
    BirthdayForm.date,
    BirthdayForm.time,
    BirthdayForm.am_pm,
    BirthdayForm.photo,
    BirthdayForm.video,
    BirthdayForm.song,
    BirthdayForm.voice,
    BirthdayForm.audio,
]

STATE_PROMPTS = {
    BirthdayForm.name: "1. Please provide the **Name**:",
    BirthdayForm.wish: "2. Please provide the **Birthday Wish / Message**:",
    BirthdayForm.year: "3. Please provide the **Year** (e.g., 2026):",
    BirthdayForm.month: "4. Please provide the **Month** (e.g., May or 05):",
    BirthdayForm.date: "5. Please provide the **Date** (e.g., 20):",
    BirthdayForm.time: "6. Please provide the **Time** (e.g., 12:00):",
    BirthdayForm.am_pm: "7. Please provide **AM or PM**:",
    BirthdayForm.photo: "8. Please send a **Photo**:",
    BirthdayForm.video: "9. Please send a **Video**:",
    BirthdayForm.song: "10. Please send a **Song**:",
    BirthdayForm.voice: "11. Please send a **Voice message**:",
    BirthdayForm.audio: "12. Please send an **Audio**:",
}


@dp.callback_query(F.data == "skip_step")
async def process_skip(callback: types.CallbackQuery, state: FSMContext):
  current_state = await state.get_state()
  current_idx = -1
  for idx, s in enumerate(STATE_SEQUENCE):
    if s.state == current_state:
      current_idx = idx
      break

  if current_idx != -1 and current_idx + 1 < len(STATE_SEQUENCE):
    next_state = STATE_SEQUENCE[current_idx + 1]
    await state.set_state(next_state)
    await callback.message.answer(
        STATE_PROMPTS[next_state], reply_markup=get_action_keyboard()
    )
  else:
    await finish_form(callback.message, state)

  await callback.answer("Skipped!")


@dp.callback_query(F.data == "change_step")
async def process_change(callback: types.CallbackQuery, state: FSMContext):
  current_state = await state.get_state()
  current_idx = -1
  for idx, s in enumerate(STATE_SEQUENCE):
    if s.state == current_state:
      current_idx = idx
      break

  if current_idx > 0:
    prev_state = STATE_SEQUENCE[current_idx - 1]
    await state.set_state(prev_state)
    await callback.message.answer(
        f"Go back to previous step:\n{STATE_PROMPTS[prev_state]}",
        reply_markup=get_action_keyboard(),
    )
  else:
    await callback.message.answer(
        "This is the first step!", reply_markup=get_action_keyboard()
    )

  await callback.answer("Go back!")


async def get_telegram_file_url(bot: Bot, file_id: str) -> str:
  try:
    file = await bot.get_file(file_id)
    return f"https://api.telegram.org/file/bot{bot.token}/{file.file_path}"
  except Exception:
    return ""


async def finish_form(message: types.Message, state: FSMContext):
  data = await state.get_data()

  params = {}
  if data.get("name"):
    params["name"] = data.get("name")
  if data.get("wish"):
    params["msg"] = data.get("wish")
  if data.get("year"):
    params["year"] = data.get("year")
  if data.get("month"):
    params["month"] = data.get("month")
  if data.get("date"):
    params["date"] = data.get("date")
  if data.get("time"):
    params["time"] = data.get("time")
  if data.get("am_pm"):
    params["am_pm"] = data.get("am_pm")

  # Target Time സെറ്റപ്പ്
  if data.get("year") and data.get("date") and data.get("time"):
    year_val = data.get("year")
    date_val = data.get("date").zfill(2)
    time_val = data.get("time")
    month_map = {
        "Jan": "01",
        "Feb": "02",
        "Mar": "03",
        "Apr": "04",
        "May": "05",
        "Jun": "06",
        "Jul": "07",
        "Aug": "08",
        "Sep": "09",
        "Oct": "10",
        "Nov": "11",
        "Dec": "12",
    }
    m_raw = str(data.get("month", "01"))
    month_val = month_map.get(m_raw[:3].capitalize(), m_raw.zfill(2))
    params["target_time"] = f"{year_val}-{month_val}-{date_val}T{time_val}:00"

  # Media URLs convert ചെയ്യുന്നു
  if data.get("photo"):
    url = await get_telegram_file_url(bot, data.get("photo"))
    if url:
      params["photo"] = url
  if data.get("video"):
    url = await get_telegram_file_url(bot, data.get("video"))
    if url:
      params["video"] = url
  if data.get("voice"):
    url = await get_telegram_file_url(bot, data.get("voice"))
    if url:
      params["voice"] = url
  if data.get("audio"):
    url = await get_telegram_file_url(bot, data.get("audio"))
    if url:
      params["song"] = url
  elif data.get("song"):
    params["song"] = data.get("song")

  query_string = urllib.parse.urlencode(params)
  final_url = (
      f"{NETLIFY_URL}/?{query_string}" if query_string else NETLIFY_URL
  )

  # Telegram Share URL ഉണ്ടാക്കുന്നു
  share_text = urllib.parse.quote(
      f"🎉 Happy Birthday {data.get('name', 'Friend')}! Here is your special surprise:"
  )
  share_url = f"https://t.me/share/url?url={urllib.parse.quote(final_url)}&text={share_text}"

  preview_kb = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="👀 Preview Your Web App",
                  web_app=WebAppInfo(url=final_url),
              )
          ],
          [
              InlineKeyboardButton(
                  text="🎉 Open Birthday Surprise",
                  web_app=WebAppInfo(url=final_url),
              )
          ],
          [
              InlineKeyboardButton(
                  text="📤 Share with Birthday Person",
                  url=share_url,
              )
          ],
      ]
  )

  recipient_name = data.get("name", "Friend")
  await message.answer(
      f"✨ All information has been saved for **{recipient_name}**!\n"
      "Use the buttons below to preview, open, or directly share the surprise link:",
      reply_markup=preview_kb,
      parse_mode="Markdown",
  )

  await state.clear()


# Message handlers for each state
@dp.message(BirthdayForm.name)
async def process_name(message: types.Message, state: FSMContext):
  await state.update_data(name=message.text)
  await message.answer(
      STATE_PROMPTS[BirthdayForm.wish], reply_markup=get_action_keyboard()
  )
  await state.set_state(BirthdayForm.wish)


@dp.message(BirthdayForm.wish)
async def process_wish(message: types.Message, state: FSMContext):
  await state.update_data(wish=message.text)
  await message.answer(
      STATE_PROMPTS[BirthdayForm.year], reply_markup=get_action_keyboard()
  )
  await state.set_state(BirthdayForm.year)


@dp.message(BirthdayForm.year)
async def process_year(message: types.Message, state: FSMContext):
  await state.update_data(year=message.text)
  await message.answer(
      STATE_PROMPTS[BirthdayForm.month], reply_markup=get_action_keyboard()
  )
  await state.set_state(BirthdayForm.month)


@dp.message(BirthdayForm.month)
async def process_month(message: types.Message, state: FSMContext):
  await state.update_data(month=message.text)
  await message.answer(
      STATE_PROMPTS[BirthdayForm.date], reply_markup=get_action_keyboard()
  )
  await state.set_state(BirthdayForm.date)


@dp.message(BirthdayForm.date)
async def process_date(message: types.Message, state: FSMContext):
  await state.update_data(date=message.text)
  await message.answer(
      STATE_PROMPTS[BirthdayForm.time], reply_markup=get_action_keyboard()
  )
  await state.set_state(BirthdayForm.time)


@dp.message(BirthdayForm.time)
async def process_time(message: types.Message, state: FSMContext):
  await state.update_data(time=message.text)
  await message.answer(
      STATE_PROMPTS[BirthdayForm.am_pm], reply_markup=get_action_keyboard()
  )
  await state.set_state(BirthdayForm.am_pm)


@dp.message(BirthdayForm.am_pm)
async def process_am_pm(message: types.Message, state: FSMContext):
  await state.update_data(am_pm=message.text)
  await message.answer(
      STATE_PROMPTS[BirthdayForm.photo], reply_markup=get_action_keyboard()
  )
  await state.set_state(BirthdayForm.photo)


@dp.message(BirthdayForm.photo, F.photo)
async def process_photo(message: types.Message, state: FSMContext):
  await state.update_data(photo=message.photo[-1].file_id)
  await message.answer(
      STATE_PROMPTS[BirthdayForm.video], reply_markup=get_action_keyboard()
  )
  await state.set_state(BirthdayForm.video)


@dp.message(BirthdayForm.video, F.video)
async def process_video(message: types.Message, state: FSMContext):
  await state.update_data(video=message.video.file_id)
  await message.answer(
      STATE_PROMPTS[BirthdayForm.song], reply_markup=get_action_keyboard()
  )
  await state.set_state(BirthdayForm.song)


@dp.message(BirthdayForm.song)
async def process_song(message: types.Message, state: FSMContext):
  await state.update_data(song=message.text)
  await message.answer(
      STATE_PROMPTS[BirthdayForm.voice], reply_markup=get_action_keyboard()
  )
  await state.set_state(BirthdayForm.voice)


@dp.message(BirthdayForm.voice, F.voice)
async def process_voice(message: types.Message, state: FSMContext):
  await state.update_data(voice=message.voice.file_id)
  await message.answer(
      STATE_PROMPTS[BirthdayForm.audio], reply_markup=get_action_keyboard()
  )
  await state.set_state(BirthdayForm.audio)


@dp.message(BirthdayForm.audio, F.audio)
async def process_audio(message: types.Message, state: FSMContext):
  await state.update_data(audio=message.audio.file_id)
  await finish_form(message, state)


# Render Web Service-ന് വേണ്ടിയുള്ള ചെറിയ Dummy Web Server
async def handle(request):
  return web.Response(text="Bot is running!")


async def web_server():
  app = web.Application()
  app.router.add_get("/", handle)
  runner = web.AppRunner(app)
  await runner.setup()
  port = int(os.environ.get("PORT", 8080))
  site = web.TCPSite(runner, "0.0.0.0", port)
  await site.start()


async def main():
  await asyncio.gather(web_server(), dp.start_polling(bot))


if __name__ == "__main__":
  asyncio.run(main())
