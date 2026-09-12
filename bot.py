import asyncio
import logging
import uuid
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

# നിങ്ങളുടെ ബോട്ട് ടോക്കൺ ഇവിടെ നൽകിയിരിക്കുന്നു
TOKEN = "8854916574:AAHhpQWzOOH7IKjuitJfS_yspUoWy0z2So4"

# നിങ്ങളുടെ ടെലഗ്രാം യൂസർ ഐഡി ഇവിടെ നൽകിയിരിക്കുന്നു (നിങ്ങൾക്ക് മാത്രം ഫ്രീ ആക്സസ് കിട്ടാൻ)
ADMIN_USER_ID = 1689374364

router = Router()
logging.basicConfig(level=logging.INFO)

surprises_db = {}


class CreateSurprise(StatesGroup):
  waiting_for_name = State()
  waiting_for_message = State()
  waiting_for_photo = State()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
  user_id = message.from_user.id
  args = message.text.split()

  if len(args) > 1 and args[1].startswith("surp_"):
    surp_id = args[1]
    if surp_id in surprises_db:
      data = surprises_db[surp_id]
      # സ്ക്രാച്ച് കാർഡ് ലുക്കിലുള്ള കവർ മെസ്സേജ്
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
          "🎁 **നിങ്ങൾക്കായി ഒരു പിറന്നാൾ സർപ്രൈസ് കാർഡ് വന്നിട്ടുണ്ട്!**\n\nതാഴെ"
          " കാണുന്ന കാർഡ് സ്ക്രാച്ച് ചെയ്ത് നോക്കൂ 👇",
          reply_markup=keyboard,
      )
      return
    else:
      await message.answer("ഈ സർപ്രൈസ് ലിങ്ക് എക്സ്പയർ ആയിരിക്കുന്നു!")
      return

  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="✨ Create Birthday Surprise",
                  callback_data="create_surprise",
              )
          ]
      ]
  )
  await message.answer(
      "🎉 **Birthday Surprise Bot-ലേക്ക് സ്വാഗതം!**\n\nസുഹൃത്തുക്കൾക്കായി"
      " സർപ്രൈസ് ക്രിയേറ്റ് ചെയ്യാൻ താഴെയുള്ള ബട്ടൺ അമർത്തൂ:",
      reply_markup=keyboard,
  )


# സ്ക്രാച്ച് കാർഡ് തുറക്കുമ്പോൾ (Scratch Reveal Effect)
@router.callback_query(F.data.startswith("scratch_"))
async def scratch_card(callback: CallbackQuery):
  surp_id = callback.data.split("_")[1]
  if surp_id in surprises_db:
    data = surprises_db[surp_id]

    await callback.message.edit_text("✨ *Scratched... Revealing surprise!* ⏳")
    await asyncio.sleep(1)

    if data.get("photo"):
      await callback.message.answer_photo(
          photo=data["photo"],
          caption=(
              f"🎉 **Happy Birthday {data['name']}!** 🎉\n\n{data['msg']}\n\n✨"
              " *Special Scratch Surprise!*"
          ),
      )
    else:
      await callback.message.answer(
          f"🎉 **Happy Birthday {data['name']}!** 🎉\n\n{data['msg']}"
      )
    await callback.answer()


@router.callback_query(F.data == "create_surprise")
async def process_creation(callback: CallbackQuery, state: FSMContext):
  user_id = callback.from_user.id

  if user_id == ADMIN_USER_ID:
    await callback.message.answer(
        "👑 [Admin Mode]: നിങ്ങൾക്ക് ഫ്രീയായി സർപ്രൈസ് സെറ്റ് ചെയ്യാം!\n\nആരുടെ"
        " പേരാണ് നൽകേണ്ടത്?"
    )
    await state.set_state(CreateSurprise.waiting_for_name)
    await callback.answer()
  else:
    prices = [LabeledPrice(label="Scratch Surprise Pass", amount=75)]
    await callback.message.answer_invoice(
        title="Birthday Scratch Card Bot",
        description=(
            "സർപ്രൈസ് സ്ക്രാച്ച് കാർഡ് സെറ്റ് ചെയ്യാൻ 75 Telegram Stars"
            " ആവശ്യമാണ്."
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
        "✅ പെയ്‌മെന്റ് വിജയകരമായി പൂർത്തിയായി!\n\nഇനി പിറന്നാൾ ആഘോഷിക്കുന്ന"
        " ആളുടെ പേര് ടൈപ്പ് ചെയ്യൂ:"
    )
    await state.set_state(CreateSurprise.waiting_for_name)


@router.message(CreateSurprise.waiting_for_name)
async def get_surprise_name(message: Message, state: FSMContext):
  await state.update_data(name=message.text)
  await message.answer(
      "അടുത്തതായി ആ വ്യക്തിക്ക് നൽകേണ്ട പിറന്നാൾ ആശംസകൾ ടൈപ്പ് ചെയ്യൂ:"
  )
  await state.set_state(CreateSurprise.waiting_for_message)


@router.message(CreateSurprise.waiting_for_message)
async def get_surprise_message(message: Message, state: FSMContext):
  await state.update_data(msg=message.text)
  await message.answer(
      "അവസാനമായി സ്ക്രാച്ച് കാർഡിനുള്ളിൽ കാണിക്കേണ്ട ഒരു **ഫോട്ടോ** അയച്ചു തരൂ"
      " (അല്ലെങ്കിൽ '/skip' അടിക്കുക):"
  )
  await state.set_state(CreateSurprise.waiting_for_photo)


@router.message(CreateSurprise.waiting_for_photo)
async def get_surprise_photo(message: Message, state: FSMContext):
  user_data = await state.get_data()
  name = user_data.get("name")
  msg = user_data.get("msg")

  photo_id = None
  if message.photo:
    photo_id = message.photo[-1].file_id

  surp_id = f"surp_{uuid.uuid4().hex[:6]}"
  surprises_db[surp_id] = {"name": name, "msg": msg, "photo": photo_id}

  bot_info = await message.bot.get_me()
  share_link = f"https://t.me/{bot_info.username}?start={surp_id}"

  await message.answer(
      f"🌟 **നിങ്ങളുടെ സ്ക്രാച്ച് കാർഡ് സർപ്രൈസ് ലിങ്ക് റെഡിയായി!**\n\nഈ ലിങ്ക്"
      f" പിറന്നാൾക്കാരന് അയച്ചുകൊടുക്കൂ:\n`{share_link}`",
      parse_mode="Markdown",
  )
  await state.clear()


async def main():
  bot = Bot(token=TOKEN)
  dp = Dispatcher()
  dp.include_router(router)
  await bot.delete_webhook(drop_pending_updates=True)
  await dp.start_polling(bot)


if __name__ == "__main__":
  asyncio.run(main())
