import asyncio
import json
import os
import sqlite3
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand,
    WebAppInfo,
    PreCheckoutQuery,
    LabeledPrice
)
from aiohttp import web
import urllib.parse

API_TOKEN = "8854916574:AAFS_XY76hbZSQPaz9AmPvVWFQLJHyY8kD0"
OWNER_ID = 1689374364

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
VERCEL_URL = "https://aura-birthday-web.vercel.app"

COUNTRY_LANGUAGES = {
    "Asia": {
        "🇯🇵 Japan": [("Japanese", "ja")],
        "🇰🇷 South Korea": [("Korean", "ko")],
        "🇨🇳 China": [("Chinese (Mandarin)", "zh")],
        "🇮🇳 India": [
            ("English", "en"), ("Malayalam", "ml"), ("Hindi", "hi"),
            ("Tamil", "ta"), ("Telugu", "te"), ("Kannada", "kn"),
            ("Bengali", "bn"), ("Marathi", "mr"), ("Gujarati", "gu"),
            ("Punjabi", "pa"), ("Urdu", "ur")
        ],
        "🇦🇿 Azerbaijan": [("Azerbaijani", "az")],
        "🇦🇲 Armenia": [("Armenian", "hy")],
        "🇷🇺 Russia": [("Russian", "ru")],
        "🇮🇩 Indonesia": [("Indonesian", "id")],
        "🇹🇷 Turkey": [("Turkish", "tr")],
        "🇸🇦 Saudi Arabia": [("Arabic", "ar")],
        "🇦🇪 UAE": [("Arabic", "ar"), ("English", "en")],
        "🇲🇾 Malaysia": [("Malay", "ms")],
        "🇸🇬 Singapore": [("English", "en"), ("Mandarin", "zh"), ("Malay", "ms"), ("Tamil", "ta")],
        "🇺🇿 Uzbekistan": [("Uzbek", "uz")],
        "🇹🇯 Tajikistan": [("Tajik", "tg")],
        "🇮🇷 Iran": [("Persian", "fa")],
        "🇲🇲 Myanmar": [("Burmese", "my")],
        "🇻🇳 Vietnam": [("Vietnamese", "vi")],
        "🇵🇭 Philippines": [("Filipino", "fil"), ("English", "en")],
        "🇹🇭 Thailand": [("Thai", "th")],
        "🇳🇵 Nepal": [("Nepali", "ne")],
        "🇱🇰 Sri Lanka": [("Sinhala", "si"), ("Tamil", "ta")],
        "🇧🇩 Bangladesh": [("Bengali", "bn")],
        "🇵🇰 Pakistan": [("Urdu", "ur"), ("English", "en")]
    },
    "Europe": {
        "🇬🇧 United Kingdom": [("English", "en")],
        "🇩🇪 Germany": [("German", "de")],
        "🇫🇷 France": [("French", "fr")],
        "🇪🇸 Spain": [("Spanish", "es")],
        "🇮🇹 Italy": [("Italian", "it")],
        "🇵🇹 Portugal": [("Portuguese", "pt")],
        "🇳🇱 Netherlands": [("Dutch", "nl")],
        "🇵🇱 Poland": [("Polish", "pl")],
        "🇺🇦 Ukraine": [("Ukrainian", "uk")],
        "🇧🇾 Belarus": [("Belarusian", "be"), ("Russian", "ru")],
        "🇸🇪 Sweden": [("Swedish", "sv")],
        "🇬🇷 Greece": [("Greek", "el")],
        "🇷🇴 Romania": [("Romanian", "ro")],
        "🇨🇿 Czech Republic": [("Czech", "cs")]
    },
    "Africa": {
        "🇳🇬 Nigeria": [("English", "en"), ("Hausa", "ha"), ("Yoruba", "yo")],
        "🇪🇬 Egypt": [("Arabic", "ar")],
        "🇰🇪 Kenya": [("English", "en"), ("Swahili", "sw")],
        "🇿🇦 South Africa": [("English", "en"), ("Zulu", "zu"), ("Xhosa", "xh"), ("Afrikaans", "af")],
        "🇪🇹 Ethiopia": [("Amharic", "am")]
    },
    "Americas": {
        "🇺🇸 United States": [("English", "en"), ("Spanish", "es")],
        "🇧🇷 Brazil": [("Portuguese", "pt")],
        "🇲🇽 Mexico": [("Spanish", "es")]
    }
}

BOT_TEXTS = {
    "en": {
        "welcome": "✨ *Welcome to your little corner of surprises...*\n\nChoose your region and country to get started:",
        "region_selected": "🌍 Region: *{region}*. Select your country:",
        "country_choice": "🗣️ Choose your language for *{country}*:",
        "lang_updated": "✅ Language updated successfully!",
        "ask_category": "🎉 *What kind of celebration or wish is this?* Choose below:",
        "det_ask_name": "✨ *Whose special celebration is this?* Send their name:",
        "det_ask_wish": "📝 *Write a sweet, heartfelt message for them:*",
        "ask_gender": "👤 *Select target profile (Boy / Girl):*",
        "ask_dob_type": "⏳ *How would you like to add age / date details for stats?*",
        "ask_dob_date": "📅 Please send Date in **YYYY-MM-DD** format:",
        "ask_dob_direct": "🔢 Please enter their direct age as a number:",
        "ask_year": "📅 *Choose the year for the surprise:*",
        "ask_month": "📆 *Choose the month:*",
        "ask_day": "🗓️ *Pick the date:*",
        "ask_hour": "⏰ *Select the Hour (24-Hour format, 00 to 23):*",
        "ask_minute": "⏱️ *Select the Minute (00 to 59):*",
        "ask_photo": "📸 *Share a lovely photo* (or skip):",
        "ask_video": "🎥 *Share a video moment* (or skip):",
        "ask_song": "🎶 *Send a favorite song* (or skip):",
        "ask_voice": "🎙️ *Send a voice note* (or skip):",
        "ask_audio": "🎵 *Add one more audio file* (or skip):",
        "ready": "✨ *All ready for {name}!*",
        "sim_ask_name": "✨ *Whose name is this wish for?* Send name:",
        "sim_ask_wish": "📝 *Type your quick wish message:*",
        "simple_ready": "✨ *Your simple wish for {name} is ready!*",
        "cancelled": "🚫 The process was cancelled. Send /start to begin again.",
        "help": "💡 *Available Commands:*\n/start - Create surprise\n/stats - System stats\n/cancel - Cancel process",
        "pay_required": "⭐ *Limit Reached!* The bot has crossed 500 users. To create more surprises, please pay with Telegram Stars."
    },
    "ml": {
        "welcome": "✨ *ചെറിയ സർപ്രൈസുകളുടെ ലോകത്തേക്ക് സ്വാഗതം...*\n\nതുടങ്ങാൻ പ്രദേശം തിരഞ്ഞെടുക്കൂ:",
        "region_selected": "🌍 പ്രദേശം: *{region}*. രാജ്യം തിരഞ്ഞെടുക്കൂ:",
        "country_choice": "🗣️ *{country}*-നുള്ള ഭാഷ തിരഞ്ഞെടുക്കൂ:",
        "lang_updated": "✅ ഭാഷ വിജയകരമായി മാറ്റിയിരിക്കുന്നു!",
        "ask_category": "🎉 *ഇത് എന്തുതരം ആഘോഷം അല്ലെങ്കിൽ ആശംസയാണ്?*",
        "det_ask_name": "✨ *ആരുടെ ആഘോഷമാണ്? പേര് അയക്കൂ:*",
        "det_ask_wish": "📝 *ദീർഘമായ ആശംസ സന്ദേശം എഴുതൂ:*",
        "ask_gender": "👤 *പ്രൊഫൈൽ തിരഞ്ഞെടുക്കൂ (Boy / Girl):*",
        "ask_dob_type": "⏳ *സ്റ്റാറ്റിസ്റ്റിക്സിനായി വിവരങ്ങൾ എങ്ങനെ നൽകണം?*",
        "ask_dob_date": "📅 തീയതി **YYYY-MM-DD** ഫോർമാറ്റിൽ അയക്കൂ:",
        "ask_dob_direct": "🔢 വയസ്സ് മാത്രം നമ്പർ ആയി നൽകൂ:",
        "ask_year": "📅 *വർഷം തിരഞ്ഞെടുക്കൂ:*", "ask_month": "📆 *മാസം തിരഞ്ഞെടുക്കൂ:*", "ask_day": "🗓️ *തീയതി തിരഞ്ഞെടുക്കൂ:*",
        "ask_hour": "⏰ *മണിക്കൂർ തിരഞ്ഞെടുക്കൂ:*", "ask_minute": "⏱️ *മിനിറ്റ് തിരഞ്ഞെടുക്കൂ:*",
        "ask_photo": "📸 *ഫോട്ടോ പങ്കുവെക്കൂ* (ഒഴിവാക്കാം):", "ask_video": "🎥 *വീഡിയോ പങ്കുവെക്കൂ* (ഒഴിവാക്കാം):",
        "ask_song": "🎶 *പാട്ട് അയക്കൂ* (ഒഴിവാക്കാം):", "ask_voice": "🎙️ *വോയിസ് നോട്ട് അയക്കൂ* (ഒഴിവാക്കാം):",
        "ask_audio": "🎵 *മറ്റൊരു ഓഡിയോ കൂടി ചേർക്കൂ* (ഒഴിവാക്കാം):",
        "ready": "✨ *{name}-നുള്ള സർപ്രൈസ് റെഡിയാണ്!*",
        "sim_ask_name": "✨ *ആർക്കാണ് ഈ വിഷ് അയക്കുന്നത്? പേര് നൽകൂ:*",
        "sim_ask_wish": "📝 *നിങ്ങളുടെ ചെറിയ ആശംസ ടൈപ്പ് ചെയ്യൂ:*",
        "simple_ready": "✨ *{name}-നുള്ള സിമ്പിൾ വിഷ് റെഡിയാണ്!*",
        "cancelled": "🚫 പ്രക്രിയ റദ്ദാക്കിയിരിക്കുന്നു. വീണ്ടും തുടങ്ങാൻ /start നൽകുക.",
        "help": "💡 *കമാൻഡുകൾ:*\n/start - പുതിയ സർപ്രൈസ്\n/stats - സ്റ്റാറ്റിസ്റ്റിക്സ്\n/cancel - റദ്ദാക്കുക",
        "pay_required": "⭐ *പരിധി കഴിഞ്ഞിരിക്കുന്നു!* ബോട്ട് 500 യൂസർമാരെ പിന്നിട്ടു. തുടർന്നും സർപ്രൈസുകൾ ഉണ്ടാക്കാൻ ടെലഗ്രാം സ്റ്റാർസ് നൽകുക."
    }
}

OTHER_LANGS = ["ru", "fa", "it", "id", "uz", "tg", "az", "my", "zh", "ja", "ko", "hi", "tr", "pt", "ms", "vi", "fil", "th", "ne", "si", "hy", "nl", "pl", "uk", "be", "sv", "el", "ro", "cs", "sw", "ha", "yo", "zu", "xh", "af", "am", "es", "de", "fr", "ar", "ta", "te", "kn", "bn", "mr", "gu", "pa", "ur"]
for lang in OTHER_LANGS:
    if lang not in BOT_TEXTS:
        BOT_TEXTS[lang] = BOT_TEXTS["en"]

def get_bot_text(user_id, text_key, **kwargs):
    lang = get_user_lang(user_id)
    lang_dict = BOT_TEXTS.get(lang, BOT_TEXTS["en"])
    raw_text = lang_dict.get(text_key, BOT_TEXTS["en"].get(text_key, ""))
    return raw_text.format(**kwargs)

def init_db():
    conn = sqlite3.connect("bot_stats.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed INTEGER DEFAULT 0,
            creations_count INTEGER DEFAULT 0,
            lang TEXT DEFAULT 'en',
            unlimited_until TIMESTAMP DEFAULT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS surprises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            category TEXT,
            recipient_name TEXT,
            wish_text TEXT,
            params_json TEXT,
            lang TEXT DEFAULT 'en',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

def record_start(user_id):
    conn = sqlite3.connect("bot_stats.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, completed, creations_count, lang) VALUES (?, 0, 0, 'en')", (user_id,))
    conn.commit()
    conn.close()

def save_user_lang(user_id, lang_code):
    conn = sqlite3.connect("bot_stats.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (user_id, lang) VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET lang = ?
    """, (user_id, lang_code, lang_code))
    conn.commit()
    conn.close()

def get_user_lang(user_id):
    conn = sqlite3.connect("bot_stats.db")
    cursor = conn.cursor()
    cursor.execute("SELECT lang FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row and row[0] else "en"

def get_total_users():
    conn = sqlite3.connect("bot_stats.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def check_user_access(user_id):
    if user_id == OWNER_ID:
        return True
    total_users = get_total_users()
    if total_users <= 500:
        return True
    conn = sqlite3.connect("bot_stats.db")
    cursor = conn.cursor()
    cursor.execute("SELECT unlimited_until FROM users WHERE user_id = ? AND unlimited_until > DATETIME('now')", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row is not None

def save_surprise_to_db(user_id, category, recipient_name, wish_text, params_dict):
    lang_code = get_user_lang(user_id)
    conn = sqlite3.connect("bot_stats.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO surprises (user_id, category, recipient_name, wish_text, params_json, lang)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, category, recipient_name, wish_text, json.dumps(params_dict), lang_code))
    cursor.execute("UPDATE users SET creations_count = creations_count + 1, completed = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    surprise_id = cursor.lastrowid
    conn.close()
    return surprise_id

class DetailedForm(StatesGroup):
    category = State()
    name = State()
    wish = State()
    gender = State()
    dob_choice = State()
    dob_input = State()
    target_year = State()
    target_month = State()
    target_day = State()
    target_hour = State()
    target_minute = State()
    photo = State()
    video = State()
    song = State()
    voice = State()
    audio = State()

class SimpleForm(StatesGroup):
    category = State()
    name = State()
    wish = State()

def get_region_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌏 Asia", callback_data="reg_Asia"), InlineKeyboardButton(text="🌍 Europe", callback_data="reg_Europe")],
        [InlineKeyboardButton(text="🌍 Africa", callback_data="reg_Africa"), InlineKeyboardButton(text="🌎 Americas", callback_data="reg_Americas")],
        [InlineKeyboardButton(text="🇬🇧 Keep English (Skip)", callback_data="setlang_en")]
    ])

def get_countries_keyboard(region, page=0, items_per_page=6):
    countries = list(COUNTRY_LANGUAGES.get(region, {}).keys())
    start_idx = page * items_per_page
    end_idx = start_idx + items_per_page
    page_countries = countries[start_idx:end_idx]
    keyboard = []
    row = []
    for c in page_countries:
        row.append(InlineKeyboardButton(text=c, callback_data=f"country_{region}_{c}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row: keyboard.append(row)
    nav = []
    if page > 0: nav.append(InlineKeyboardButton(text="⬅️ Prev", callback_data=f"cpage_{region}_{page-1}"))
    if end_idx < len(countries): nav.append(InlineKeyboardButton(text="Next ➡️", callback_data=f"cpage_{region}_{page+1}"))
    if nav: keyboard.append(nav)
    keyboard.append([InlineKeyboardButton(text="🔙 Back", callback_data="back_to_regions")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

DETAILED_CATEGORIES = ["Birthday", "HouseWarming", "Proposal", "WeddingWish", "Wedding", "NewBorn", "Graduation", "Festival", "Other"]

def get_category_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎂 Happy Birthday", callback_data="cat_Birthday"), InlineKeyboardButton(text="🏡 House Warming", callback_data="cat_HouseWarming")],
        [InlineKeyboardButton(text="🏮 Festival", callback_data="cat_Festival"), InlineKeyboardButton(text="💍 Proposal", callback_data="cat_Proposal")],
        [InlineKeyboardButton(text="💒 Wedding Wish", callback_data="cat_WeddingWish"), InlineKeyboardButton(text="💍 Happy Anniversary", callback_data="cat_Wedding")],
        [InlineKeyboardButton(text="👶 New Born Baby", callback_data="cat_NewBorn"), InlineKeyboardButton(text="🎓 Graduation", callback_data="cat_Graduation")],
        [InlineKeyboardButton(text="🌅 Good Morning", callback_data="cat_Morning"), InlineKeyboardButton(text="🌙 Good Night", callback_data="cat_Night")],
        [InlineKeyboardButton(text="🎉 Congratulations", callback_data="cat_Congratulations"), InlineKeyboardButton(text="❤️ I Love You", callback_data="cat_Love")],
        [InlineKeyboardButton(text="🫂 I Miss You", callback_data="cat_MissYou"), InlineKeyboardButton(text="🙏 Thank You", callback_data="cat_Thanks")],
        [InlineKeyboardButton(text="🥺 I’m Sorry", callback_data="cat_Sorry"), InlineKeyboardButton(text="🍀 Good Luck", callback_data="cat_Luck")],
        [InlineKeyboardButton(text="💪 All the Best", callback_data="cat_AllTheBest"), InlineKeyboardButton(text="🩷 Get Well Soon", callback_data="cat_GetWell")],
        [InlineKeyboardButton(text="🫶 Take Care", callback_data="cat_TakeCare"), InlineKeyboardButton(text="🎓 Exam Best of Luck", callback_data="cat_Exam")],
        [InlineKeyboardButton(text="💼 New Job", callback_data="cat_NewJob"), InlineKeyboardButton(text="🏆 Achievement", callback_data="cat_Achievement")],
        [InlineKeyboardButton(text="✈️ Safe Journey", callback_data="cat_Journey"), InlineKeyboardButton(text="🎁 Just For You", callback_data="cat_JustForYou")],
        [InlineKeyboardButton(text="😊 Have a Great Day", callback_data="cat_GreatDay"), InlineKeyboardButton(text="🌟 Other Celebration", callback_data="cat_Other")]
    ])

def get_gender_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👦 Boy / Groom", callback_data="gender_boy"), InlineKeyboardButton(text="👧 Girl / Bride", callback_data="gender_girl")]
    ])

def get_action_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✨ Skip", callback_data="skip_step"), InlineKeyboardButton(text="↩️ Change", callback_data="change_step")]
    ])

@dp.message(Command("cancel"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(get_bot_text(message.from_user.id, "cancelled"))

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(get_bot_text(message.from_user.id, "help"), parse_mode="Markdown")

@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    conn = sqlite3.connect("bot_stats.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), SUM(creations_count) FROM users")
    users_count, total_creations = cursor.fetchone()
    conn.close()
    users_count = users_count or 0
    total_creations = total_creations or 0
    stats_msg = f"📊 *Bot Statistics*\n\n👥 Total Users: `{users_count}`\n🎉 Total Surprises Created: `{total_creations}`\n⚡ System Status: `Operational`"
    await message.answer(stats_msg, parse_mode="Markdown")

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    record_start(user_id)
    save_user_lang(user_id, "en")
    await message.answer(get_bot_text(user_id, "welcome"), reply_markup=get_region_keyboard(), parse_mode="Markdown")

@dp.callback_query(F.data == "back_to_regions")
async def back_to_regions_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    await callback.message.edit_text(get_bot_text(user_id, "welcome"), reply_markup=get_region_keyboard(), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data.startswith("reg_"))
async def process_region(callback: types.CallbackQuery):
    region = callback.data.split("_")[1]
    user_id = callback.from_user.id
    await callback.message.edit_text(get_bot_text(user_id, "region_selected", region=region), reply_markup=get_countries_keyboard(region), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data.startswith("cpage_"))
async def process_cpage(callback: types.CallbackQuery):
    _, region, page = callback.data.split("_")
    await callback.message.edit_reply_markup(reply_markup=get_countries_keyboard(region, page=int(page)))
    await callback.answer()

@dp.callback_query(F.data.startswith("country_"))
async def process_country(callback: types.CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    region, country = parts[1], "_".join(parts[2:])
    user_id = callback.from_user.id
    langs = COUNTRY_LANGUAGES.get(region, {}).get(country, [("English", "en")])
    if len(langs) == 1:
        save_user_lang(user_id, langs[0][1])
        await callback.message.edit_text(get_bot_text(user_id, "lang_updated"))
        await check_access_and_proceed(callback.message, user_id, state)
    else:
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=l[0], callback_data=f"setlang_{l[1]}")] for l in langs])
        await callback.message.edit_text(get_bot_text(user_id, "country_choice", country=country), reply_markup=kb, parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data.startswith("setlang_"))
async def set_final_lang(callback: types.CallbackQuery, state: FSMContext):
    lang_code = callback.data.split("_")[1]
    user_id = callback.from_user.id
    save_user_lang(user_id, lang_code)
    await callback.message.edit_text(get_bot_text(user_id, "lang_updated"))
    await check_access_and_proceed(callback.message, user_id, state)
    await callback.answer()

async def check_access_and_proceed(message: types.Message, user_id: int, state: FSMContext):
    total_users = get_total_users()
    if total_users > 500 and user_id != OWNER_ID and not check_user_access(user_id):
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⭐ Pay 50 Stars (1 Month Unlimited)", callback_data="buy_unlimited")]
        ])
        await message.answer(get_bot_text(user_id, "pay_required"), reply_markup=kb, parse_mode="Markdown")
    else:
        await message.answer(get_bot_text(user_id, "ask_category"), reply_markup=get_category_keyboard(), parse_mode="Markdown")

@dp.callback_query(F.data == "buy_unlimited")
async def buy_unlimited_handler(callback: types.CallbackQuery):
    prices = [LabeledPrice(label="Monthly Unlimited Pass", amount=50)]
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="Unlimited Surprises Pass",
        description="Get 1 month of unlimited surprise creation after 500 users limit!",
        payload="monthly_unlimited_pass",
        currency="XTR",
        prices=prices
    )
    await callback.answer()

@dp.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(F.successful_payment)
async def successful_payment_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    conn = sqlite3.connect("bot_stats.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET unlimited_until = DATETIME('now', '+30 days') WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    await message.answer("🎉 Payment successful! You now have unlimited access for 30 days. Send /start to begin.")

@dp.callback_query(F.data.startswith("cat_"))
async def process_category(callback: types.CallbackQuery, state: FSMContext):
    category = callback.data.split("_")[1]
    user_id = callback.from_user.id
    
    total_users = get_total_users()
    if total_users > 500 and user_id != OWNER_ID and not check_user_access(user_id):
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⭐ Pay 50 Stars (1 Month Unlimited)", callback_data="buy_unlimited")]
        ])
        await callback.message.answer(get_bot_text(user_id, "pay_required"), reply_markup=kb, parse_mode="Markdown")
        await callback.answer()
        return

    if category in DETAILED_CATEGORIES:
        await state.update_data(category=category)
        await callback.message.answer(get_bot_text(user_id, "det_ask_name"), reply_markup=get_action_keyboard(), parse_mode="Markdown")
        await state.set_state(DetailedForm.name)
    else:
        await state.update_data(category=category)
        await callback.message.answer(get_bot_text(user_id, "sim_ask_name"), parse_mode="Markdown")
        await state.set_state(SimpleForm.name)
    await callback.answer()

@dp.message(SimpleForm.name)
async def process_simple_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(SimpleForm.wish)
    await message.answer(get_bot_text(message.from_user.id, "sim_ask_wish"), parse_mode="Markdown")

@dp.message(SimpleForm.wish)
async def process_simple_wish(message: types.Message, state: FSMContext):
    await state.update_data(wish=message.text.strip())
    data = await state.get_data()
    
    params = {
        "name": data.get("name", "Friend"),
        "msg": data.get("wish", ""),
        "category": data.get("category", "Morning"),
        "gender": "boy",
        "dob": "", "age": "", "target_time": "",
        "photo": "", "video": "", "song": "", "voice": "", "extra_audio": ""
    }
    
    surprise_id = save_surprise_to_db(message.from_user.id, params["category"], params["name"], params["msg"], params)
    view_url = f"{VERCEL_URL}/?id={surprise_id}"
    
    wa_share = f"https://api.whatsapp.com/send?text={urllib.parse.quote('✨ Special celebration wish! 🎉 ' + view_url)}"
    tg_share = f"https://t.me/share/url?url={urllib.parse.quote(view_url)}&text={urllib.parse.quote('✨ Special celebration wish! 🎉')}"
    fb_share = f"https://www.facebook.com/sharer/sharer.php?u={urllib.parse.quote(view_url)}"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✨ Open View", web_app=WebAppInfo(url=view_url))],
        [
            InlineKeyboardButton(text="🟢 WhatsApp", url=wa_share),
            InlineKeyboardButton(text="💬 Telegram", url=tg_share),
            InlineKeyboardButton(text="🔵 Facebook", url=fb_share)
        ],
        [InlineKeyboardButton(text="🗑️ Delete", callback_data=f"delete_surp_{surprise_id}")]
    ])
    
    success_msg = get_bot_text(message.from_user.id, "simple_ready", name=params["name"])
    await message.answer(success_msg, reply_markup=kb, parse_mode="Markdown")
    await state.clear()

@dp.message(DetailedForm.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    data = await state.get_data()
    cat = data.get("category", "")
    
    if cat in ["Wedding", "WeddingWish", "NewBorn", "Graduation"]:
        await state.set_state(DetailedForm.gender)
        await message.answer(get_bot_text(message.from_user.id, "ask_gender"), reply_markup=get_gender_keyboard(), parse_mode="Markdown")
    else:
        if cat in ["Festival", "HouseWarming"]:
            await state.update_data(dob="", age="")
            await ask_target_year(message, state)
        else:
            await state.set_state(DetailedForm.wish)
            await message.answer(get_bot_text(message.from_user.id, "det_ask_wish"), reply_markup=get_action_keyboard(), parse_mode="Markdown")

@dp.callback_query(F.data.startswith("gender_"))
async def process_gender(callback: types.CallbackQuery, state: FSMContext):
    gender = callback.data.split("_")[1]
    await state.update_data(gender=gender)
    data = await state.get_data()
    cat = data.get("category", "")
    if cat in ["Festival", "HouseWarming"]:
        await state.update_data(dob="", age="")
        await ask_target_year(callback.message, state)
    else:
        await state.set_state(DetailedForm.wish)
        await callback.message.answer(get_bot_text(callback.from_user.id, "det_ask_wish"), reply_markup=get_action_keyboard(), parse_mode="Markdown")
    await callback.answer()

@dp.message(DetailedForm.wish)
async def process_wish(message: types.Message, state: FSMContext):
    await state.update_data(wish=message.text.strip())
    data = await state.get_data()
    cat = data.get("category", "")
    
    if cat == "Festival":
        await state.update_data(dob="", age="")
        await ask_target_year(message, state)
    else:
        await state.set_state(DetailedForm.dob_choice)
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📅 Enter Date", callback_data="dob_date")],
            [InlineKeyboardButton(text="🔢 Enter Age Details", callback_data="dob_direct")],
            [InlineKeyboardButton(text="✨ Skip Stats", callback_data="skip_stats")]
        ])
        await message.answer(get_bot_text(message.from_user.id, "ask_dob_type"), reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "dob_date")
async def dob_date_selected(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(dob_type="date")
    await state.set_state(DetailedForm.dob_input)
    await callback.message.answer(get_bot_text(callback.from_user.id, "ask_dob_date"), reply_markup=get_action_keyboard(), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "dob_direct")
async def dob_direct_selected(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(dob_type="direct")
    await state.set_state(DetailedForm.dob_input)
    await callback.message.answer(get_bot_text(callback.from_user.id, "ask_dob_direct"), reply_markup=get_action_keyboard(), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "skip_stats")
async def skip_stats_selected(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(dob="", age="")
    await ask_target_year(callback.message, state)
    await callback.answer()

@dp.message(DetailedForm.dob_input)
async def process_dob_input(message: types.Message, state: FSMContext):
    val = message.text.strip()
    data = await state.get_data()
    if data.get("dob_type") == "direct":
        await state.update_data(age=val, dob=val)
    else:
        await state.update_data(dob=val, age="")
    await ask_target_year(message, state)

async def ask_target_year(message: types.Message, state: FSMContext):
    await state.set_state(DetailedForm.target_year)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="2026", callback_data="year_2026"), InlineKeyboardButton(text="2027", callback_data="year_2027")],
        [InlineKeyboardButton(text="✨ Skip", callback_data="skip_year")]
    ])
    await message.answer(get_bot_text(message.from_user.id, "ask_year"), reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data.startswith("year_"))
async def process_year(callback: types.CallbackQuery, state: FSMContext):
    year = callback.data.split("_")[1]
    await state.update_data(target_year=year)
    await ask_target_month(callback.message, state)
    await callback.answer()

@dp.callback_query(F.data == "skip_year")
async def skip_year(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(target_year="")
    await ask_target_month(callback.message, state)
    await callback.answer()

async def ask_target_month(message: types.Message, state: FSMContext):
    await state.set_state(DetailedForm.target_month)
    months = [("January", "01"), ("February", "02"), ("March", "03"), ("April", "04"),
              ("May", "05"), ("June", "06"), ("July", "07"), ("August", "08"),
              ("September", "09"), ("October", "10"), ("November", "11"), ("December", "12")]
    kb = []
    row = []
    for m, num in months:
        row.append(InlineKeyboardButton(text=m, callback_data=f"mon_{num}"))
        if len(row) == 3:
            kb.append(row)
            row = []
    if row: kb.append(row)
    kb.append([InlineKeyboardButton(text="✨ Skip", callback_data="skip_month")])
    await message.answer(get_bot_text(message.from_user.id, "ask_month"), reply_markup=InlineKeyboardMarkup(inline_keyboard=kb), parse_mode="Markdown")

@dp.callback_query(F.data.startswith("mon_"))
async def process_month(callback: types.CallbackQuery, state: FSMContext):
    mon = callback.data.split("_")[1]
    await state.update_data(target_month=mon)
    await ask_target_day(callback.message, state)
    await callback.answer()

@dp.callback_query(F.data == "skip_month")
async def skip_month(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(target_month="")
    await ask_target_day(callback.message, state)
    await callback.answer()

async def ask_target_day(message: types.Message, state: FSMContext):
    await state.set_state(DetailedForm.target_day)
    kb = []
    row = []
    for d in range(1, 32):
        day_str = f"{d:02d}"
        row.append(InlineKeyboardButton(text=str(d), callback_data=f"day_{day_str}"))
        if len(row) == 7:
            kb.append(row)
            row = []
    if row: kb.append(row)
    kb.append([InlineKeyboardButton(text="✨ Skip", callback_data="skip_day")])
    await message.answer(get_bot_text(message.from_user.id, "ask_day"), reply_markup=InlineKeyboardMarkup(inline_keyboard=kb), parse_mode="Markdown")

@dp.callback_query(F.data.startswith("day_"))
async def process_day(callback: types.CallbackQuery, state: FSMContext):
    day = callback.data.split("_")[1]
    await state.update_data(target_day=day)
    await ask_target_hour(callback.message, state)
    await callback.answer()

@dp.callback_query(F.data == "skip_day")
async def skip_day(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(target_day="")
    await ask_target_hour(callback.message, state)
    await callback.answer()

async def ask_target_hour(message: types.Message, state: FSMContext):
    await state.set_state(DetailedForm.target_hour)
    kb = []
    row = []
    for h in range(24):
        h_str = f"{h:02d}"
        row.append(InlineKeyboardButton(text=h_str, callback_data=f"hour_{h_str}"))
        if len(row) == 6:
            kb.append(row)
            row = []
    if row: kb.append(row)
    kb.append([InlineKeyboardButton(text="✨ Skip", callback_data="skip_hour")])
    await message.answer(get_bot_text(message.from_user.id, "ask_hour"), reply_markup=InlineKeyboardMarkup(inline_keyboard=kb), parse_mode="Markdown")

@dp.callback_query(F.data.startswith("hour_"))
async def process_hour(callback: types.CallbackQuery, state: FSMContext):
    hour = callback.data.split("_")[1]
    await state.update_data(target_hour=hour)
    await ask_target_minute(callback.message, state)
    await callback.answer()

@dp.callback_query(F.data == "skip_hour")
async def skip_hour(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(target_hour="")
    await ask_target_minute(callback.message, state)
    await callback.answer()

async def ask_target_minute(message: types.Message, state: FSMContext):
    await state.set_state(DetailedForm.target_minute)
    kb = []
    row = []
    for m in range(0, 60):
        m_str = f"{m:02d}"
        row.append(InlineKeyboardButton(text=m_str, callback_data=f"min_{m_str}"))
        if len(row) == 6:
            kb.append(row)
            row = []
    if row: kb.append(row)
    kb.append([InlineKeyboardButton(text="✨ Skip", callback_data="skip_minute")])
    await message.answer(get_bot_text(message.from_user.id, "ask_minute"), reply_markup=InlineKeyboardMarkup(inline_keyboard=kb), parse_mode="Markdown")

@dp.callback_query(F.data.startswith("min_"))
async def process_minute(callback: types.CallbackQuery, state: FSMContext):
    minute = callback.data.split("_")[1]
    await state.update_data(target_minute=minute)
    await prompt_photo(callback.message, state)
    await callback.answer()

@dp.callback_query(F.data == "skip_minute")
async def skip_minute(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(target_minute="")
    await prompt_photo(callback.message, state)
    await callback.answer()

async def prompt_photo(message: types.Message, state: FSMContext):
    await state.set_state(DetailedForm.photo)
    await message.answer(get_bot_text(message.from_user.id, "ask_photo"), reply_markup=get_action_keyboard(), parse_mode="Markdown")

async def get_telegram_file_url(bot: Bot, file_id: str) -> str:
    try:
        file = await bot.get_file(file_id)
        return f"https://api.telegram.org/file/bot{bot.token}/{file.file_path}"
    except Exception:
        return ""

@dp.message(DetailedForm.photo, F.photo)
async def process_photo(message: types.Message, state: FSMContext):
    url = await get_telegram_file_url(bot, message.photo[-1].file_id)
    await state.update_data(photo=url)
    await state.set_state(DetailedForm.video)
    await message.answer(get_bot_text(message.from_user.id, "ask_video"), reply_markup=get_action_keyboard(), parse_mode="Markdown")

@dp.message(DetailedForm.video, F.video)
async def process_video(message: types.Message, state: FSMContext):
    url = await get_telegram_file_url(bot, message.video.file_id)
    await state.update_data(video=url)
    await state.set_state(DetailedForm.song)
    await message.answer(get_bot_text(message.from_user.id, "ask_song"), reply_markup=get_action_keyboard(), parse_mode="Markdown")

@dp.message(DetailedForm.song, F.audio)
async def process_song(message: types.Message, state: FSMContext):
    url = await get_telegram_file_url(bot, message.audio.file_id)
    await state.update_data(song=url)
    await state.set_state(DetailedForm.voice)
    await message.answer(get_bot_text(message.from_user.id, "ask_voice"), reply_markup=get_action_keyboard(), parse_mode="Markdown")

@dp.message(DetailedForm.voice, F.voice)
async def process_voice(message: types.Message, state: FSMContext):
    url = await get_telegram_file_url(bot, message.voice.file_id)
    await state.update_data(voice=url)
    await state.set_state(DetailedForm.audio)
    await message.answer(get_bot_text(message.from_user.id, "ask_audio"), reply_markup=get_action_keyboard(), parse_mode="Markdown")

@dp.message(DetailedForm.audio, F.audio)
async def process_audio(message: types.Message, state: FSMContext):
    url = await get_telegram_file_url(bot, message.audio.file_id)
    await state.update_data(extra_audio=url)
    await finish_detailed_form(message, state)

@dp.callback_query(F.data == "skip_step")
async def process_skip(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    user_id = callback.from_user.id
    if current_state == DetailedForm.photo.state:
        await state.set_state(DetailedForm.video)
        await callback.message.answer(get_bot_text(user_id, "ask_video"), reply_markup=get_action_keyboard(), parse_mode="Markdown")
    elif current_state == DetailedForm.video.state:
        await state.set_state(DetailedForm.song)
        await callback.message.answer(get_bot_text(user_id, "ask_song"), reply_markup=get_action_keyboard(), parse_mode="Markdown")
    elif current_state == DetailedForm.song.state:
        await state.set_state(DetailedForm.voice)
        await callback.message.answer(get_bot_text(user_id, "ask_voice"), reply_markup=get_action_keyboard(), parse_mode="Markdown")
    elif current_state == DetailedForm.voice.state:
        await state.set_state(DetailedForm.audio)
        await callback.message.answer(get_bot_text(user_id, "ask_audio"), reply_markup=get_action_keyboard(), parse_mode="Markdown")
    elif current_state == DetailedForm.audio.state:
        await finish_detailed_form(callback.message, state)
    elif current_state == DetailedForm.dob_input.state:
        await ask_target_year(callback.message, state)
    await callback.answer("Skipped")

async def finish_detailed_form(message: types.Message, state: FSMContext):
    data = await state.get_data()
    y, m, d = data.get("target_year", ""), data.get("target_month", ""), data.get("target_day", "")
    h, mn = data.get("target_hour", "00"), data.get("target_minute", "00")
    
    target_time_str = f"{y}-{m}-{d}T{h}:{mn}:00" if (y and m and d) else ""

    params = {
        "name": data.get("name", "Friend"),
        "msg": data.get("wish", ""),
        "category": data.get("category", "Birthday"),
        "gender": data.get("gender", "boy"),
        "dob": data.get("dob", ""),
        "age": data.get("age", data.get("dob", "")),
        "target_time": target_time_str,
        "photo": data.get("photo", ""),
        "video": data.get("video", ""),
        "song": data.get("song", ""),
        "voice": data.get("voice", ""),
        "extra_audio": data.get("extra_audio", "")
    }
    
    surprise_id = save_surprise_to_db(message.from_user.id, params["category"], params["name"], params["msg"], params)
    
    preview_url = f"{VERCEL_URL}/?id={surprise_id}&preview=true"
    view_url = f"{VERCEL_URL}/?id={surprise_id}"
    
    wa_share = f"https://api.whatsapp.com/send?text={urllib.parse.quote('✨ Special celebration wish! 🎉 ' + view_url)}"
    tg_share = f"https://t.me/share/url?url={urllib.parse.quote(view_url)}&text={urllib.parse.quote('✨ Special celebration wish! 🎉')}"
    fb_share = f"https://www.facebook.com/sharer/sharer.php?u={urllib.parse.quote(view_url)}"

    btn_label = "🎂 My View" if params["category"] == "Birthday" else "✨ Open Surprise View"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🤍 Preview", web_app=WebAppInfo(url=preview_url)),
            InlineKeyboardButton(text=btn_label, web_app=WebAppInfo(url=view_url))
        ],
        [
            InlineKeyboardButton(text="🟢 WhatsApp", url=wa_share),
            InlineKeyboardButton(text="💬 Telegram", url=tg_share),
            InlineKeyboardButton(text="🔵 Facebook", url=fb_share)
        ],
        [InlineKeyboardButton(text="🗑️ Delete", callback_data=f"delete_surp_{surprise_id}")]
    ])
    
    success_msg = get_bot_text(message.from_user.id, "ready", name=params["name"])
    await message.answer(success_msg, reply_markup=kb, parse_mode="Markdown")
    await state.clear()

@dp.callback_query(F.data.startswith("delete_surp_"))
async def inline_delete_surprise(callback: types.CallbackQuery):
    surp_id = callback.data.split("_")[2]
    conn = sqlite3.connect("bot_stats.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM surprises WHERE id = ?", (surp_id,))
    conn.commit()
    conn.close()
    await callback.message.edit_text("🗑️ This surprise has been deleted successfully!")
    await callback.answer()

async def get_surprise_api(request):
    surprise_id = request.query.get("id")
    if not surprise_id: return web.json_response({"error": "No ID"}, status=400)
    conn = sqlite3.connect("bot_stats.db")
    cursor = conn.cursor()
    cursor.execute("SELECT params_json FROM surprises WHERE id = ?", (surprise_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return web.json_response(json.loads(row[0]), headers={"Access-Control-Allow-Origin": "*"})
    return web.json_response({"error": "Not found"}, status=404)

async def web_server():
    app = web.Application()
    app.router.add_get("/api/surprise", get_surprise_api)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.environ.get("PORT", 8080)))
    await site.start()

async def setup_bot_commands():
    commands = [
        BotCommand(command="start", description="🎉 Create a Surprise"),
        BotCommand(command="stats", description="📊 Bot Statistics"),
        BotCommand(command="help", description="💡 Help & Info"),
        BotCommand(command="cancel", description="🚫 Cancel Process")
    ]
    await bot.set_my_commands(commands)

async def main():
    await setup_bot_commands()
    await asyncio.gather(web_server(), dp.start_polling(bot))

if __name__ == "__main__":
    asyncio.run(main())
