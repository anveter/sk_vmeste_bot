import os
import logging
from flask import Flask, request
from aiogram import Bot, Dispatcher, types
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

# ---------------------------------------------------
# ЛОГИ
# ---------------------------------------------------
logging.basicConfig(level=logging.INFO)

# ---------------------------------------------------
# ENV ПЕРЕМЕННЫЕ
# ---------------------------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")     # https://....railway.app

if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN не найден в переменных окружения")

if not ADMIN_CHAT_ID:
    raise RuntimeError("❌ ADMIN_CHAT_ID не найден в переменных окружения")

if not WEBHOOK_HOST:
    raise RuntimeError("❌ WEBHOOK_HOST не найден в переменных окружения")

WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = WEBHOOK_HOST + WEBHOOK_PATH

# ---------------------------------------------------
# AIOGRAM
# ---------------------------------------------------
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# ---------------------------------------------------
# FLASK — приём webhook Telegram
# ---------------------------------------------------
app = Flask(__name__)

@app.route("/")
def root():
    return "💚 SK Vmeste bot is running via webhook!"

@app.route(WEBHOOK_PATH, methods=["POST"])
async def telegram_webhook():
    json_data = request.get_json()
    if not json_data:
        return "No JSON", 400

    update = types.Update(**json_data)
    await dp.process_update(update)
    return "OK", 200

# ---------------------------------------------------
# КЛАВИАТУРЫ
# ---------------------------------------------------
def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("📋 О компании", "📁 Каталог проектов")
    kb.row("🏗 Расчёт стоимости дома", "✏️ Архитектурное проектирование")
    kb.row("🌐 Сайты компании", "📞 Контакты")
    return kb

# ---------------------------------------------------
# СОСТОЯНИЯ (можно расширять)
# ---------------------------------------------------
class QuizBuild(StatesGroup):
    q1 = State()
    q2 = State()
    q3 = State()
    q4 = State()
    q5 = State()
    phone = State()

class QuizProject(StatesGroup):
    q1 = State()
    q2 = State()
    q3 = State()
    q4 = State()
    q5 = State()
    phone = State()

class FormLead(StatesGroup):
    name = State()
    phone = State()

# ---------------------------------------------------
# /START
# ---------------------------------------------------
@dp.message_handler(commands=["start", "help"])
async def cmd_start(message: types.Message):
    text = (
        "👋 Привет! Я бот компании <b>СК «Вместе»</b>\n\n"
        "Помогу рассчитать стоимость дома, подобрать проект или заказать архитектурное решение.\n\n"
        "Выберите действие из меню ниже 👇\n\n"
        "📝 Или оставьте заявку здесь 👉 /lead"
    )
    await message.answer(text, reply_markup=main_menu())

# ---------------------------------------------------
# О КОМПАНИИ
# ---------------------------------------------------
@dp.message_handler(lambda m: m.text == "📋 О компании")
async def about_company(message: types.Message):
    text = (
        "🏗 Строительная компания СК «Вместе» — команда архитекторов, инженеров и специалистов.\n\n"
        "Мы проектируем и строим современные загородные дома.\n"
        "Работаем под ключ: от выбора участка до сдачи интерьеров.\n\n"
        "✨ (Здесь будет твой расширенный текст)"
    )

    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("📝 Оставить заявку", callback_data="lead_open"),
        InlineKeyboardButton("💬 Написать нам", url="https://t.me/skVmeste"),
    )

    await message.answer(text, reply_markup=kb)

# ---------------------------------------------------
# CALLBACK: открыть заявку
# ---------------------------------------------------
@dp.callback_query_handler(lambda c: c.data == "lead_open")
async def cb_lead_open(callback: types.CallbackQuery):
    await callback.message.answer(
        "Введите ваше имя:",
    )
    await FormLead.name.set()
    await callback.answer()

# ---------------------------------------------------
# Форма лидов (минимальная)
# ---------------------------------------------------
@dp.message_handler(state=FormLead.name)
async def form_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите номер телефона:")
    await FormLead.phone.set()

@dp.message_handler(state=FormLead.phone)
async def form_phone(message: types.Message, state: FSMContext):
    data = await state.get_data()
    name = data.get("name")
    phone = message.text

    await bot.send_message(
        ADMIN_CHAT_ID,
        f"📨 Новая заявка:\n\n👤 Имя: {name}\n📞 Телефон: {phone}"
    )

    await message.answer("Спасибо! Наш менеджер скоро с вами свяжется 💚")
    await state.finish()

# ---------------------------------------------------
# on_startup — SET WEBHOOK
# ---------------------------------------------------
async def on_startup():
    logging.warning("Удаляю старый Webhook…")
    await bot.delete_webhook()

    logging.warning(f"Устанавливаю новый Webhook:\n{WEBHOOK_URL}")
    await bot.set_webhook(WEBHOOK_URL)

    await bot.send_message(ADMIN_CHAT_ID, "⚡ Бот СК «Вместе» запущен (webhook).")


# ---------------------------------------------------
# MAIN — только FLASK! (БЕЗ POLLING)
# ---------------------------------------------------
if __name__ == "__main__":
    import asyncio

    # запускаем установку вебхука перед стартом Flask
    loop = asyncio.get_event_loop()
    loop.run_until_complete(on_startup())

    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
