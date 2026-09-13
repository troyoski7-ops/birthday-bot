import asyncio
import os
import sqlite3
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

# Owner ID (നിങ്ങൾക്ക് ഫ്രീ ആയി ഉപയോഗിക്കാനും /stats കാണാനും)
OWNER_ID = 1689374364

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Netlify Web App Link
NETLIFY_URL = "https://earnest-jelly-986463.netlify.app"


# Database Setup (SQLite)
def init_db():
  conn = sqlite3.connect("bot_stats.db")
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed INTEGER DEFAULT 0
        )
    """)
  conn.commit()
  conn.close()


init_db()


def record_start(user_id):
  conn = sqlite3.connect("bot_stats.db")
  cursor = conn.cursor()
  cursor.execute(
      "INSERT OR IGNORE INTO users (user_id, completed) VALUES (?, 0)",
      (user_id,),
  )
  conn.commit()
  conn.close()


def record_completion(user_id):
  conn = sqlite3.connect("bot_stats.db")
  cursor = conn.cursor()
  cursor.execute(
      "UPDATE users SET completed = 1 WHERE user_id = ?", (user_id,)
  )
  conn.commit()
  conn.close()


def get_stats():
  conn = sqlite3.connect("bot_stats.db")
  cursor = conn.cursor()
  cursor.execute("SELECT COUNT(*) FROM users")
  total_started = cursor.fetchone()[0]
  cursor.execute("SELECT COUNT(*) FROM users WHERE completed = 1")
  total_completed = cursor.fetchone()[0]
  conn.close()
  return total_started, total_completed


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
              InlineKeyboardButton(text="⏭️ Skip Step", callback_data="skip_step"),
              InlineKeyboardButton(text="✏️ Change / Back", callback_data="change_step"),
          ]
      ]
  )


# Year Selection Keyboard
def get_year_keyboard():
  return InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(text="2026", callback_data="set_year_2026"),
              InlineKeyboardButton(text="2027", callback_data="set_year_2027"),
          ],
          [InlineKeyboardButton(text="⏭️ Skip", callback_data="skip_step")],
      ]
  )


# Month Selection Keyboard
def get_month_keyboard():
  return InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(text="Jan", callback_data="set_month_Jan"),
              InlineKeyboardButton(text="Feb", callback_data="set_month_Feb"),
              InlineKeyboardButton(text="Mar", callback_data="set_month_Mar"),
          ],
          [
              InlineKeyboardButton(text="Apr", callback_data="set_month_Apr"),
              InlineKeyboardButton(text="May", callback_data="set_month_May"),
              InlineKeyboardButton(text="Jun", callback_data="set_month_Jun"),
          ],
          [
              InlineKeyboardButton(text="Jul", callback_data="set_month_Jul"),
              InlineKeyboardButton(text="Aug", callback_data="set_month_Aug"),
              InlineKeyboardButton(text="Sep", callback_data="set_month_Sep"),
          ],
          [
              InlineKeyboardButton(text="Oct", callback_data="set_month_Oct"),
              InlineKeyboardButton(text="Nov", callback_data="set_month_Nov"),
              InlineKeyboardButton(text="Dec", callback_data="set_month_Dec"),
          ],
          [InlineKeyboardButton(text="⏭️ Skip", callback_data="skip_step")],
      ]
  )


# AM / PM Keyboard
def get_ampm_keyboard():
  return InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(text="☀️ AM", callback_data="set_ampm_AM"),
              InlineKeyboardButton(text="🌙 PM", callback_data="set_ampm_PM"),
          ],
          [InlineKeyboardButton(text="⏭️ Skip", callback_data="skip_step")],
      ]
  )


# /stats command (Only for Owner)
@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
  if message.from_user.id == OWNER_ID:
    started, completed = get_stats()
    await message.answer(
        f"📊 **Bot Usage Statistics:**\n\n"
        f"👤 Total users who started the bot: **{started}**\n"
        f"🎉 Total birthday websites created: **{completed}**",
        parse_mode="Markdown",
    )
  else:
    await message.answer("⚠️ You are not authorized to use this command.")


# /start command with Welcome & Explanation (Luxury Theme)
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
  user_id = message.from_user.id
  record_start(user_id)

  welcome_text = (
      "✨ **WELCOME TO LUXURY BIRTHDAY SURPRISE BOT** ✨\n"
      "═══════════════════════════════\n"
      "🎂 Craft an unforgettable, time-locked & interactive digital birthday experience for your special someone.\n\n"
      "🌟 **Exclusive Features:**\n"
      " • Interactive Scratch Card & Cake Cutting 🕯️\n"
      " • Custom Photos, Videos, Songs & Voice Notes 🎶\n"
      " • Smart Time-Locked Countdown Portal ⏳\n"
      " • Instant Creator Preview & Universal Sharing 🚀\n"
      "═══════════════════════════════"
  )
  await message.answer(welcome_text, parse_mode="Markdown")

  # Owner ആണെങ്കിൽ payment ഇല്ലാതെ നേരിട്ട് തുടങ്ങാം
  if user_id == OWNER_ID:
    await message.answer(
        "👑 **Owner Privilege Activated:** Unlimited Free Access Granted!\n\n"
        "1️⃣ Please enter or send the **Recipient's Name**:",
        reply_markup=get_action_keyboard(),
    )
    await state.set_state(BirthdayForm.name)
  else:
    # സാധാരണ യൂസർമാർക്ക് Telegram Stars invoice കാണിക്കുന്നു (1 Star)
    await message.answer(
        "⭐ Unlock full access to create your luxury birthday surprise web app for just **1 Telegram Star**:"
    )
    await message.answer_invoice(
        title="Luxury Birthday Surprise Access",
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
  user_id = message.from_user.id
  record_start(user_id)
  await message.answer(
      "✅ **Payment Verified!** Welcome to your VIP creator studio.\n\n"
      "1️⃣ Please enter or send the **Recipient's Name**:",
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
    BirthdayForm.name: "1️⃣ Please enter the **Recipient's Name**:",
    BirthdayForm.wish: "2️⃣ Please write a heartfelt **Birthday Wish / Message**:",
    BirthdayForm.year: "3️⃣ Please select the **Year**:",
    BirthdayForm.month: "4️⃣ Please select the **Month**:",
    BirthdayForm.date: "5️⃣ Please enter the **Date** (e.g., 20):",
    BirthdayForm.time: (
        "6️⃣ Please enter the **Time** in format HH:MM (e.g., 06:30):"
    ),
    BirthdayForm.am_pm: "7️⃣ Please select **AM or PM**:",
    BirthdayForm.photo: "8️⃣ Please send a **Photo** (or Skip):",
    BirthdayForm.video: "9️⃣ Please send a **Video** (or Skip):",
    BirthdayForm.song: (
        "🔟 Please send a **Song / Audio file or link** (or Skip):"
    ),
    BirthdayForm.voice: "1️⃣1️⃣ Please send a **Voice Message** (or Skip):",
    BirthdayForm.audio: "1️⃣2️⃣ Please send an extra **Audio file** (or Skip):",
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

    # სპეციალური Inline Keyboards ഉള്ള സ്റ്റെപ്പുകൾ
    if next_state == BirthdayForm.year:
      await callback.message.answer(
          STATE_PROMPTS[next_state],
          reply_markup=get_year_keyboard(),
          parse_mode="Markdown",
      )
    elif next_state == BirthdayForm.month:
      await callback.message.answer(
          STATE_PROMPTS[next_state],
          reply_markup=get_month_keyboard(),
          parse_mode="Markdown",
      )
    elif next_state == BirthdayForm.am_pm:
      await callback.message.answer(
          STATE_PROMPTS[next_state],
          reply_markup=get_ampm_keyboard(),
          parse_mode="Markdown",
      )
    else:
      await callback.message.answer(
          STATE_PROMPTS[next_state],
          reply_markup=get_action_keyboard(),
          parse_mode="Markdown",
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
        f"↩️ Back to previous step:\n{STATE_PROMPTS[prev_state]}",
        reply_markup=get_action_keyboard(),
        parse_mode="Markdown",
    )
  else:
    await callback.message.answer(
        "This is the first step!", reply_markup=get_action_keyboard()
    )

  await callback.answer("Go back!")


# Inline Button Handlers for Year, Month, AM/PM
@dp.callback_query(F.data.startswith("set_year_"))
async def cb_set_year(callback: types.CallbackQuery, state: FSMContext):
  year_val = callback.data.split("_")[2]
  await state.update_data(year=year_val)
  await state.set_state(BirthdayForm.month)
  await callback.message.answer(
      f"Selected Year: **{year_val}**\n\n{STATE_PROMPTS[BirthdayForm.month]}",
      reply_markup=get_month_keyboard(),
      parse_mode="Markdown",
  )
  await callback.answer(f"Year {year_val} selected!")


@dp.callback_query(F.data.startswith("set_month_"))
async def cb_set_month(callback: types.CallbackQuery, state: FSMContext):
  month_val = callback.data.split("_")[2]
  await state.update_data(month=month_val)
  await state.set_state(BirthdayForm.date)
  await callback.message.answer(
      f"Selected Month: **{month_val}**\n\n{STATE_PROMPTS[BirthdayForm.date]}",
      reply_markup=get_action_keyboard(),
      parse_mode="Markdown",
  )
  await callback.answer(f"Month {month_val} selected!")


@dp.callback_query(F.data.startswith("set_ampm_"))
async def cb_set_ampm(callback: types.CallbackQuery, state: FSMContext):
  ampm_val = callback.data.split("_")[2]
  await state.update_data(am_pm=ampm_val)
  await state.set_state(BirthdayForm.photo)
  await callback.message.answer(
      f"Selected AM/PM: **{ampm_val}**\n\n{STATE_PROMPTS[BirthdayForm.photo]}",
      reply_markup=get_action_keyboard(),
      parse_mode="Markdown",
  )
  await callback.answer(f"{ampm_val} selected!")


async def get_telegram_file_url(bot: Bot, file_id: str) -> str:
  try:
    file = await bot.get_file(file_id)
    return f"https://api.telegram.org/file/bot{bot.token}/{file.file_path}"
  except Exception:
    return ""


async def finish_form(message: types.Message, state: FSMContext):
  user_id = message.from_user.id
  record_completion(user_id)

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

  # Target Time സെറ്റപ്പ് (24-hour conversion support or ISO format)
  if data.get("year") and data.get("date") and data.get("time"):
    year_val = data.get("year")
    date_val = str(data.get("date")).zfill(2)
    time_raw = str(data.get("time")).replace(".", ":")
    parts = time_raw.split(":")
    hour = int(parts[0]) if len(parts) > 0 else 12
    minute = parts[1] if len(parts) > 1 else "00"
    am_pm = str(data.get("am_pm", "")).upper()

    if am_pm == "PM" and hour < 12:
      hour += 12
    elif am_pm == "AM" and hour == 12:
      hour = 0

    time_val = f"{str(hour).zfill(2)}:{minute}"

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

  # 1. Preview URL (target_time ഒഴിവാക്കിയത് - അപ്പോൾ തന്നെ തുറക്കും)
  params_preview = params.copy()
  params_preview.pop("target_time", None)
  query_string_preview = urllib.parse.urlencode(params_preview)
  preview_url = (
      f"{NETLIFY_URL}/?{query_string_preview}"
      if query_string_preview
      else NETLIFY_URL
  )

  # 2. Final / Share URL (target_time ഉൾപ്പെടെ - കൗണ്ട്ഡൗൺ വർക്ക് ചെയ്യും)
  query_string_final = urllib.parse.urlencode(params)
  final_url = (
      f"{NETLIFY_URL}/?{query_string_final}" if query_string_final else NETLIFY_URL
  )

  # Universal Share URLs (Telegram, WhatsApp, General Share Text)
  share_text = urllib.parse.quote(
      f"🎉 Happy Birthday {data.get('name', 'Friend')}! Here is your special luxury surprise:"
  )
  telegram_share_url = f"https://t.me/share/url?url={urllib.parse.quote(final_url)}&text={share_text}"
  whatsapp_share_url = f"https://api.whatsapp.com/send?text={share_text}%20{urllib.parse.quote(final_url)}"

  preview_kb = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="👀 Preview Your Web App",
                  web_app=WebAppInfo(url=preview_url),
              ),
              InlineKeyboardButton(
                  text="🎂 My Birthday Surprise",
                  web_app=WebAppInfo(url=preview_url),
              ),
          ],
          [
              InlineKeyboardButton(
                  text="💬 Share via Telegram",
                  url=telegram_share_url,
              ),
              InlineKeyboardButton(
                  text="🟢 Share via WhatsApp",
                  url=whatsapp_share_url,
              ),
          ],
          [
              InlineKeyboardButton(
                  text="🔗 Copy & Share Link (All Social Media)",
                  url=final_url,
              )
          ],
      ]
  )

  recipient_name = data.get("name", "Friend")
  await message.answer(
      f"✨ **LUXURY SURPRISE READY FOR {recipient_name.upper()}!** ✨\n\n"
      "👇 Choose an option below:\n"
      "• **Preview / My Birthday Surprise**: Opens immediately without countdown.\n"
      "• **Share Options**: Scheduled countdown enabled for the birthday person!",
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
      STATE_PROMPTS[BirthdayForm.year],
      reply_markup=get_year_keyboard(),
      parse_mode="Markdown",
  )
  await state.set_state(BirthdayForm.year)


@dp.message(BirthdayForm.year)
async def process_year(message: types.Message, state: FSMContext):
  await state.update_data(year=message.text)
  await message.answer(
      STATE_PROMPTS[BirthdayForm.month],
      reply_markup=get_month_keyboard(),
      parse_mode="Markdown",
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
      STATE_PROMPTS[BirthdayForm.am_pm],
      reply_markup=get_ampm_keyboard(),
      parse_mode="Markdown",
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
