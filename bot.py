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
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
)

TOKEN = "8854916574:AAHhpQWzOOH7IKjuitJfS_yspUoWy0z2So4"
ADMIN_USER_ID = 1689374364

router = Router()
logging.basicConfig(level=logging.INFO)

surprises_db = {}


class CreateSurprise(StatesGroup):
  waiting_for_name = State()
  waiting_for_date = State()
  waiting_for_message = State()
  waiting_for_media = State()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
  user_id = message.from_user.id
  args = message.text.split()

  if len(args) > 1 and args[1].startswith("surp_"):
    surp_id = args[1]
    if surp_id in surprises_db:
      data = surprises_db[surp_id]

      # Date, Month, Year & Time Check (Schedule Lock)
      if data.get("target_time"):
        try:
          target_dt = datetime.datetime.strptime(
              data["target_time"], "%Y-%m-%d %H:%M"
          )
          current_dt = datetime.datetime.now()
          if current_dt < target_dt:
            await message.answer(
                f"⏳ **This birthday surprise is locked!**\nIt will open"
                f" automatically on:\n📅 *{data['target_time']}*"
            )
            return
        except Exception:
          pass

      # Scratch Card View
      keyboard = InlineKeyboardMarkup(
          inline_keyboard=[
              [
                  InlineKeyboardButton(
                      text="🎫 🔲🔲🔲🔲🔲 (Scratch Here)",
                      callback_data=f"scratch_{surp_id}",
                  )
              ]
          ]
      )
      await message.answer(
          f"🎁 **You have an exclusive birthday surprise card for"
          f" {data['name']}!**\n\nTap below to scratch and reveal 👇",
          reply_markup=keyboard,
      )
      return
    else:
      await message.answer("This surprise link has expired or is invalid!")
      return

  # Highlighted Main Menu Banner
  highlight_banner = (
      "🌟━━━━━━━━━━━━━━━━━━━🌟\n"
      "   🎉 **ULTIMATE BIRTHDAY SURPRISE BOT** 🎉\n"
      "🌟━━━━━━━━━━━━━━━━━━━🌟\n\n"
      "✨ *Create magical, interactive, and unforgettable birthday surprises"
      " with Photos, Videos, Songs, and Scratch Cards!*\n\n"
      "Choose an option below to get started:"
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
          ]
      ]
  )
  await message.answer(highlight_banner, reply_markup=keyboard)


# How it Works Guide
@router.callback_query(F.data == "how_it_works")
async def show_guide(callback: CallbackQuery):
  guide_text = (
      "📖 **How This Bot Works:**\n\n"
      "1️⃣ **Create:** Click 'Create Surprise' and enter the birthday"
      " person's name.\n"
      "2️⃣ **Schedule with Year:** Set the exact unlock Date & Year (e.g.,"
      " `2026-09-15 00:00`) or skip.\n"
      "3️⃣ **Customize:** Write your wishes and add a Photo, Video, or"
      " Audio/Song!\n"
      "4️⃣ **Share:** Get a unique secure link and send it to your friend.\n"
      "5️⃣ **Surprise:** They open the link and scratch the card to reveal"
      " your gift!"
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


@router.callback_query(F.data.startswith("scratch_"))
async def scratch_card(callback: CallbackQuery):
  surp_id = callback.data.split("_")[1]
  if surp_id in surprises_db:
    data = surprises_db[surp_id]

    await callback.message.edit_text("✨ *Scratched... Revealing surprise!* ⏳")
    await asyncio.sleep(1)

    media_type = data.get("media_type")
    media_id = data.get("media_id")
    caption = f"🎉 **Happy Birthday {data['name']}!** 🎉\n\n{data['msg']}"

    if media_type == "photo":
      await callback.message.answer_photo(
          photo=media_id, caption=caption + "\n\n✨ *Special Scratch Surprise!*"
      )
    elif media_type == "video":
      await callback.message.answer_video(
          video=media_id, caption=caption + "\n\n✨ *Special Scratch Surprise!*"
      )
    elif media_type == "audio":
      await callback.message.answer_audio(
          audio=media_id, caption=caption + "\n\n✨ *Special Scratch Surprise!*"
      )
    else:
      await callback.message.answer(caption)

    await callback.answer()


@router.callback_query(F.data == "create_surprise")
async def process_creation(callback: CallbackQuery, state: FSMContext):
  user_id = callback.from_user.id

  if user_id == ADMIN_USER_ID:
    await callback.message.answer(
        "👑 [Admin Mode]: You can create surprises for free!\n\nEnter the"
        " birthday person's name:"
    )
    await state.set_state(CreateSurprise.waiting_for_name)
    await callback.answer()
  else:
    prices = [LabeledPrice(label="Scratch Surprise Pass", amount=75)]
    await callback.message.answer_invoice(
        title="Birthday Scratch Card Bot",
        description=(
            "Pay 75 Telegram Stars to create your custom birthday scratch"
            " surprise."
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
      "📅 Enter the unlock Date, Year & Time (Format: `YYYY-MM-DD"
      " HH:MM`)\n*(Example: `2026-12-25 00:00`)*\n\n(Or type `/skip` to open"
      " it immediately anytime):"
  )
  await state.set_state(CreateSurprise.waiting_for_date)


@router.message(CreateSurprise.waiting_for_date)
async def get_surprise_date(message: Message, state: FSMContext):
  target_time = None
  if message.text != "/skip":
    target_time = message.text

  await state.update_data(target_time=target_time)
  await message.answer("✍️ Now, type the special birthday wishes/message:")
  await state.set_state(CreateSurprise.waiting_for_message)


@router.message(CreateSurprise.waiting_for_message)
async def get_surprise_message(message: Message, state: FSMContext):
  await state.update_data(msg=message.text)
  await message.answer(
      "📁 Send a media file: You can send a **Photo**, **Video**, or"
      " **Audio/Song** to show inside the scratch card (Or type `/skip`):"
  )
  await state.set_state(CreateSurprise.waiting_for_media)


@router.message(CreateSurprise.waiting_for_media)
async def get_surprise_media(message: Message, state: FSMContext):
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

  bot_info = await message.bot.get_me()
  share_link = f"https://t.me/{bot_info.username}?start={surp_id}"

  await message.answer(
      f"🌟 **Your Scratch Card Surprise is Ready!**\n\nShare this link with"
      f" the birthday person:\n`{share_link}`\n\n👉 *Want to test it yourself?* "
      f"Just click your link above to see how it works!",
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
