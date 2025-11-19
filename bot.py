import os
import logging
from flask import Flask, request
from aiogram import Bot, Dispatcher, types
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import asyncio

# ------------------------------
# CONFIG
# ------------------------------
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

if not BOT_TOKEN or not ADMIN_CHAT_ID:
    raise RuntimeError("BOT_TOKEN / ADMIN_CHAT_ID not set")

WEBHOOK_HOST = "https://captivating-insight-production.up.railway.app"
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = WEBHOOK_HOST + WEBHOOK_PATH

# ------------------------------
# BOT / DISPATCHER
# ------------------------------
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# ------------------------------
# FLASK WEB SERVER
# ------------------------------
app = Flask(__name__)

@app.route("/")
def index():
    return "Bot working (webhook) 💚"

@app.route(WEBHOOK_PATH, methods=["POST"])
async def telegram_webhook():
    update_data = request.get_json()

    if update_data:
        update = types.Update.to_object(update_data)
        await dp.process_update(update)

    return "OK"


# ------------------------------
# STATES
# ------------------------------
class FormLead(StatesGroup):
    name = State()
    phone = State()


# ------------------------------
# START CMD
# ------------------------------
@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    await message.answer("Бот работает по webhook! 👍")


# ------------------------------
# LEAD
# ------------------------------
@dp.message_handler(commands=["lead"])
async def lead_start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Введите ваше имя:")
    await FormLead.name.set()

@dp.message_handler(state=FormLead.name)
async def lead_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите номер телефона:")
    await FormLead.phone.set()

@dp.message_handler(state=FormLead.phone)
async def lead_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    data = await state.get_data()

    await bot.send_message(
        ADMIN_CHAT_ID,
        f"Новая заявка:\nИмя: {data['name']}\nТелефон: {data['phone']}"
    )

    await message.answer("Спасибо! Мы свяжемся с вами.")
    await state.finish()


# ------------------------------
# STARTUP
# ------------------------------
async def on_startup():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(WEBHOOK_URL)

    await bot.send_message(ADMIN_CHAT_ID, "Webhook установлен! 🚀")


# ------------------------------
# RUNNER
# ------------------------------
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(on_startup())

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
