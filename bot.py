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
    BotCommand,
)

TOKEN = "8854916574:AAHhpQWzOOH7IKjuitJfS_yspUoWy0z2So4"
ADMIN_USER_ID = 1689374364

router = Router()
logging.basicConfig(level=logging.INFO)

surprises_db = {}
user_created_surprises = {}
paid_users = set()


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


async def set_bot_commands(bot: Bot):
  commands = [
      BotCommand(command="start", description="🚀 Start / Initialize Hub"),
      BotCommand(command="stats", description="📊 Vault Statistics"),
      BotCommand(command="help", description="📖 Elite Help Guide"),
      BotCommand(command="cancel", description="🛑 Abort Process"),
  ]
  await bot.set_my_commands(commands)


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
  await state.clear()
  user_id = message.from_user.id
  args = message.text.split()

  if len(args) > 1 and args[1].startswith("surp_"):
    surp_id = args[1]
    if surp_id in surprises_db:
      data = surprises_db[surp_id]

      # Allow Admin or the Creator of this specific surprise to bypass time lock instantly
      is_creator = (
          user_id == ADMIN_USER_ID or user_id in data.get("creators", [])
      )

      if data.get("target_time") and not is_creator:
        try:
          time_str = data["target_time"].replace(".", ":")
          target_dt = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M")
          current_dt = datetime.datetime.now()
          if current_dt < target_dt:
            time_left = target_dt - current_dt
            days = time_left.days
            hours = time_left.seconds // 3600
            minutes = (time_left.seconds % 3600) // 60
            await message.answer(
                f"⏳ **This elite birthday portal is currently locked!**\n\n"
                f"🎁 **Recipient:** *{data['name']}*\n"
                f"🔓 **Unlocks On:** *{data['target_time']}*\n"
                f"⏰ **Time Remaining:** *{days} days, {hours} hours, {minutes}"
                f" minutes*",
                parse_mode="Markdown",
            )
            return
        except Exception as e:
          logging.error(f"Time parsing exception bypassed: {e}")

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
          parse_mode="Markdown",
      )
      return
    else:
      await message.answer("This surprise link has expired or is invalid!")
      return

  premium_banner = (
      "💎✨━━━━━━━━━━━━━━━━━━━✨💎\n"
      "     🎉 **ELITE BIRTHDAY SURPRISE HUB** 🎉\n"
      "💎✨━━━━━━━━━━━━━━━━━━━✨💎\n\n"
      "🌟 *Welcome to the world's most advanced interactive Telegram"
      " experience!* \n\n"
      "🎁 **Unleash Next-Gen Magic:**\n"
      "• 📦 *Milestone Gift Box Unwrapping*\n"
      "• 🎫 *Golden Scratch Card Reveal*\n"
      "• 🎂 *Virtual Cake Cutting & Candles*\n"
      "• ⏰ *Precision Countdown & Schedule Locks*\n"
      "• 🎬 *Photos, Videos, Songs & Voice Notes*\n\n"
      "👇 *Select an option from below to explore:*"
  )

  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="✨ Craft Elite Surprise", callback_data="create_surprise"
              ),
              InlineKeyboardButton(
                  text="📊 Vault Analytics", callback_data="check_stats"
              ),
          ],
          [
              InlineKeyboardButton(
                  text="📖 Guide", callback_data="how_it_works"
              ),
              InlineKeyboardButton(
                  text="🛑 Abort Process", callback_data="cancel_creation"
              ),
          ],
          [
              InlineKeyboardButton(
                  text="🔍 Global Inline Search",
                  switch_inline_query_current_chat="",
              )
          ],
      ]
  )
  await message.answer(premium_banner, reply_markup=keyboard)


@router.message(Command("stats"))
async def cmd_stats(message: Message):
  total_surprises = len(surprises_db)
  await message.answer(
      "📊 **Elite Vault Analytics:**\n\n"
      f"💎 Total Surprises Generated: `{total_surprises}`\n"
      f"👑 Core System Status: `Online & Secured 🚀`",
      parse_mode="Markdown",
  )


@router.callback_query(F.data == "check_stats")
async def callback_stats(callback: CallbackQuery):
  total_surprises = len(surprises_db)
  await callback.message.answer(
      "📊 **Elite Vault Analytics:**\n\n"
      f"💎 Total Surprises Generated: `{total_surprises}`\n"
      f"👑 Core System Status: `Online & Secured 🚀`",
      parse_mode="Markdown",
  )
  await callback.answer()


@router.message(Command("help"))
async def cmd_help(message: Message):
  help_text = (
      "📖 **Elite Command Guide:**\n\n"
      "• `/start` - Initialize main luxury menu\n"
      "• `/stats` - View total vault creations\n"
      "• `/cancel` - Terminate active setup sequence\n"
      "• Use left-side menu or inline options for smooth navigation."
  )
  await message.answer(help_text)


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
  await state.clear()
  await message.answer(
      "🛑 Sequence aborted successfully. Send /start to re-initialize."
  )


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
                title=f"💎 Elite Surprise for {data['name']}",
                description=f"Message: {data['msg'][:30]}...",
                input_message_content=InputTextMessageContent(
                    message_text=(
                        f"🎉 *Exclusive luxury birthday portal for*"
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
            title="No Surprises Crafted Yet",
            description="Tap to initialize your first elite creation!",
            input_message_content=InputTextMessageContent(
                message_text=(
                    "✨ Craft your high-end interactive birthday portal now!"
                )
            ),
        )
    )

  await inline_query.answer(results, cache_time=1)


@router.callback_query(F.data == "how_it_works")
async def show_guide(callback: CallbackQuery):
  guide_text = (
      "📖 **Elite Creator Walkthrough:**\n\n"
      "1️⃣ Tap **Craft Elite Surprise**.\n"
      "2️⃣ Enter Name, Schedule Year, Month, Date, Time & AM/PM.\n"
      "3️⃣ Provide your custom Wish, Photo, Video, Song, and Voice Note.\n"
      "4️⃣ Utilize built-in **Change / Back** keys if modifications are required.\n"
      "5️⃣ Distribute your secure access link!"
  )
  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="✨ Start Crafting Now", callback_data="create_surprise"
              )
          ]
      ]
  )
  await callback.message.edit_text(guide_text, reply_markup=keyboard)
  await callback.answer()


# Gift Box Handler (Fixed to always open instantly via new message if edit fails)
@router.callback_query(F.data.startswith("gift_"))
async def open_gift(callback: CallbackQuery):
  surp_id = callback.data.split("_")[1]
  if surp_id in surprises_db:
    data = surprises_db[surp_id]
    await callback.answer("📦 Unwrapping gift box...", show_alert=False)

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
    try:
      await callback.message.edit_text(
          f"🎉 **Gift Unwrapped successfully for {data['name']}!** 🎉\n\n👇"
          " *Scratch the card below to proceed!*",
          reply_markup=scratch_keyboard,
      )
    except Exception:
      await callback.message.answer(
          f"🎉 **Gift Unwrapped successfully for {data['name']}!** 🎉\n\n👇"
          " *Scratch the card below to proceed!*",
          reply_markup=scratch_keyboard,
      )


# Scratch Card Handler
@router.callback_query(F.data.startswith("scratch_"))
async def scratch_card(callback: CallbackQuery):
  surp_id = callback.data.split("_")[1]
  if surp_id in surprises_db:
    data = surprises_db[surp_id]
    await callback.answer("✨ Card scratched!", show_alert=False)

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
    try:
      await callback.message.edit_text(
          f"🎈 **Almost there, {data['name']}!** 🎈\n\n👇 *Tap below to blow out"
          " the candles and cut the cake!*",
          reply_markup=cake_keyboard,
      )
    except Exception:
      await callback.message.answer(
          f"🎈 **Almost there, {data['name']}!** 🎈\n\n👇 *Tap below to blow out"
          " the candles and cut the cake!*",
          reply_markup=cake_keyboard,
      )


# Cake Cutting & Media Delivery Handler
@router.callback_query(F.data.startswith("cake_"))
async def cut_cake(callback: CallbackQuery):
  surp_id = callback.data.split("_")[1]
  if surp_id in surprises_db:
    data = surprises_db[surp_id]
    await callback.answer("🎂 Cutting cake...", show_alert=False)

    caption = (
        f"🎊✨ **HAPPY BIRTHDAY {data['name'].upper()}!** ✨🎊\n\n{data['msg']}"
    )

    try:
      await callback.message.edit_text(
          "🎊✨ **MAKING A WISH & CUTTING CAKE!** ✨🎊"
      )
    except Exception:
      pass

    if data.get("photo"):
      await callback.message.answer_photo(photo=data["photo"], caption=caption)
    if data.get("video"):
      await callback.message.answer_video(
          video=data["video"], caption="🎥 Elite Video Feature"
      )
    if data.get("song"):
      await callback.message.answer_audio(
          audio=data["song"], caption="🎵 Premium Sound Track"
      )
    if data.get("voice"):
      await callback.message.answer_voice(
          voice=data["voice"], caption="🎤 Exclusive Voice Note"
      )

    if not any([
        data.get("photo"),
        data.get("video"),
        data.get("song"),
        data.get("voice"),
    ]):
      await callback.message.answer(caption)


@router.callback_query(F.data == "create_surprise")
async def process_creation(callback: CallbackQuery, state: FSMContext):
  user_id = callback.from_user.id
  if user_id == ADMIN_USER_ID or user_id in paid_users:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Abort & Return", callback_data="cancel_creation"
                )
            ]
        ]
    )
    badge = (
        "👑 [Admin Privilege]"
        if user_id == ADMIN_USER_ID
        else "⭐ [Elite Pass Active]"
    )
    await callback.message.answer(
        f"{badge}\n\n💎 *Step 1/11:* Enter the recipient's full **Name**:",
        reply_markup=keyboard,
    )
    await state.set_state(CreateSurprise.waiting_for_name)
    await callback.answer()
  else:
    prices = [LabeledPrice(label="Elite Surprise Pass", amount=75)]
    await callback.message.answer_invoice(
        title="Elite Birthday Pass",
        description=(
            "Secure 75 Telegram Stars to craft your elite portal and unlock"
            " instant preview."
        ),
        prices=prices,
        currency="XTR",
        payload="scratch_surprise_payment",
    )
    await callback.answer()


@router.callback_query(F.data == "cancel_creation")
async def cancel_creation(callback: CallbackQuery, state: FSMContext):
  await state.clear()
  try:
    await callback.message.edit_text(
        "🛑 Creation sequence terminated. Send /start to restart."
    )
  except Exception:
    await callback.message.answer(
        "🛑 Creation sequence terminated. Send /start to restart."
    )
  await callback.answer()


@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
  await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message, state: FSMContext):
  if message.successful_payment.invoice_payload == "scratch_surprise_payment":
    user_id = message.from_user.id
    paid_users.add(user_id)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Abort", callback_data="cancel_creation"
                )
            ]
        ]
    )
    await message.answer(
        "✅ **Payment Verified Successfully!**\n\n💎 *Step 1/11:* Enter the"
        " recipient's full **Name**:",
        reply_markup=keyboard,
    )
    await state.set_state(CreateSurprise.waiting_for_name)


# 1. Name Step
@router.message(CreateSurprise.waiting_for_name)
async def get_surprise_name(message: Message, state: FSMContext):
  await state.update_data(name=message.text)

  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(text="2026", callback_data="year_2026"),
              InlineKeyboardButton(text="2027", callback_data="year_2027"),
          ],
          [
              InlineKeyboardButton(
                  text="✏️ Type Year Manually", callback_data="year_manual"
              )
          ],
          [
              InlineKeyboardButton(
                  text="⬅️ Change Name", callback_data="change_name"
              )
          ],
      ]
  )
  await message.answer(
      f"💎 Name registered: **{message.text}**\n\n🗓️ *Step 2/11:* Select or type"
      " target **Year**:",
      reply_markup=keyboard,
      parse_mode="Markdown",
  )
  await state.set_state(CreateSurprise.waiting_for_year)


@router.callback_query(F.data == "change_name")
async def callback_change_name(callback: CallbackQuery, state: FSMContext):
  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="⬅️ Abort", callback_data="cancel_creation"
              )
          ]
      ]
  )
  try:
    await callback.message.edit_text(
        "💎 *Step 1/11:* Re-enter recipient's **Name**:", reply_markup=keyboard
    )
  except Exception:
    await callback.message.answer(
        "💎 *Step 1/11:* Re-enter recipient's **Name**:", reply_markup=keyboard
    )
  await state.set_state(CreateSurprise.waiting_for_name)
  await callback.answer()


@router.callback_query(F.data.startswith("year_"))
async def select_year(callback: CallbackQuery, state: FSMContext):
  if callback.data == "year_manual":
    try:
      await callback.message.edit_text(
          "✏️ Please type the target **Year** (e.g., 2026):"
      )
    except Exception:
      await callback.message.answer(
          "✏️ Please type the target **Year** (e.g., 2026):"
      )
    return

  year = callback.data.split("_")[1]
  await state.update_data(year=year)

  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(text="Jan-Apr", callback_data="m_q1"),
              InlineKeyboardButton(text="May-Aug", callback_data="m_q2"),
          ],
          [
              InlineKeyboardButton(text="Sep-Dec", callback_data="m_q3"),
              InlineKeyboardButton(
                  text="✏️ Type Month (1-12)", callback_data="m_manual"
              ),
          ],
          [
              InlineKeyboardButton(
                  text="⬅️ Change Year", callback_data="change_year"
              )
          ],
      ]
  )
  try:
    await callback.message.edit_text(
        f"💎 Year locked: **{year}**\n\n🗓️ *Step 3/11:* Select target"
        f" **Month**:",
        reply_markup=keyboard,
    )
  except Exception:
    await callback.message.answer(
        f"💎 Year locked: **{year}**\n\n🗓️ *Step 3/11:* Select target"
        f" **Month**:",
        reply_markup=keyboard,
    )
  await state.set_state(CreateSurprise.waiting_for_month)
  await callback.answer()


@router.callback_query(F.data == "change_year")
async def callback_change_year(callback: CallbackQuery, state: FSMContext):
  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(text="2026", callback_data="year_2026"),
              InlineKeyboardButton(text="2027", callback_data="year_2027"),
          ],
          [
              InlineKeyboardButton(
                  text="✏️ Type Manual", callback_data="year_manual"
              )
          ],
      ]
  )
  try:
    await callback.message.edit_text(
        "🗓️ *Step 2/11:* Select or type target **Year**:", reply_markup=keyboard
    )
  except Exception:
    await callback.message.answer(
        "🗓️ *Step 2/11:* Select or type target **Year**:", reply_markup=keyboard
    )
  await state.set_state(CreateSurprise.waiting_for_year)
  await callback.answer()


@router.message(CreateSurprise.waiting_for_year)
async def manual_year(message: Message, state: FSMContext):
  await state.update_data(year=message.text)
  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="⬅️ Change Year", callback_data="change_year"
              )
          ]
      ]
  )
  await message.answer(
      "🗓️ *Step 3/11:* Enter target **Month** (1 to 12):", reply_markup=keyboard
  )
  await state.set_state(CreateSurprise.waiting_for_month)


@router.callback_query(F.data.startswith("m_"))
async def select_month(callback: CallbackQuery, state: FSMContext):
  if callback.data == "m_q1":
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="1 (Jan)", callback_data="mo_1"),
                InlineKeyboardButton(text="2 (Feb)", callback_data="mo_2"),
            ],
            [
                InlineKeyboardButton(text="3 (Mar)", callback_data="mo_3"),
                InlineKeyboardButton(text="4 (Apr)", callback_data="mo_4"),
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Change Month", callback_data="change_month"
                )
            ],
        ]
    )
    try:
      await callback.message.edit_text("🗓️ Select Month:", reply_markup=kb)
    except Exception:
      await callback.message.answer("🗓️ Select Month:", reply_markup=kb)
    return
  elif callback.data == "m_q2":
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="5 (May)", callback_data="mo_5"),
                InlineKeyboardButton(text="6 (Jun)", callback_data="mo_6"),
            ],
            [
                InlineKeyboardButton(text="7 (Jul)", callback_data="mo_7"),
                InlineKeyboardButton(text="8 (Aug)", callback_data="mo_8"),
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Change Month", callback_data="change_month"
                )
            ],
        ]
    )
    try:
      await callback.message.edit_text("🗓️ Select Month:", reply_markup=kb)
    except Exception:
      await callback.message.answer("🗓️ Select Month:", reply_markup=kb)
    return
  elif callback.data == "m_q3":
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="9 (Sep)", callback_data="mo_9"),
                InlineKeyboardButton(text="10 (Oct)", callback_data="mo_10"),
            ],
            [
                InlineKeyboardButton(text="11 (Nov)", callback_data="mo_11"),
                InlineKeyboardButton(text="12 (Dec)", callback_data="mo_12"),
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Change Month", callback_data="change_month"
                )
            ],
        ]
    )
    try:
      await callback.message.edit_text("🗓️ Select Month:", reply_markup=kb)
    except Exception:
      await callback.message.answer("🗓️ Select Month:", reply_markup=kb)
    return
  elif callback.data == "m_manual":
    try:
      await callback.message.edit_text("✏️ Type Month number (1 to 12):")
    except Exception:
      await callback.message.answer("✏️ Type Month number (1 to 12):")
    return
  await callback.answer()


@router.callback_query(F.data == "change_month")
async def callback_change_month(callback: CallbackQuery, state: FSMContext):
  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(text="Jan-Apr", callback_data="m_q1"),
              InlineKeyboardButton(text="May-Aug", callback_data="m_q2"),
          ],
          [
              InlineKeyboardButton(text="Sep-Dec", callback_data="m_q3"),
              InlineKeyboardButton(
                  text="✏️ Type Manual", callback_data="m_manual"
              ),
          ],
      ]
  )
  try:
    await callback.message.edit_text(
        "🗓️ *Step 3/11:* Select target **Month**:", reply_markup=keyboard
    )
  except Exception:
    await callback.message.answer(
        "🗓️ *Step 3/11:* Select target **Month**:", reply_markup=keyboard
    )
  await state.set_state(CreateSurprise.waiting_for_month)
  await callback.answer()


@router.callback_query(F.data.startswith("mo_"))
async def set_month_callback(callback: CallbackQuery, state: FSMContext):
  month = callback.data.split("_")[1]
  await state.update_data(month=month)

  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="⬅️ Change Month", callback_data="change_month"
              )
          ]
      ]
  )
  try:
    await callback.message.edit_text(
        f"💎 Month locked: **{month}**\n\n🗓️ *Step 4/11:* Enter target **Date**"
        " (1-31):",
        reply_markup=keyboard,
    )
  except Exception:
    await callback.message.answer(
        f"💎 Month locked: **{month}**\n\n🗓️ *Step 4/11:* Enter target **Date**"
        " (1-31):",
        reply_markup=keyboard,
    )
  await state.set_state(CreateSurprise.waiting_for_date)
  await callback.answer()


@router.message(CreateSurprise.waiting_for_month)
async def manual_month(message: Message, state: FSMContext):
  await state.update_data(month=message.text)
  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="⬅️ Change Month", callback_data="change_month"
              )
          ]
      ]
  )
  await message.answer(
      "🗓️ *Step 4/11:* Enter target **Date** (1 to 31):", reply_markup=keyboard
  )
  await state.set_state(CreateSurprise.waiting_for_date)


@router.message(CreateSurprise.waiting_for_date)
async def get_date(message: Message, state: FSMContext):
  await state.update_data(date=message.text)

  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="⬅️ Change Date", callback_data="change_date"
              )
          ]
      ]
  )
  await message.answer(
      "⏰ *Step 5/11:* Enter target **Time** (Format: `HH:MM`, e.g., `12:00`):",
      reply_markup=keyboard,
  )
  await state.set_state(CreateSurprise.waiting_for_time)


@router.callback_query(F.data == "change_date")
async def callback_change_date(callback: CallbackQuery, state: FSMContext):
  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="⬅️ Abort", callback_data="cancel_creation"
              )
          ]
      ]
  )
  try:
    await callback.message.edit_text(
        "🗓️ *Step 4/11:* Enter target **Date** (1 to 31):", reply_markup=keyboard
    )
  except Exception:
    await callback.message.answer(
        "🗓️ *Step 4/11:* Enter target **Date** (1 to 31):", reply_markup=keyboard
    )
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
          [
              InlineKeyboardButton(
                  text="⬅️ Change Time", callback_data="change_time"
              )
          ],
      ]
  )
  await message.answer(
      "☀️🌙 *Step 6/11:* Select **AM or PM**:", reply_markup=keyboard
  )
  await state.set_state(CreateSurprise.waiting_for_ampm)


@router.callback_query(F.data == "change_time")
async def callback_change_time(callback: CallbackQuery, state: FSMContext):
  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="⬅️ Abort", callback_data="cancel_creation"
              )
          ]
      ]
  )
  try:
    await callback.message.edit_text(
        "⏰ *Step 5/11:* Enter target **Time** (Format: `HH:MM`):",
        reply_markup=keyboard,
    )
  except Exception:
    await callback.message.answer(
        "⏰ *Step 5/11:* Enter target **Time** (Format: `HH:MM`):",
        reply_markup=keyboard,
    )
  await state.set_state(CreateSurprise.waiting_for_time)
  await callback.answer()


@router.callback_query(F.data.startswith("ampm_"))
async def get_ampm(callback: CallbackQuery, state: FSMContext):
  ampm = callback.data.split("_")[1]
  data = await state.get_data()

  year = data.get("year")
  month = data.get("month").zfill(2)
  day = data.get("date").zfill(2)
  time_str = data.get("time").replace(".", ":")

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

  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="⬅️ Change AM/PM", callback_data="change_ampm"
              )
          ]
      ]
  )
  try:
    await callback.message.edit_text(
        f"✅ Schedule locked: `{target_time} ({ampm})`\n\n✍️ *Step 7/11:* Type"
        " your heartfelt **Birthday Wish / Message**:",
        reply_markup=keyboard,
    )
  except Exception:
    await callback.message.answer(
        f"✅ Schedule locked: `{target_time} ({ampm})`\n\n✍️ *Step 7/11:* Type"
        " your heartfelt **Birthday Wish / Message**:",
        reply_markup=keyboard,
    )
  await state.set_state(CreateSurprise.waiting_for_message)
  await callback.answer()


@router.callback_query(F.data == "change_ampm")
async def callback_change_ampm(callback: CallbackQuery, state: FSMContext):
  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(text="☀️ AM", callback_data="ampm_AM"),
              InlineKeyboardButton(text="🌙 PM", callback_data="ampm_PM"),
          ]
      ]
  )
  try:
    await callback.message.edit_text(
        "☀️🌙 *Step 6/11:* Select **AM or PM**:", reply_markup=keyboard
    )
  except Exception:
    await callback.message.answer(
        "☀️🌙 *Step 6/11:* Select **AM or PM**:", reply_markup=keyboard
    )
  await state.set_state(CreateSurprise.waiting_for_ampm)
  await callback.answer()


@router.message(CreateSurprise.waiting_for_message)
async def get_message(message: Message, state: FSMContext):
  await state.update_data(msg=message.text)

  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="⬅️ Change Wish", callback_data="change_wish"
              )
          ]
      ]
  )
  await message.answer(
      "📸 *Step 8/11:* Send your elite **Photo** attachment (Or type"
      " `/skip`):",
      reply_markup=keyboard,
  )
  await state.set_state(CreateSurprise.waiting_for_photo)


@router.callback_query(F.data == "change_wish")
async def callback_change_wish(callback: CallbackQuery, state: FSMContext):
  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="⬅️ Abort", callback_data="cancel_creation"
              )
          ]
      ]
  )
  try:
    await callback.message.edit_text(
        "✍️ *Step 7/11:* Re-type your **Birthday Wish / Message**:",
        reply_markup=keyboard,
    )
  except Exception:
    await callback.message.answer(
        "✍️ *Step 7/11:* Re-type your **Birthday Wish / Message**:",
        reply_markup=keyboard,
    )
  await state.set_state(CreateSurprise.waiting_for_message)
  await callback.answer()


@router.message(CreateSurprise.waiting_for_photo)
async def get_photo(message: Message, state: FSMContext):
  photo_id = message.photo[-1].file_id if message.photo else None
  await state.update_data(photo=photo_id)

  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="⬅️ Change Photo", callback_data="change_photo"
              )
          ]
      ]
  )
  await message.answer(
      "🎬 *Step 9/11:* Send your cinematic **Video** attachment (Or type"
      " `/skip`):",
      reply_markup=keyboard,
  )
  await state.set_state(CreateSurprise.waiting_for_video)


@router.callback_query(F.data == "change_photo")
async def callback_change_photo(callback: CallbackQuery, state: FSMContext):
  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="⬅️ Abort", callback_data="cancel_creation"
              )
          ]
      ]
  )
  try:
    await callback.message.edit_text(
        "📸 *Step 8/11:* Send your elite **Photo** attachment (Or type"
        " `/skip`):",
        reply_markup=keyboard,
    )
  except Exception:
    await callback.message.answer(
        "📸 *Step 8/11:* Send your elite **Photo** attachment (Or type"
        " `/skip`):",
        reply_markup=keyboard,
    )
  await state.set_state(CreateSurprise.waiting_for_photo)
  await callback.answer()


@router.message(CreateSurprise.waiting_for_video)
async def get_video(message: Message, state: FSMContext):
  video_id = message.video.file_id if message.video else None
  await state.update_data(video=video_id)

  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="⬅️ Change Video", callback_data="change_video"
              )
          ]
      ]
  )
  await message.answer(
      "🎵 *Step 10/11:* Send your background **Song / Music file** (Or type"
      " `/skip`):",
      reply_markup=keyboard,
  )
  await state.set_state(CreateSurprise.waiting_for_song)


@router.callback_query(F.data == "change_video")
async def callback_change_video(callback: CallbackQuery, state: FSMContext):
  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="⬅️ Abort", callback_data="cancel_creation"
              )
          ]
      ]
  )
  try:
    await callback.message.edit_text(
        "🎬 *Step 9/11:* Send your cinematic **Video** attachment (Or type"
        " `/skip`):",
        reply_markup=keyboard,
    )
  except Exception:
    await callback.message.answer(
        "🎬 *Step 9/11:* Send your cinematic **Video** attachment (Or type"
        " `/skip`):",
        reply_markup=keyboard,
    )
  await state.set_state(CreateSurprise.waiting_for_video)
  await callback.answer()


@router.message(CreateSurprise.waiting_for_song)
async def get_song(message: Message, state: FSMContext):
  song_id = message.audio.file_id if message.audio else None
  await state.update_data(song=song_id)

  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="⬅️ Change Song", callback_data="change_song"
              )
          ]
      ]
  )
  await message.answer(
      "🎤 *Step 11/11:* Send your personal **Voice Note / Audio message** (Or"
      " type `/skip`):",
      reply_markup=keyboard,
  )
  await state.set_state(CreateSurprise.waiting_for_voice)


@router.callback_query(F.data == "change_song")
async def callback_change_song(callback: CallbackQuery, state: FSMContext):
  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="⬅️ Abort", callback_data="cancel_creation"
              )
          ]
      ]
  )
  try:
    await callback.message.edit_text(
        "🎵 *Step 10/11:* Send your background **Song / Music file** (Or type"
        " `/skip`):",
        reply_markup=keyboard,
    )
  except Exception:
    await callback.message.answer(
        "🎵 *Step 10/11:* Send your background **Song / Music file** (Or type"
        " `/skip`):",
        reply_markup=keyboard,
    )
  await state.set_state(CreateSurprise.waiting_for_song)
  await callback.answer()


@router.message(CreateSurprise.waiting_for_voice)
async def get_voice(message: Message, state: FSMContext):
  user_id = message.from_user.id
  voice_id = (
      message.voice.file_id
      if message.voice
      else (message.audio.file_id if message.audio else None)
  )

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
      "creators": [user_id],  # This ensures the creator can open it instantly!
  }

  if user_id not in user_created_surprises:
    user_created_surprises[user_id] = []
  user_created_surprises[user_id].append(surp_id)

  bot_info = await message.bot.get_me()
  share_link = f"https://t.me/{bot_info.username}?start={surp_id}"

  preview_keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="🔍 Preview Elite Portal Now", url=share_link
              )
          ]
      ]
  )

  await message.answer(
      f"💎✨ **Your Elite Birthday Portal is Fully Secured!** ✨💎\n\nSecure"
      f" Access Link:\n`{share_link}`\n\n👉 *Tap below to experience your"
      " luxury creation instantly!*",
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

  await set_bot_commands(bot)

  await web_server()
  await bot.delete_webhook(drop_pending_updates=True)
  await dp.start_polling(bot)


if __name__ == "__main__":
  asyncio.run(main())
