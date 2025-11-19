import os
import logging
from flask import Flask, request
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
)
from aiogram.dispatcher.filters.state import State, StatesGroup
import asyncio

# ---------------------------------------------
# НАСТРОЙКИ
# ---------------------------------------------
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

if not BOT_TOKEN or not ADMIN_CHAT_ID:
    raise RuntimeError("❌ BOT_TOKEN или ADMIN_CHAT_ID не заданы!")

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# ---------------------------------------------
# FLASK ПРИЁМНИК WEBHOOK
# ---------------------------------------------
app = Flask(__name__)

@app.route("/")
def home():
    return "СК ВМЕСТЕ: webhook OK"

@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    json_data = request.json
    asyncio.run(dp.process_update(types.Update(**json_data)))
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
        "Помогу рассчитать стоимость дома, подобрать проект или заказать проектирование.\n"
        "Выберите действие 👇"
    )
    await message.answer(text, reply_markup=main_menu())

# ---------------------------------------------
# О КОМПАНИИ
# ---------------------------------------------
@dp.message_handler(lambda m: m.text == "📋 О компании")
async def about(message: types.Message):
    text = (
        "🏗 Строительная компания СК «Вместе» — это команда архитекторов, инженеров и специалистов, которые создают надёжные дома 🏡, продуманные проекты 📐 и комфортные пространства для жизни..."
    )
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("📝 Оставить заявку", callback_data="lead_open"),
        InlineKeyboardButton("💬 Написать нам", url="https://t.me/skVmeste")
    )
    await message.answer(text, reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == "lead_open")
async def open_lead(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.finish()
    await call.message.answer("✍️ Введите ваше имя:")
    await FormLead.name.set()

# ---------------------------------------------
# КАТАЛОГ
# ---------------------------------------------
@dp.message_handler(lambda m: m.text == "📁 Каталог проектов")
async def catalog(message: types.Message):
    await message.answer("📂 Каталог: https://disk.yandex.ru/i/UBQkSxjZVyUKPw")

# ---------------------------------------------
# САЙТЫ
# ---------------------------------------------
@dp.message_handler(lambda m: m.text == "🌐 Сайты компании")
async def sites(message: types.Message):
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("🏠 СК «Вместе»", url="https://ск-вместе.рф"),
        InlineKeyboardButton("📐 Проектирование", url="https://ск-вместе-проектирование.рф")
    )
    await message.answer("🌐 Наши сайты:", reply_markup=kb)

# ---------------------------------------------
# КОНТАКТЫ
# ---------------------------------------------
@dp.message_handler(lambda m: m.text == "📞 Контакты")
async def contacts(message: types.Message):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("💬 Написать", url="https://t.me/skVmeste"))
    await message.answer(
        "📞 Контакты:\n📱 +7 (918) 538-14-55\n📍 Ростов-на-Дону, Береговая 8 (Риверсайд), офис 512",
        reply_markup=kb
    )

# ---------------------------------------------
# СТАРТ — УСТАНОВКА WEBHOOK
# ---------------------------------------------
async def on_startup():
    webhook_url = f"https://{os.getenv('RAILWAY_PUBLIC_DOMAIN')}/webhook/{BOT_TOKEN}"
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(webhook_url)
    await bot.send_message(ADMIN_CHAT_ID, f"✅ Webhook установлен:\n{webhook_url}")

# ---------------------------------------------
# СТАРТ FLASK
# ---------------------------------------------
if __name__ == "__main__":
    asyncio.run(on_startup())
    app.run(host="0.0.0.0", port=8080)
