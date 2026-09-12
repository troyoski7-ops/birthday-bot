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
user_created_surprises = {}  # Track user creations for stats


class CreateSurprise(StatesGroup):
  waiting_for_name = State()
  waiting_for_date = State()
  waiting_for_message = State()
  waiting_for_media = State()


# 1. Start & Deep Linking Handler
@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
  user_id = message.from_user.id
  args = message.text.split()

  if len(args) > 1 and args[1].startswith("surp_"):
    surp_id = args[1]
    if surp_id in surprises_db:
      data = surprises_db[surp_id]

      # Advanced Countdown & Date Check
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

      # Magical Gift Box Opening UI
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

  # Ultimate Highlight Banner with Inline Features
  highlight_banner = (
      "🌟━━━━━━━━━━━━━━━━━━━🌟\n"
      "   🎉 **THE ULTIMATE ALL-IN-ONE BIRTHDAY BOT** 🎉\n"
      "🌟━━━━━━━━━━━━━━━━━━━🌟\n\n"
      "✨ *Experience full Telegram capabilities: Inline Search, Gift Boxes,"
      " Scratch Cards, Cake Cutting, Countdown Locks, Media & Stars Payment!* "
      "\n\n"
      "Choose an option below:"
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


# 2. Admin Statistics Dashboard Command (/stats)
@router.message(Command("stats"))
async def cmd_stats(message: Message):
  if message.from_user.id == ADMIN_USER_ID:
    total_surprises = len(surprises_db)
    await message.answer(
        "📊 **Admin Statistics Dashboard:**\n\n"
        f"🎁 Total Surprises Created: `{total_surprises}`\n"
        f"👑 Bot Status: `Online & Fully Operational`\n"
        f"⚡ Hosting: `Render + UptimeRobot Active`",
        parse_mode="Markdown",
    )
  else:
    await message.answer("❌ You are not authorized to view admin stats.")


# 3. Inline Mode Support (Search surprises anywhere on Telegram)
@router.inline_query()
async def inline_search(inline_query: InlineQuery):
  results = []
  query = inline_query.query.lower()
  user_id = inline_query.from_user.id

  # If user has created surprises, show them in inline search
  if user_id in user_id_surprises := user_created_surprises.get(user_id, []):
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


# How it Works Guide
@router.callback_query(F.data == "how_it_works")
async def show_guide(callback: CallbackQuery):
  guide_text = (
      "📖 **How This All-In-One Bot Works:**\n\n"
      "1️⃣ **Create:** Click 'Create Surprise' and enter the name.\n"
      "2️⃣ **Schedule:** Set exact date/year/time with live countdown.\n"
      "3️⃣ **Customize:** Add Photos, Videos, or Audio/Songs!\n"
      "4️⃣ **Inline Search:** Type `@BotUsername` in any chat to share your"
      " links instantly.\n"
      "5️⃣ **Magic Experience:** Gift Box unwrapping, Scratch Cards, and Cake"
      " cutting with ratings!"
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


# Step 2: Gift Box Opened -> Scratch Card
@router.callback_query(F.data.startswith("gift_"))
async def open_gift(callback: CallbackQuery):
  surp_id = callback.data.split("_")[1]
  if surp_id in surprises_db:
    data = surprises_db[surp_id]

    await callback.message.edit_text(
        "📦 *Unwrapping the gift box...* ✨\n🎟️ *Preparing the golden scratch"
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
        f"🎉 **Gift Unwrapped successfully for {data['name']}!** 🎉\n\nA special"
        " scratch card is waiting for you.\n\n👇 *Scratch the card below to"
        " proceed!*",
        reply_markup=scratch_keyboard,
    )
    await callback.answer()


# Step 3: Scratch Card -> Virtual Cake & Candles
@router.callback_query(F.data.startswith("scratch_"))
async def scratch_card(callback: CallbackQuery):
  surp_id = callback.data.split("_")[1]
  if surp_id in surprises_db:
    data = surprises_db[surp_id]

    await callback.message.edit_text(
        "✨ *Card scratched successfully!* 🎫\n🎂 *Lighting up birthday candles"
        " & bringing out the cake...* 🕯️"
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
        f"🎈 **Almost there, {data['name']}!** 🎈\n\nA delicious custom birthday"
        " cake is right here with burning candles. 🎂🕯️\n\n👇 *Tap below to blow"
        " out the candles and cut the cake!*",
        reply_markup=cake_keyboard,
    )
    await callback.answer()


# Step 4: Cake Cutting -> Final Confetti, Media Reveal & Rating Feedback
@router.callback_query(F.data.startswith("cake_"))
async def cut_cake(callback: CallbackQuery):
  surp_id = callback.data.split("_")[1]
  if surp_id in surprises_db:
    data = surprises_db[surp_id]

    await callback.message.edit_text(
        "🎉 *Make a wish! Blow!* 🌬️🎂\n🎊 *Confetti explosion! Cutting the"
        " cake...* 🍰✨"
    )
    await asyncio.sleep(1.5)

    media_type = data.get("media_type")
    media_id = data.get("media_id")
    caption = (
        f"🎊✨ **HAPPY BIRTHDAY {data['name'].upper()}!** ✨🎊\n\n{data['msg']}\n\n💖"
        " *Brought to life with the Ultimate Telegram Birthday Bot!*"
    )

    # Interactive Feedback / Rating Keyboard at the end
    rating_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⭐ 1", callback_data="rate_1"
                ),
                InlineKeyboardButton(
                    text="⭐⭐ 2", callback_data="rate_2"
                ),
                InlineKeyboardButton(
                    text="⭐⭐⭐ 3", callback_data="rate_3"
                ),
                InlineKeyboardButton(
                    text="⭐⭐⭐⭐ 4", callback_data="rate_4"
                ),
                InlineKeyboardButton(
                    text="⭐⭐⭐⭐⭐ 5", callback_data="rate_5"
                ),
            ]
        ]
    )

    if media_type == "photo":
      await callback.message.answer_photo(
          photo=media_id, caption=caption, reply_markup=rating_keyboard
      )
    elif media_type == "video":
      await callback.message.answer_video(
          video=media_id, caption=caption, reply_markup=rating_keyboard
      )
    elif media_type == "audio":
      await callback.message.answer_audio(
          audio=media_id, caption=caption, reply_markup=rating_keyboard
      )
    else:
      await callback.message.answer(caption, reply_markup=rating_keyboard)

    await callback.answer()


# Rating Callback Handler
@router.callback_query(F.data.startswith("rate_"))
async def process_rating(callback: CallbackQuery):
  rating = callback.data.split("_")[1]
  await callback.answer(
      f"🙏 Thank you for rating this surprise {rating} stars! ⭐"
  )
  await callback.message.edit_reply_markup(
      reply_markup=InlineKeyboardMarkup(
          inline_keyboard=[
              [
                  InlineKeyboardButton(
                      text=f"✅ Rated {rating}/5 Stars ⭐",
                      callback_data="rated_done",
                  )
              ]
          ]
      )
  )


@router.callback_query(F.data == "create_surprise")
async def process_creation(callback: CallbackQuery, state: FSMContext):
  user_id = callback.from_user.id

  if user_id == ADMIN_USER_ID:
    await callback.message.answer(
        "👑 [Admin Mode]: You can create ultimate surprises for"
        " free!\n\nEnter the birthday person's name:"
    )
    await state.set_state(CreateSurprise.waiting_for_name)
    await callback.answer()
  else:
    prices = [LabeledPrice(label="Ultimate Surprise Pass", amount=75)]
    await callback.message.answer_invoice(
        title="Ultimate Birthday Bot",
        description=(
            "Pay 75 Telegram Stars to create your custom next-gen magical"
            " birthday surprise."
        ),
        prices=prices,
        currency="XTR",
        payload="scratch_surprise_payment",
    )
    await callback.answer()


@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
  await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message, state: FSMContext):
  if message.successful_payment.invoice_payload == "scratch_surprise_payment":
    await message.answer(
        "✅ Payment successful!\n\nEnter the birthday person's name:"
    )
    await state.set_state(CreateSurprise.waiting_for_name)


@router.message(CreateSurprise.waiting_for_name)
async def get_surprise_name(message: Message, state: FSMContext):
  await state.update_data(name=message.text)
  await message.answer(
      "📅 Enter the unlock Date, Year & Time with Countdown Lock (Format:"
      " `YYYY-MM-DD HH:MM`)\n*(Example: `2026-12-31 00:00`)*\n\n(Or type"
      " `/skip` to open it immediately anytime):"
  )
  await state.set_state(CreateSurprise.waiting_for_date)


@router.message(CreateSurprise.waiting_for_date)
async def get_surprise_date(message: Message, state: FSMContext):
  target_time = None
  if message.text != "/skip":
    target_time = message.text

  await state.update_data(target_time=target_time)
  await message.answer("✍️ Now, type your heartfelt birthday wishes/message:")
  await state.set_state(CreateSurprise.waiting_for_message)


@router.message(CreateSurprise.waiting_for_message)
async def get_surprise_message(message: Message, state: FSMContext):
  await state.update_data(msg=message.text)
  await message.answer(
      "📁 Send a media file: You can send a **Photo**, **Video**, or"
      " **Audio/Song** to show after the cake cutting (Or type `/skip`):"
  )
  await state.set_state(CreateSurprise.waiting_for_media)


@router.message(CreateSurprise.waiting_for_media)
async def get_surprise_media(message: Message, state: FSMContext):
  user_id = message.from_user.id
  user_data = await state.get_data()
  name = user_data.get("name")
  msg = user_data.get("msg")
  target_time = user_data.get("target_time")

  media_type = None
  media_id = None

  if message.photo:
    media_type = "photo"
    media_id = message.photo[-1].file_id
  elif message.video:
    media_type = "video"
    media_id = message.video.file_id
  elif message.audio or message.voice:
    media_type = "audio"
    media_id = (
        message.audio.file_id if message.audio else message.voice.file_id
    )

  surp_id = f"surp_{uuid.uuid4().hex[:6]}"
  surprises_db[surp_id] = {
      "name": name,
      "msg": msg,
      "media_type": media_type,
      "media_id": media_id,
      "target_time": target_time,
  }

  # Track user created surprises for inline search
  if user_id not in user_created_surprises:
    user_created_surprises[user_id] = []
  user_created_surprises[user_id].append(surp_id)

  bot_info = await message.bot.get_me()
  share_link = f"https://t.me/{bot_info.username}?start={surp_id}"

  await message.answer(
      f"🌟 **Your Magical All-in-One Birthday Surprise is Ready!**\n\nShare this"
      f" link with the birthday person:\n`{share_link}`\n\n🔍 *Pro Tip:* You can"
      f" also type `@{bot_info.username}` in any chat to share your surprise"
      " instantly via Inline Search!",
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
