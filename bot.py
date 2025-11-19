import os
import logging
from flask import Flask, request
from aiogram import Bot, Dispatcher, types
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
)
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import executor

# ---------------------------------------------
# ЛОГИ
# ---------------------------------------------
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

if not BOT_TOKEN or not ADMIN_CHAT_ID:
    raise RuntimeError("BOT_TOKEN или ADMIN_CHAT_ID не заданы")

WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")   # например https://captivating-insight-production.up.railway.app
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = WEBHOOK_HOST + WEBHOOK_PATH

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# ---------------------------------------------
# FLASK — принимает webhook Telegram
# ---------------------------------------------
app = Flask(__name__)

@app.route("/")
def index():
    return "Бот СК Вместе запущен и слушает webhook 💚"

@app.route(WEBHOOK_PATH, methods=["POST"])
async def webhook():
    update = types.Update(**request.json)
    await dp.process_update(update)
    return "OK", 200

# ---------------------------------------------
# ОСНОВНОЕ МЕНЮ
# ---------------------------------------------
def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("📋 О компании", "📁 Каталог проектов")
    kb.row("🏗 Расчёт стоимости дома", "✏️ Архитектурное проектирование")
    kb.row("🌐 Сайты компании", "📞 Контакты")
    return kb

# ---------------------------------------------
# СОСТОЯНИЯ
# ---------------------------------------------
class QuizBuild(StatesGroup):
    q1 = State(); q2 = State(); q3 = State(); q4 = State(); q5 = State(); phone = State()

class QuizProject(StatesGroup):
    q1 = State(); q2 = State(); q3 = State(); q4 = State(); q5 = State(); phone = State()

class FormLead(StatesGroup):
    name = State()
    phone = State()

# ---------------------------------------------
# /START
# ---------------------------------------------
@dp.message_handler(commands=["start", "help"])
async def cmd_start(message: types.Message):
    text = (
        "👋 Привет! Я бот компании <b>СК «Вместе»</b>\n\n"
        "Помогу рассчитать стоимость дома, подобрать проект или заказать архитектурное решение.\n\n"
        "Выберите действие из меню ниже 👇\n\n"
        "📝 Или оставьте заявку здесь 👉 /lead"
    )
    await message.answer(text, reply_markup=main_menu())

# ---------------------------------------------
# О КОМПАНИИ
# ---------------------------------------------
@dp.message_handler(lambda m: m.text == "📋 О компании")
async def about(message: types.Message):
    text = (
        "🏗 Строительная компания СК «Вместе» — это команда архитекторов, инженеров и специалистов..."
        "\n\n(ТВОЙ НОВЫЙ ТЕКСТ ЗДЕСЬ)"
    )

    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("📝 Оставить заявку", callback_data="lead_open"),
        InlineKeyboardButton("💬 Написать нам", url="https://t.me/skVmeste"),
    )

    await message.answer(text, reply_markup=kb)

# ---------------------------------------------
# ОСТАЛЬНЫЕ ФУНКЦИИ (квизы, контакты, заявки)
# — всё остаётся как у тебя, можно вставить весь блок сюда
# ---------------------------------------------

# ---------------------------------------------
# СТАРТУЕМ AIOGRAM + УСТАНАВЛИВАЕМ WEBHOOK
# ---------------------------------------------
async def on_startup(dp):
    logging.warning("Удаляю старый webhook...")
    await bot.delete_webhook()

    logging.warning(f"Устанавливаю новый webhook: {WEBHOOK_URL}")
    await bot.set_webhook(WEBHOOK_URL)

    await bot.send_message(ADMIN_CHAT_ID, "✅ Бот СК «Вместе» запущен (WEBHOOK).")

if __name__ == "__main__":
    from threading import Thread

    def run_flask():
        port = int(os.environ.get("PORT", 8080))
        app.run(host="0.0.0.0", port=port)

    Thread(target=run_flask).start()

    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
