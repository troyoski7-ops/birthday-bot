import asyncio
import json
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

# എത്ര എണ്ണം ഫ്രീ ആയി വേണം എന്ന് ഇവിടെ സെറ്റ് ചെയ്യാം (5 എണ്ണം)
FREE_LIMIT = 5

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
            completed INTEGER DEFAULT 0,
            creations_count INTEGER DEFAULT 0
        )
    """)
  # Long wish ഉം ഡിലീറ്റ് ഓപ്ഷനും സപ്പോർട്ട് ചെയ്യാൻ surprises table
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS surprises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            recipient_name TEXT,
            wish_text TEXT,
            params_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
  conn.commit()
  conn.close()


init_db()


def record_start(user_id):
  conn = sqlite3.connect("bot_stats.db")
  cursor = conn.cursor()
  cursor.execute(
      "INSERT OR IGNORE INTO users (user_id, completed, creations_count)"
      " VALUES (?, 0, 0)",
      (user_id,),
  )
  conn.commit()
  conn.close()


def get_user_creations(user_id):
  conn = sqlite3.connect("bot_stats.db")
  cursor = conn.cursor()
  cursor.execute(
      "SELECT creations_count FROM users WHERE user_id = ?", (user_id,)
  )
  row = cursor.fetchone()
  conn.close()
  return row[0] if row else 0


def increment_user_creation(user_id):
  conn = sqlite3.connect("bot_stats.db")
  cursor = conn.cursor()
  cursor.execute(
      """
        INSERT INTO users (user_id, completed, creations_count) VALUES (?, 1, 1)
        ON CONFLICT(user_id) DO UPDATE SET 
            completed = 1,
            creations_count = creations_count + 1
    """,
      (user_id,),
  )
  conn.commit()
  conn.close()


def save_surprise_to_db(user_id, recipient_name, wish_text, params_dict):
  conn = sqlite3.connect("bot_stats.db")
  cursor = conn.cursor()
  cursor.execute(
      """
        INSERT INTO surprises (user_id, recipient_name, wish_text, params_json)
        VALUES (?, ?, ?, ?)
    """,
      (user_id, recipient_name, wish_text, json.dumps(params_dict)),
  )
  conn.commit()
  surprise_id = cursor.lastrowid
  conn.close()
  return surprise_id


def get_stats():
  conn = sqlite3.connect("bot_stats.db")
  cursor = conn.cursor()
  cursor.execute("SELECT COUNT(*) FROM users")
  total_started = cursor.fetchone()[0]
  cursor.execute("SELECT SUM(creations_count) FROM users")
  row = cursor.fetchone()
  total_completed = row[0] if row and row[0] else 0
  conn.close()
  return total_started, total_completed


# Define states
class BirthdayForm(StatesGroup):
  name = State()
  wish = State()
  year = State()
  month = State()
  date = State()
  hour = State()
  minute = State()
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
              InlineKeyboardButton(text="✨ Skip", callback_data="skip_step"),
              InlineKeyboardButton(text="↩️ Change", callback_data="change_step"),
          ]
      ]
  )


# Year Selection Keyboard with Skip and Change
def get_year_keyboard():
  return InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(text="2026", callback_data="set_year_2026"),
              InlineKeyboardButton(text="2027", callback_data="set_year_2027"),
          ],
          [
              InlineKeyboardButton(text="✨ Skip", callback_data="skip_step"),
              InlineKeyboardButton(text="↩️ Change", callback_data="change_step"),
          ],
      ]
  )


# Month Selection Keyboard with Skip and Change
def get_month_keyboard():
  return InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(text="January", callback_data="set_month_Jan"),
              InlineKeyboardButton(text="February", callback_data="set_month_Feb"),
              InlineKeyboardButton(text="March", callback_data="set_month_Mar"),
          ],
          [
              InlineKeyboardButton(text="April", callback_data="set_month_Apr"),
              InlineKeyboardButton(text="May", callback_data="set_month_May"),
              InlineKeyboardButton(text="June", callback_data="set_month_Jun"),
          ],
          [
              InlineKeyboardButton(text="July", callback_data="set_month_Jul"),
              InlineKeyboardButton(text="August", callback_data="set_month_Aug"),
              InlineKeyboardButton(text="September", callback_data="set_month_Sep"),
          ],
          [
              InlineKeyboardButton(text="October", callback_data="set_month_Oct"),
              InlineKeyboardButton(text="November", callback_data="set_month_Nov"),
              InlineKeyboardButton(text="December", callback_data="set_month_Dec"),
          ],
          [
              InlineKeyboardButton(text="✨ Skip", callback_data="skip_step"),
              InlineKeyboardButton(text="↩️ Change", callback_data="change_step"),
          ],
      ]
  )


# Date Selection Keyboard (1 to 31) with Skip and Change
def get_date_keyboard():
  buttons = []
  row = []
  for i in range(1, 32):
    row.append(
        InlineKeyboardButton(
            text=str(i), callback_data=f"set_date_{str(i).zfill(2)}"
        )
    )
    if len(row) == 7:
      buttons.append(row)
      row = []
  if row:
    buttons.append(row)
  buttons.append([
      InlineKeyboardButton(text="✨ Skip", callback_data="skip_step"),
      InlineKeyboardButton(text="↩️ Change", callback_data="change_step"),
  ])
  return InlineKeyboardMarkup(inline_keyboard=buttons)


# 24-Hour Selection Keyboard (00 to 23) with Skip and Change
def get_hour_keyboard():
  return InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(text="00", callback_data="set_hour_00"),
              InlineKeyboardButton(text="01", callback_data="set_hour_01"),
              InlineKeyboardButton(text="02", callback_data="set_hour_02"),
              InlineKeyboardButton(text="03", callback_data="set_hour_03"),
              InlineKeyboardButton(text="04", callback_data="set_hour_04"),
              InlineKeyboardButton(text="05", callback_data="set_hour_05"),
          ],
          [
              InlineKeyboardButton(text="06", callback_data="set_hour_06"),
              InlineKeyboardButton(text="07", callback_data="set_hour_07"),
              InlineKeyboardButton(text="08", callback_data="set_hour_08"),
              InlineKeyboardButton(text="09", callback_data="set_hour_09"),
              InlineKeyboardButton(text="10", callback_data="set_hour_10"),
              InlineKeyboardButton(text="11", callback_data="set_hour_11"),
          ],
          [
              InlineKeyboardButton(text="12", callback_data="set_hour_12"),
              InlineKeyboardButton(text="13", callback_data="set_hour_13"),
              InlineKeyboardButton(text="14", callback_data="set_hour_14"),
              InlineKeyboardButton(text="15", callback_data="set_hour_15"),
              InlineKeyboardButton(text="16", callback_data="set_hour_16"),
              InlineKeyboardButton(text="17", callback_data="set_hour_17"),
          ],
          [
              InlineKeyboardButton(text="18", callback_data="set_hour_18"),
              InlineKeyboardButton(text="19", callback_data="set_hour_19"),
              InlineKeyboardButton(text="20", callback_data="set_hour_20"),
              InlineKeyboardButton(text="21", callback_data="set_hour_21"),
              InlineKeyboardButton(text="22", callback_data="set_hour_22"),
              InlineKeyboardButton(text="23", callback_data="set_hour_23"),
          ],
          [
              InlineKeyboardButton(text="✨ Skip", callback_data="skip_step"),
              InlineKeyboardButton(text="↩️ Change", callback_data="change_step"),
          ],
      ]
  )


# Minute Selection Keyboard (Quick buttons + Skip/Change)
def get_minute_keyboard():
  return InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(text="00", callback_data="set_min_00"),
              InlineKeyboardButton(text="10", callback_data="set_min_10"),
              InlineKeyboardButton(text="14", callback_data="set_min_14"),
              InlineKeyboardButton(text="15", callback_data="set_min_15"),
              InlineKeyboardButton(text="20", callback_data="set_min_20"),
          ],
          [
              InlineKeyboardButton(text="25", callback_data="set_min_25"),
              InlineKeyboardButton(text="30", callback_data="set_min_30"),
              InlineKeyboardButton(text="35", callback_data="set_min_35"),
              InlineKeyboardButton(text="40", callback_data="set_min_40"),
              InlineKeyboardButton(text="45", callback_data="set_min_45"),
          ],
          [
              InlineKeyboardButton(text="50", callback_data="set_min_50"),
              InlineKeyboardButton(text="55", callback_data="set_min_55"),
          ],
          [
              InlineKeyboardButton(text="✨ Skip", callback_data="skip_step"),
              InlineKeyboardButton(text="↩️ Change", callback_data="change_step"),
          ],
      ]
  )


# /stats command (Only for Owner)
@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
  if message.from_user.id == OWNER_ID:
    started, completed = get_stats()
    await message.answer(
        f"📊 Bot Usage Statistics:\n\n"
        f"• Total users who started: {started}\n"
        f"• Total surprises created: {completed}"
    )
  else:
    await message.answer("⚠️ You are not authorized to use this command.")


# /start command
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
  user_id = message.from_user.id
  record_start(user_id)

  creations = get_user_creations(user_id)

  welcome_text = (
      "✨ Welcome to your little corner of surprises...\n\n"
      "Let's craft a timeless, heartfelt digital birthday wish filled with sweet memories, music, and love. 🤍"
  )
  await message.answer(welcome_text)

  # Owner ആണെങ്കിൽ Unlimited Free Access
  if user_id == OWNER_ID:
    await message.answer(
        "🤍 **Owner Mode Active!** You have unlimited free creations.\n\nWhose"
        " birthday are we celebrating today? Send me their name:",
        reply_markup=get_action_keyboard(),
        parse_mode="Markdown",
    )
    await state.set_state(BirthdayForm.name)
  elif creations < FREE_LIMIT:
    remaining_free = FREE_LIMIT - creations
    if creations > 0:
      await message.answer(
          f"🎁 You have **{remaining_free}** free birthday surprise(s)"
          " remaining!\n\nWhose birthday are we celebrating today? Send me"
          " their name:",
          reply_markup=get_action_keyboard(),
          parse_mode="Markdown",
      )
    else:
      await message.answer(
          f"🎁 Your first **{FREE_LIMIT}** birthday surprises are"
          " **FREE**!\n\nWhose birthday are we celebrating today? Send me"
          " their name:",
          reply_markup=get_action_keyboard(),
          parse_mode="Markdown",
      )
    await state.set_state(BirthdayForm.name)
  else:
    await message.answer(
        "⭐ You have used all your 5 free birthday surprises!\n"
        "Please unlock full access for the next creation with **1 Telegram"
        " Star**:",
        parse_mode="Markdown",
    )
    await message.answer_invoice(
        title="Birthday Surprise Creator",
        description="Create a custom, time-locked luxury birthday web app.",
        payload="birthday_bot_stars_access",
        currency="XTR",
        prices=[LabeledPrice(label="Access Fee", amount=1)],
    )


@dp.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
  await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message(F.successful_payment)
async def process_successful_payment(message: types.Message, state: FSMContext):
  user_id = message.from_user.id
  record_start(user_id)
  await message.answer(
      "🤍 Thank you! Your payment is verified. Whose birthday are we"
      " celebrating today? Send me their name:",
      reply_markup=get_action_keyboard(),
  )
  await state.set_state(BirthdayForm.name)


STATE_SEQUENCE = [
    BirthdayForm.name,
    BirthdayForm.wish,
    BirthdayForm.year,
    BirthdayForm.month,
    BirthdayForm.date,
    BirthdayForm.hour,
    BirthdayForm.minute,
    BirthdayForm.photo,
    BirthdayForm.video,
    BirthdayForm.song,
    BirthdayForm.voice,
    BirthdayForm.audio,
]

STATE_PROMPTS = {
    BirthdayForm.name: (
        "Whose birthday are we celebrating today? Send me their name:"
    ),
    BirthdayForm.wish: (
        "Write a sweet, heartfelt birthday wish or message for them (Long paragraphs supported!):"
    ),
    BirthdayForm.year: "Choose the year for the surprise:",
    BirthdayForm.month: "Choose the month:",
    BirthdayForm.date: "Pick the date:",
    BirthdayForm.hour: "Select the Hour (24-Hour format, 00 to 23):",
    BirthdayForm.minute: (
        "Select the Minute (tap button below OR type any number from 00 to"
        " 59):"
    ),
    BirthdayForm.photo: "Share a lovely photo to cherish (or skip):",
    BirthdayForm.video: "Share a special video moment (or skip):",
    BirthdayForm.song: "Send a favorite song or audio file (or skip):",
    BirthdayForm.voice: (
        "Send a warm voice note to make it extra special (or skip):"
    ),
    BirthdayForm.audio: "Add one more audio file if you'd like (or skip):",
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

    if next_state == BirthdayForm.year:
      await callback.message.answer(
          STATE_PROMPTS[next_state],
          reply_markup=get_year_keyboard(),
      )
    elif next_state == BirthdayForm.month:
      await callback.message.answer(
          STATE_PROMPTS[next_state],
          reply_markup=get_month_keyboard(),
      )
    elif next_state == BirthdayForm.date:
      await callback.message.answer(
          STATE_PROMPTS[next_state],
          reply_markup=get_date_keyboard(),
      )
    elif next_state == BirthdayForm.hour:
      await callback.message.answer(
          STATE_PROMPTS[next_state],
          reply_markup=get_hour_keyboard(),
      )
    elif next_state == BirthdayForm.minute:
      await callback.message.answer(
          STATE_PROMPTS[next_state],
          reply_markup=get_minute_keyboard(),
      )
    else:
      await callback.message.answer(
          STATE_PROMPTS[next_state],
          reply_markup=get_action_keyboard(),
      )
  else:
    await finish_form(callback.message, state)

  await callback.answer("Skipped")


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

    if prev_state == BirthdayForm.year:
      kb = get_year_keyboard()
    elif prev_state == BirthdayForm.month:
      kb = get_month_keyboard()
    elif prev_state == BirthdayForm.date:
      kb = get_date_keyboard()
    elif prev_state == BirthdayForm.hour:
      kb = get_hour_keyboard()
    elif prev_state == BirthdayForm.minute:
      kb = get_minute_keyboard()
    else:
      kb = get_action_keyboard()

    await callback.message.answer(
        f"Let's step back:\n{STATE_PROMPTS[prev_state]}",
        reply_markup=kb,
    )
  else:
    await callback.message.answer(
        "We are at the very beginning!", reply_markup=get_action_keyboard()
    )

  await callback.answer("Going back")


@dp.callback_query(F.data.startswith("set_year_"))
async def cb_set_year(callback: types.CallbackQuery, state: FSMContext):
  year_val = callback.data.split("_")[2]
  await state.update_data(year=year_val)
  await state.set_state(BirthdayForm.month)
  await callback.message.answer(
      f"Year: {year_val}\n\n{STATE_PROMPTS[BirthdayForm.month]}",
      reply_markup=get_month_keyboard(),
  )
  await callback.answer(f"{year_val} chosen")


@dp.callback_query(F.data.startswith("set_month_"))
async def cb_set_month(callback: types.CallbackQuery, state: FSMContext):
  month_val = callback.data.split("_")[2]
  await state.update_data(month=month_val)
  await state.set_state(BirthdayForm.date)
  await callback.message.answer(
      f"Month: {month_val}\n\n{STATE_PROMPTS[BirthdayForm.date]}",
      reply_markup=get_date_keyboard(),
  )
  await callback.answer(f"{month_val} chosen")


@dp.callback_query(F.data.startswith("set_date_"))
async def cb_set_date(callback: types.CallbackQuery, state: FSMContext):
  date_val = callback.data.split("_")[2]
  await state.update_data(date=date_val)
  await state.set_state(BirthdayForm.hour)
  await callback.message.answer(
      f"Date: {date_val}\n\n{STATE_PROMPTS[BirthdayForm.hour]}",
      reply_markup=get_hour_keyboard(),
  )
  await callback.answer(f"Date {date_val} chosen")


@dp.callback_query(F.data.startswith("set_hour_"))
async def cb_set_hour(callback: types.CallbackQuery, state: FSMContext):
  hour_val = callback.data.split("_")[2]
  await state.update_data(hour=hour_val)
  await state.set_state(BirthdayForm.minute)
  await callback.message.answer(
      f"Hour: {hour_val}\n\n{STATE_PROMPTS[BirthdayForm.minute]}",
      reply_markup=get_minute_keyboard(),
  )
  await callback.answer(f"Hour {hour_val} chosen")


@dp.callback_query(F.data.startswith("set_min_"))
async def cb_set_min(callback: types.CallbackQuery, state: FSMContext):
  min_val = callback.data.split("_")[2]
  await state.update_data(minute=min_val)
  await state.set_state(BirthdayForm.photo)
  await callback.message.answer(
      f"Minute: {min_val}\n\n{STATE_PROMPTS[BirthdayForm.photo]}",
      reply_markup=get_action_keyboard(),
  )
  await callback.answer(f"Minute {min_val} chosen")


# Direct text input handler for custom minute (e.g. typing "14" or "42")
@dp.message(BirthdayForm.minute)
async def process_custom_minute(message: types.Message, state: FSMContext):
  min_text = message.text.strip().zfill(2)
  await state.update_data(minute=min_text)
  await state.set_state(BirthdayForm.photo)
  await message.answer(
      f"Minute: {min_text}\n\n{STATE_PROMPTS[BirthdayForm.photo]}",
      reply_markup=get_action_keyboard(),
  )


async def get_telegram_file_url(bot: Bot, file_id: str) -> str:
  try:
    file = await bot.get_file(file_id)
    return f"https://api.telegram.org/file/bot{bot.token}/{file.file_path}"
  except Exception:
    return ""


async def finish_form(message: types.Message, state: FSMContext):
  user_id = message.from_user.id
  if user_id != OWNER_ID:
    increment_user_creation(user_id)

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
  if data.get("hour") and data.get("minute"):
    time_str = f"{data.get('hour')}:{data.get('minute')}"
    params["time"] = time_str

  if (
      data.get("year")
      and data.get("date")
      and data.get("hour")
      and data.get("minute")
  ):
    year_val = data.get("year")
    date_val = str(data.get("date")).zfill(2)
    hour_val = str(data.get("hour")).zfill(2)
    min_val = str(data.get("minute")).zfill(2)

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
    params["target_time"] = f"{year_val}-{month_val}-{date_val}T{hour_val}:{min_val}:00"

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
    song_val = data.get("song")
    if not str(song_val).startswith("http"):
      url = await get_telegram_file_url(bot, str(song_val))
      if url:
        params["song"] = url
    else:
      params["song"] = song_val

  # സർപ്രൈസ് SQLite-ൽ സേവ് ചെയ്യുന്നു (Long wish-നുള്ള ഐഡി ജനറേറ്റ് ചെയ്യാൻ)
  surprise_id = save_surprise_to_db(
      user_id=user_id,
      recipient_name=data.get("name", "Friend"),
      wish_text=data.get("wish", ""),
      params_dict=params,
  )

  params_preview = params.copy()
  params_preview.pop("target_time", None)
  # ID കൂടി പാസ് ചെയ്യുന്നു જેથી ലോങ്ങ് wish ആണെങ്കിലും query + id സപ്പോർട്ട് ചെയ്യും
  params_preview["id"] = surprise_id
  query_string_preview = urllib.parse.urlencode(params_preview)
  preview_url = (
      f"{NETLIFY_URL}/?{query_string_preview}"
      if query_string_preview
      else NETLIFY_URL
  )

  params["id"] = surprise_id
  query_string_final = urllib.parse.urlencode(params)
  final_url = (
      f"{NETLIFY_URL}/?{query_string_final}" if query_string_final else NETLIFY_URL
  )

  share_text = urllib.parse.quote(
      f"✨ Happy Birthday {data.get('name', 'Dear')}! I made a little surprise just for you:"
  )
  telegram_share_url = f"https://t.me/share/url?url={urllib.parse.quote(final_url)}&text={share_text}"
  whatsapp_share_url = f"https://api.whatsapp.com/send?text={share_text}%20{urllib.parse.quote(final_url)}"

  preview_kb = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="🤍 Preview Surprise",
                  web_app=WebAppInfo(url=preview_url),
              ),
              InlineKeyboardButton(
                  text="🎂 My Birthday View",
                  web_app=WebAppInfo(url=preview_url),
              ),
          ],
          [
              InlineKeyboardButton(
                  text="💬 Share on Telegram",
                  url=telegram_share_url,
              ),
              InlineKeyboardButton(
                  text="🟢 Share on WhatsApp",
                  url=whatsapp_share_url,
              ),
          ],
          [
              InlineKeyboardButton(
                  text="🔗 Copy Link (All Apps)",
                  url=final_url,
              )
          ],
          [
              # ക്രിയേറ്റർക്കോ ഓണർക്കോ മാത്രം ഡിലീറ്റ് ചെയ്യാൻ ഉള്ള ബട്ടൺ
              InlineKeyboardButton(
                  text="🗑️ Delete this Surprise",
                  callback_data=f"del_surprise_{surprise_id}",
              )
          ],
      ]
  )

  recipient_name = data.get("name", "Friend")
  await message.answer(
      f"✨ All ready for {recipient_name}!\n\n"
      "Choose how you'd like to experience or share your creation below:",
      reply_markup=preview_kb,
  )

  await state.clear()


# Delete Surprise Callback Handler (Owner or Creator only)
@dp.callback_query(F.data.startswith("del_surprise_"))
async def delete_surprise_callback(callback: types.CallbackQuery):
  try:
    surprise_id = int(callback.data.split("_")[2])
  except Exception:
    await callback.answer("❌ Invalid ID", show_alert=True)
    return

  conn = sqlite3.connect("bot_stats.db")
  cursor = conn.cursor()
  cursor.execute(
      "SELECT user_id FROM surprises WHERE id = ?", (surprise_id,)
  )
  row = cursor.fetchone()

  if not row:
    conn.close()
    await callback.answer(
        "❌ Surprise not found or already deleted!", show_alert=True
    )
    return

  creator_id = row[0]
  user_id = callback.from_user.id

  # ഓണർ (OWNER_ID: 1689374364) അല്ലെങ്കിൽ ഒറിജിനൽ ക്രിയേറ്റർ ആണെങ്കിൽ മാത്രം ഡിലീറ്റ് ചെയ്യാം
  if user_id == OWNER_ID or user_id == creator_id:
    cursor.execute("DELETE FROM surprises WHERE id = ?", (surprise_id,))
    conn.commit()
    conn.close()
    await callback.message.edit_text(
        "🗑️ This birthday surprise has been permanently deleted."
    )
    await callback.answer("Deleted successfully!", show_alert=True)
  else:
    conn.close()
    await callback.answer(
        "⛔ You do not have permission to delete this surprise!",
        show_alert=True,
    )


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
  )
  await state.set_state(BirthdayForm.year)


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


@dp.message(BirthdayForm.song, F.audio)
async def process_song_audio(message: types.Message, state: FSMContext):
  await state.update_data(song=message.audio.file_id)
  await message.answer(
      STATE_PROMPTS[BirthdayForm.voice], reply_markup=get_action_keyboard()
  )
  await state.set_state(BirthdayForm.voice)


@dp.message(BirthdayForm.song)
async def process_song_text(message: types.Message, state: FSMContext):
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
