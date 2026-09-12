import asyncio
import datetime
import logging
import os
import uuid
from aiohttp import web
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
    InlineQuery,
)

TOKEN = "8854916574:AAHhpQWzOOH7IKjuitJfS_yspUoWy0z2So4"
ADMIN_USER_ID = 1689374364

router = Router()
logging.basicConfig(level=logging.INFO)

surprises_db = {}
user_created_surprises = {}


class CreateSurprise(StatesGroup):
  waiting_for_name = State()
  waiting_for_year = State()
  waiting_for_month = State()
  waiting_for_date = State()
  waiting_for_time = State()
  waiting_for_ampm = State()
  waiting_for_message = State()
  waiting_for_photo = State()
  waiting_for_video = State()
  waiting_for_song = State()
  waiting_for_voice = State()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
  user_id = message.from_user.id
  args = message.text.split()

  if len(args) > 1 and args[1].startswith("surp_"):
    surp_id = args[1]
    if surp_id in surprises_db:
      data = surprises_db[surp_id]

      if data.get("target_time"):
        try:
          target_dt = datetime.datetime.strptime(
              data["target_time"], "%Y-%m-%d %H:%M"
          )
          current_dt = datetime.datetime.now()
          if current_dt < target_dt:
            time_left = target_dt - current_dt
            days = time_left.days
            hours = time_left.seconds // 3600
            minutes = (time_left.seconds % 3600) // 60
            await message.answer(
                f"⏳ **This magical surprise is locked!**\n\n"
                f"⏰ Unlocks in: *{days} days, {hours} hours, {minutes}"
                f" minutes*\n📅 Exact Date: *{data['target_time']}*"
            )
            return
        except Exception:
          pass

      keyboard = InlineKeyboardMarkup(
          inline_keyboard=[
              [
                  InlineKeyboardButton(
                      text="🎁 📦 Open Magical Gift Box",
                      callback_data=f"gift_{surp_id}",
                  )
              ]
          ]
      )
      await message.answer(
          f"🌟 **A top-secret milestone birthday package has arrived for"
          f" {data['name']}!**\n\nTap the glowing gift box below to unwrap it"
          " 👇",
          reply_markup=keyboard,
      )
      return
    else:
      await message.answer("This surprise link has expired or is invalid!")
      return

  highlight_banner = (
      "🌟━━━━━━━━━━━━━━━━━━━🌟\n"
      "   🎉 **THE ULTIMATE ALL-IN-ONE BIRTHDAY BOT** 🎉\n"
      "🌟━━━━━━━━━━━━━━━━━━━🌟\n\n"
      "✨ *Create magical birthday surprises with Gift Boxes, Scratch Cards,"
      " Cake Cutting, Photos, Videos, Songs, Voice Notes & Custom Schedules!* \n\n"
      "👇 **Click the button below to start:**"
  )

  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="📖 How It Works", callback_data="how_it_works"
              ),
              InlineKeyboardButton(
                  text="✨ Create Surprise", callback_data="create_surprise"
              ),
          ],
          [
              InlineKeyboardButton(
                  text="🔍 Search via Inline",
                  switch_inline_query_current_chat="",
              )
          ],
      ]
  )
  await message.answer(highlight_banner, reply_markup=keyboard)


@router.message(Command("stats"))
async def cmd_stats(message: Message):
  if message.from_user.id == ADMIN_USER_ID:
    total_surprises = len(surprises_db)
    await message.answer(
        "📊 **Admin Statistics Dashboard:**\n\n"
        f"🎁 Total Surprises Created: `{total_surprises}`\n"
        f"👑 Bot Status: `Online & Fully Operational`",
        parse_mode="Markdown",
    )
  else:
    await message.answer("❌ You are not authorized to view admin stats.")


@router.inline_query()
async def inline_search(inline_query: InlineQuery):
  results = []
  user_id = inline_query.from_user.id
  user_id_surprises = user_created_surprises.get(user_id, [])

  if user_id_surprises:
    for surp_id in user_id_surprises:
      if surp_id in surprises_db:
        data = surprises_db[surp_id]
        bot_info = await inline_query.bot.get_me()
        link = f"https://t.me/{bot_info.username}?start={surp_id}"
        results.append(
            InlineQueryResultArticle(
                id=surp_id,
                title=f"🎂 Birthday Surprise for {data['name']}",
                description=f"Message: {data['msg'][:30]}...",
                input_message_content=InputTextMessageContent(
                    message_text=(
                        f"🎉 Here is the exclusive birthday surprise link for"
                        f" *{data['name']}*:\n{link}"
                    ),
                    parse_mode="Markdown",
                ),
            )
        )

  if not results:
    results.append(
        InlineQueryResultArticle(
            id="empty",
            title="Create a Birthday Surprise First",
            description="Tap here or go to the bot to create one!",
            input_message_content=InputTextMessageContent(
                message_text=(
                    "✨ Create your own interactive birthday surprise using our"
                    " bot!"
                )
            ),
        )
    )

  await inline_query.answer(results, cache_time=1)


@router.callback_query(F.data == "how_it_works")
async def show_guide(callback: CallbackQuery):
  guide_text = (
      "📖 **How This Bot Works:**\n\n"
      "1️⃣ Click **Create Surprise**.\n"
      "2️⃣ Enter Name, Date, Year & Time using buttons.\n"
      "3️⃣ Add Wish, Photo, Video, Song, and Voice Note step-by-step.\n"
      "4️⃣ Use **Back / Change** buttons if you need to modify anything!\n"
      "5️⃣ Share the unique link with your friend!"
  )
  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="✨ Create Surprise Now", callback_data="create_surprise"
              )
          ]
      ]
  )
  await callback.message.edit_text(guide_text, reply_markup=keyboard)
  await callback.answer()


@router.callback_query(F.data.startswith("gift_"))
async def open_gift(callback: CallbackQuery):
  surp_id = callback.data.split("_")[1]
  if surp_id in surprises_db:
    data = surprises_db[surp_id]
    await callback.message.edit_text(
        "📦 *Unwrapping the gift box...* ✨\n🎟️ *Preparing the scratch"
        " card...* 🌟"
    )
    await asyncio.sleep(1.5)

    scratch_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎫 🔲🔲🔲🔲🔲 (Scratch Here)",
                    callback_data=f"scratch_{surp_id}",
                )
            ]
        ]
    )
    await callback.message.edit_text(
        f"🎉 **Gift Unwrapped successfully for {data['name']}!** 🎉\n\n👇"
        " *Scratch the card below to proceed!*",
        reply_markup=scratch_keyboard,
    )
    await callback.answer()


@router.callback_query(F.data.startswith("scratch_"))
async def scratch_card(callback: CallbackQuery):
  surp_id = callback.data.split("_")[1]
  if surp_id in surprises_db:
    data = surprises_db[surp_id]
    await callback.message.edit_text(
        "✨ *Card scratched!* 🎫\n🎂 *Lighting candles & bringing out the"
        " cake...* 🕯️"
    )
    await asyncio.sleep(1.5)

    cake_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎂🔥 Blow Candles & Cut Cake",
                    callback_data=f"cake_{surp_id}",
                )
            ]
        ]
    )
    await callback.message.edit_text(
        f"🎈 **Almost there, {data['name']}!** 🎈\n\n👇 *Tap below to blow out"
        " the candles and cut the cake!*",
        reply_markup=cake_keyboard,
    )
    await callback.answer()


@router.callback_query(F.data.startswith("cake_"))
async def cut_cake(callback: CallbackQuery):
  surp_id = callback.data.split("_")[1]
  if surp_id in surprises_db:
    data = surprises_db[surp_id]
    await callback.message.edit_text(
        "🎉 *Make a wish! Blow!* 🌬️🎂\n🎊 *Cutting the cake...* 🍰✨"
    )
    await asyncio.sleep(1.5)

    caption = (
        f"🎊✨ **HAPPY BIRTHDAY {data['name'].upper()}!** ✨🎊\n\n{data['msg']}"
    )

    if data.get("photo"):
      await callback.message.answer_photo(photo=data["photo"], caption=caption)
    if data.get("video"):
      await callback.message.answer_video(video=data["video"], caption="🎥 Special Video")
    if data.get("song"):
      await callback.message.answer_audio(audio=data["song"], caption="🎵 Special Song")
    if data.get("voice"):
      await callback.message.answer_voice(voice=data["voice"], caption="🎤 Special Voice Note")

    if not any([data.get("photo"), data.get("video"), data.get("song"), data.get("voice")]):
      await callback.message.answer(caption)

    await callback.answer()


@router.callback_query(F.data == "create_surprise")
async def process_creation(callback: CallbackQuery, state: FSMContext):
  user_id = callback.from_user.id
  if user_id == ADMIN_USER_ID:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Cancel / Back to Start", callback_data="cancel_creation")]
        ]
    )
    await callback.message.answer(
        "👑 [Admin Mode]: Free creation enabled!\n\n1️⃣ Enter the birthday"
        " person's name:",
        reply_markup=keyboard
    )
    await state.set_state(CreateSurprise.waiting_for_name)
    await callback.answer()
  else:
    prices = [LabeledPrice(label="Ultimate Surprise Pass", amount=75)]
    await callback.message.answer_invoice(
        title="Ultimate Birthday Bot",
        description="Pay 75 Telegram Stars to create your surprise.",
        prices=prices,
        currency="XTR",
        payload="scratch_surprise_payment",
    )
    await callback.answer()


@router.callback_query(F.data == "cancel_creation")
async def cancel_creation(callback: CallbackQuery, state: FSMContext):
  await state.clear()
  await callback.message.edit_text("❌ Creation cancelled. Send /start to begin again.")
  await callback.answer()


@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
  await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message, state: FSMContext):
  if message.successful_payment.invoice_payload == "scratch_surprise_payment":
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Cancel", callback_data="cancel_creation")]
        ]
    )
    await message.answer(
        "✅ Payment successful!\n\n1️⃣ Enter the birthday person's name:",
        reply_markup=keyboard
    )
    await state.set_state(CreateSurprise.waiting_for_name)


@router.message(CreateSurprise.waiting_for_name)
async def get_surprise_name(message: Message, state: FSMContext):
  await state.update_data(name=message.text)
  
  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(text="2026", callback_data="year_2026"),
              InlineKeyboardButton(text="2027", callback_data="year_2027"),
          ],
          [InlineKeyboardButton(text="✏️ Type Year Manually", callback_data="year_manual")],
          [InlineKeyboardButton(text="⬅️ Change Name", callback_data="change_name")]
      ]
  )
  await message.answer(f"Name saved: **{message.text}**\n\n2️⃣ Select or type the **Year**:", reply_markup=keyboard, parse_mode="Markdown")
  await state.set_state(CreateSurprise.waiting_for_year)


@router.callback_query(F.data == "change_name")
async def callback_change_name(callback: CallbackQuery, state: FSMContext):
  keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Cancel", callback_data="cancel_creation")]])
  await callback.message.edit_text("1️⃣ Please re-enter the birthday person's name:", reply_markup=keyboard)
  await state.set_state(CreateSurprise.waiting_for_name)
  await callback.answer()


@router.callback_query(F.data.startswith("year_"))
async def select_year(callback: CallbackQuery, state: FSMContext):
  if callback.data == "year_manual":
    await callback.message.edit_text("Please type the Year (e.g., 2026):")
    return
  
  year = callback.data.split("_")[1]
  await state.update_data(year=year)
  
  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [InlineKeyboardButton(text="Jan-Apr", callback_data="m_q1"), InlineKeyboardButton(text="May-Aug", callback_data="m_q2")],
          [InlineKeyboardButton(text="Sep-Dec", callback_data="m_q3"), InlineKeyboardButton(text="✏️ Type Month (1-12)", callback_data="m_manual")],
          [InlineKeyboardButton(text="⬅️ Change Year", callback_data="change_year")]
      ]
  )
  await callback.message.edit_text(f"Year selected: {year}\n\n3️⃣ Select **Month**:", reply_markup=keyboard)
  await state.set_state(CreateSurprise.waiting_for_month)
  await callback.answer()


@router.callback_query(F.data == "change_year")
async def callback_change_year(callback: CallbackQuery, state: FSMContext):
  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [InlineKeyboardButton(text="2026", callback_data="year_2026"), InlineKeyboardButton(text="2027", callback_data="year_2027")],
          [InlineKeyboardButton(text="✏️ Type Manual", callback_data="year_manual")]
      ]
  )
  await callback.message.edit_text("2️⃣ Select or type the **Year**:", reply_markup=keyboard)
  await state.set_state(CreateSurprise.waiting_for_year)
  await callback.answer()


@router.message(CreateSurprise.waiting_for_year)
async def manual_year(message: Message, state: FSMContext):
  await state.update_data(year=message.text)
  keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Change Year", callback_data="change_year")]])
  await message.answer("3️⃣ Enter **Month** (1 to 12):", reply_markup=keyboard)
  await state.set_state(CreateSurprise.waiting_for_month)


@router.callback_query(F.data.startswith("m_"))
async def select_month(callback: CallbackQuery, state: FSMContext):
  if callback.data == "m_q1":
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="1 (Jan)", callback_data="mo_1"), InlineKeyboardButton(text="2 (Feb)", callback_data="mo_2")], [InlineKeyboardButton(text="3 (Mar)", callback_data="mo_3"), InlineKeyboardButton(text="4 (Apr)", callback_data="mo_4")], [InlineKeyboardButton(text="⬅️ Change Month", callback_data="change_month")]])
    await callback.message.edit_text("Select Month:", reply_markup=kb)
    return
  elif callback.data == "m_q2":
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="5 (May)", callback_data="mo_5"), InlineKeyboardButton(text="6 (Jun)", callback_data="mo_6")], [InlineKeyboardButton(text="7 (Jul)", callback_data="mo_7"), InlineKeyboardButton(text="8 (Aug)", callback_data="mo_8")], [InlineKeyboardButton(text="⬅️ Change Month", callback_data="change_month")]])
    await callback.message.edit_text("Select Month:", reply_markup=kb)
    return
  elif callback.data == "m_q3":
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="9 (Sep)", callback_data="mo_9"), InlineKeyboardButton(text="10 (Oct)", callback_data="mo_10")], [InlineKeyboardButton(text="11 (Nov)", callback_data="mo_11"), InlineKeyboardButton(text="12 (Dec)", callback_data="mo_12")], [InlineKeyboardButton(text="⬅️ Change Month", callback_data="change_month")]])
    await callback.message.edit_text("Select Month:", reply_markup=kb)
    return
  elif callback.data == "m_manual":
    await callback.message.edit_text("Type Month number (1-12):")
    return
  await callback.answer()


@router.callback_query(F.data == "change_month")
async def callback_change_month(callback: CallbackQuery, state: FSMContext):
  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [InlineKeyboardButton(text="Jan-Apr", callback_data="m_q1"), InlineKeyboardButton(text="May-Aug", callback_data="m_q2")],
          [InlineKeyboardButton(text="Sep-Dec", callback_data="m_q3"), InlineKeyboardButton(text="✏️ Type Manual", callback_data="m_manual")]
      ]
  )
  await callback.message.edit_text("3️⃣ Select **Month**:", reply_markup=keyboard)
  await state.set_state(CreateSurprise.waiting_for_month)
  await callback.answer()


@router.callback_query(F.data.startswith("mo_"))
async def set_month_callback(callback: CallbackQuery, state: FSMContext):
  month = callback.data.split("_")[1]
  await state.update_data(month=month)
  
  keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Change Month", callback_data="change_month")]])
  await callback.message.edit_text(f"Month selected: {month}\n\n4️⃣ Enter **Date** (1-31):", reply_markup=keyboard)
  await state.set_state(CreateSurprise.waiting_for_date)
  await callback.answer()


@router.message(CreateSurprise.waiting_for_month)
async def manual_month(message: Message, state: FSMContext):
  await state.update_data(month=message.text)
  keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Change Month", callback_data="change_month")]])
  await message.answer("4️⃣ Enter **Date** (1 to 31):", reply_markup=keyboard)
  await state.set_state(CreateSurprise.waiting_for_date)


@router.message(CreateSurprise.waiting_for_date)
async def get_date(message: Message, state: FSMContext):
  await state.update_data(date=message.text)
  
  keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Change Date", callback_data="change_date")]])
  await message.answer("5️⃣ Enter **Time** (Format: `HH:MM`, e.g., `12:00`):", reply_markup=keyboard)
  await state.set_state(CreateSurprise.waiting_for_time)


@router.callback_query(F.data == "change_date")
async def callback_change_date(callback: CallbackQuery, state: FSMContext):
  keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Cancel", callback_data="cancel_creation")]])
  await callback.message.edit_text("4️⃣ Enter **Date** (1 to 31):", reply_markup=keyboard)
  await state.set_state(CreateSurprise.waiting_for_date)
  await callback.answer()


@router.message(CreateSurprise.waiting_for_time)
async def get_time(message: Message, state: FSMContext):
  await state.update_data(time=message.text)
  
  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(text="☀️ AM", callback_data="ampm_AM"),
              InlineKeyboardButton(text="🌙 PM", callback_data="ampm_PM"),
          ],
          [InlineKeyboardButton(text="⬅️ Change Time", callback_data="change_time")]
      ]
  )
  await message.answer("6️⃣ Select **AM or PM**:", reply_markup=keyboard)
  await state.set_state(CreateSurprise.waiting_for_ampm)


@router.callback_query(F.data == "change_time")
async def callback_change_time(callback: CallbackQuery, state: FSMContext):
  keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Cancel", callback_data="cancel_creation")]])
  await callback.message.edit_text("5️⃣ Enter **Time** (Format: `HH:MM`):", reply_markup=keyboard)
  await state.set_state(CreateSurprise.waiting_for_time)
  await callback.answer()


@router.callback_query(F.data.startswith("ampm_"))
async def get_ampm(callback: CallbackQuery, state: FSMContext):
  ampm = callback.data.split("_")[1]
  data = await state.get_data()
  
  year = data.get("year")
  month = data.get("month").zfill(2)
  day = data.get("date").zfill(2)
  time_str = data.get("time")
  
  try:
    if ampm == "PM" and not time_str.startswith("12"):
      hours, mins = map(int, time_str.split(":"))
      time_str = f"{hours + 12}:{mins:02d}"
    elif ampm == "AM" and time_str.startswith("12"):
      time_str = f"00:{time_str.split(':')[1]}"
  except Exception:
    pass

  target_time = f"{year}-{month}-{day} {time_str}"
  await state.update_data(target_time=target_time)

  keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Change AM/PM", callback_data="change_ampm")]])
  await callback.message.edit_text(f"✅ Schedule set to: {target_time} ({ampm})\n\n7️⃣ Now, type your heartfelt **Birthday Wish / Message**:", reply_markup=keyboard)
  await state.set_state(CreateSurprise.waiting_for_message)
  await callback.answer()


@router.callback_query(F.data == "change_ampm")
async def callback_change_ampm(callback: CallbackQuery, state: FSMContext):
  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [InlineKeyboardButton(text="☀️ AM", callback_data="ampm_AM"), InlineKeyboardButton(text="🌙 PM", callback_data="ampm_PM")]
      ]
  )
  await callback.message.edit_text("6️⃣ Select **AM or PM**:", reply_markup=keyboard)
  await state.set_state(CreateSurprise.waiting_for_ampm)
  await callback.answer()


@router.message(CreateSurprise.waiting_for_message)
async def get_message(message: Message, state: FSMContext):
  await state.update_data(msg=message.text)
  
  keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Change Wish", callback_data="change_wish")]])
  await message.answer("8️⃣ Send a **Photo** for the surprise (Or type `/skip`):", reply_markup=keyboard)
  await state.set_state(CreateSurprise.waiting_for_photo)


@router.callback_query(F.data == "change_wish")
async def callback_change_wish(callback: CallbackQuery, state: FSMContext):
  keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Cancel", callback_data="cancel_creation")]])
  await callback.message.edit_text("7️⃣ Now, type your heartfelt **Birthday Wish / Message**:", reply_markup=keyboard)
  await state.set_state(CreateSurprise.waiting_for_message)
  await callback.answer()


@router.message(CreateSurprise.waiting_for_photo)
async def get_photo(message: Message, state: FSMContext):
  photo_id = message.photo[-1].file_id if message.photo else None
  await state.update_data(photo=photo_id)
  
  keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Change Photo", callback_data="change_photo")]])
  await message.answer("9️⃣ Send a **Video** (Or type `/skip`):", reply_markup=keyboard)
  await state.set_state(CreateSurprise.waiting_for_video)


@router.callback_query(F.data == "change_photo")
async def callback_change_photo(callback: CallbackQuery, state: FSMContext):
  keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Cancel", callback_data="cancel_creation")]])
  await callback.message.edit_text("8️⃣ Send a **Photo** for the surprise (Or type `/skip`):", reply_markup=keyboard)
  await state.set_state(CreateSurprise.waiting_for_photo)
  await callback.answer()


@router.message(CreateSurprise.waiting_for_video)
async def get_video(message: Message, state: FSMContext):
  video_id = message.video.file_id if message.video else None
  await state.update_data(video=video_id)
  
  keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Change Video", callback_data="change_video")]])
  await message.answer("🔟 Send a **Song / Music file** (Or type `/skip`):", reply_markup=keyboard)
  await state.set_state(CreateSurprise.waiting_for_song)


@router.callback_query(F.data == "change_video")
async def callback_change_video(callback: CallbackQuery, state: FSMContext):
  keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Cancel", callback_data="cancel_creation")]])
  await callback.message.edit_text("9️⃣ Send a **Video** (Or type `/skip`):", reply_markup=keyboard)
  await state.set_state(CreateSurprise.waiting_for_video)
  await callback.answer()


@router.message(CreateSurprise.waiting_for_song)
async def get_song(message: Message, state: FSMContext):
  song_id = message.audio.file_id if message.audio else None
  await state.update_data(song=song_id)
  
  keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Change Song", callback_data="change_song")]])
  await message.answer("1️⃣1️⃣ Send a **Voice Note / Audio message** (Or type `/skip`):", reply_markup=keyboard)
  await state.set_state(CreateSurprise.waiting_for_voice)


@router.callback_query(F.data == "change_song")
async def callback_change_song(callback: CallbackQuery, state: FSMContext):
  keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Cancel", callback_data="cancel_creation")]])
  await callback.message.edit_text("🔟 Send a **Song / Music file** (Or type `/skip`):", reply_markup=keyboard)
  await state.set_state(CreateSurprise.waiting_for_song)
  await callback.answer()


@router.message(CreateSurprise.waiting_for_voice)
async def get_voice(message: Message, state: FSMContext):
  user_id = message.from_user.id
  voice_id = message.voice.file_id if message.voice else (message.audio.file_id if message.audio else None)
  
  data = await state.get_data()
  name = data.get("name")
  msg = data.get("msg")
  photo = data.get("photo")
  video = data.get("video")
  song = data.get("song")
  target_time = data.get("target_time")

  surp_id = f"surp_{uuid.uuid4().hex[:6]}"
  surprises_db[surp_id] = {
      "name": name,
      "msg": msg,
      "photo": photo,
      "video": video,
      "song": song,
      "voice": voice_id,
      "target_time": target_time,
  }

  if user_id not in user_created_surprises:
    user_created_surprises[user_id] = []
  user_created_surprises[user_id].append(surp_id)

  bot_info = await message.bot.get_me()
  share_link = f"https://t.me/{bot_info.username}?start={surp_id}"

  preview_keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [InlineKeyboardButton(text="🔍 Preview My Surprise Now", url=share_link)]
      ]
  )

  await message.answer(
      f"🌟 **Your Amazing Birthday Surprise is Ready!**\n\n"
      f"Share link: `{share_link}`\n\n"
      f"👉 Click below to test/preview your own surprise instantly!",
      reply_markup=preview_keyboard,
      parse_mode="Markdown",
  )
  await state.clear()


async def handle(request):
  return web.Response(text="Bot is running!")


async def web_server():
  app = web.Application()
  app.add_routes([web.get("/", handle)])
  runner = web.AppRunner(app)
  await runner.setup()
  port = int(os.environ.get("PORT", 8080))
  site = web.TCPSite(runner, "0.0.0.0", port)
  await site.start()


async def main():
  bot = Bot(token=TOKEN)
  dp = Dispatcher()
  dp.include_router(router)
  await web_server()
  await bot.delete_webhook(drop_pending_updates=True)
  await dp.start_polling(bot)


if __name__ == "__main__":
  asyncio.run(main())
