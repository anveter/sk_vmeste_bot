
# FULL WEBHOOK BOT WITH QUIZZES + MONITORING + AUTO-LOGGING
import os
import logging
import asyncio
from flask import Flask, request
from aiogram import Bot, Dispatcher, types
from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.executor import start_webhook

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")

# ENV
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

BASE_WEBHOOK = "https://skvmestebot-production.up.railway.app/webhook/"
WEBHOOK_URL = BASE_WEBHOOK + BOT_TOKEN
WEBHOOK_PATH = "/webhook/" + BOT_TOKEN
HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", 8080))

if not BOT_TOKEN or not ADMIN_CHAT_ID:
    raise RuntimeError("Missing BOT_TOKEN or ADMIN_CHAT_ID")

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
app = Flask(__name__)

#############################
# HEALTHCHECK
#############################
@app.route("/healthz")
def health():
    logging.info("Healthcheck OK")
    return "OK", 200

#############################
# WEBHOOK RECEIVER
#############################
@app.route(WEBHOOK_PATH, methods=["POST"])
def receive_webhook():
    update = types.Update.de_json(request.get_json(force=True))
    dp.process_update(update)
    return "OK", 200

#############################
# AUTO CHECK WEBHOOK
#############################
async def monitor_webhook():
    await asyncio.sleep(10)
    while True:
        try:
            info = await bot.get_webhook_info()
            if info.url != WEBHOOK_URL:
                logging.warning("Webhook lost. Restoring...")
                await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
                await bot.send_message(ADMIN_CHAT_ID, "⚠️ Webhook был потерян и восстановлен.")
            else:
                logging.info("Webhook OK")
        except Exception as e:
            logging.error(f"Webhook check error: {e}")
        await asyncio.sleep(300)

#############################
# STATES (QUIZZES)
#############################
class QuizBuild(StatesGroup):
    q1 = State(); q2 = State(); q3 = State(); q4 = State(); q5 = State(); phone = State()

class QuizProject(StatesGroup):
    q1 = State(); q2 = State(); q3 = State(); q4 = State(); q5 = State(); phone = State()

class FormLead(StatesGroup):
    name = State()
    phone = State()

#############################
# KEYBOARDS
#############################
def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("📋 О компании", "📁 Каталог проектов")
    kb.row("🏗 Расчёт стоимости дома", "✏️ Архитектурное проектирование")
    kb.row("🌐 Сайты компании", "📞 Контакты")
    return kb

def build_keyboard(options):
    kb = InlineKeyboardMarkup(row_width=2)
    for o in options: kb.add(InlineKeyboardButton(o, callback_data=o))
    return kb

def phone_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(KeyboardButton("📱 Отправить телефон", request_contact=True))
    kb.add(KeyboardButton("Отправлю позже"))
    return kb

#############################
# START
#############################
@dp.message_handler(commands=["start"])
async def start_cmd(msg: types.Message):
    await msg.answer("👋 Привет! Я бот СК «Вместе». Выберите действие:", reply_markup=main_menu())

#############################
# ABOUT COMPANY
#############################
@dp.message_handler(lambda m: m.text == "📋 О компании")
async def about(msg: types.Message):
    text = (
        "🏗 Строительная компания СК «Вместе» — это команда архитекторов, инженеров и специалистов..."
    )
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("📝 Оставить заявку", callback_data="lead_open"),
        InlineKeyboardButton("💬 Написать нам", url="https://t.me/skVmeste")
    )
    await msg.answer(text, reply_markup=kb)

#############################
# CONTACTS
#############################
@dp.message_handler(lambda m: m.text == "📞 Контакты")
async def contacts(msg: types.Message):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("💬 Написать в Telegram", url="https://t.me/skVmeste"))
    await msg.answer(
        "📱 +7 (928) 621-11-05
📱 +7 (919) 892-94-02
📱 +7 (918) 538-14-55", reply_markup=kb)

#############################
# CATALOG
#############################
@dp.message_handler(lambda m: m.text == "📁 Каталог проектов")
async def catalog(msg: types.Message):
    await msg.answer("📂 Каталог проектов: https://disk.yandex.ru/i/UBQkSxjZVyUKPw")

#############################
# QUIZ 1 — BUILD
#############################
@dp.message_handler(lambda m: m.text == "🏗 Расчёт стоимости дома")
async def quiz_build_start(msg: types.Message, state: FSMContext):
    await state.finish()
    await msg.answer("Вопрос 1: Этажность?", reply_markup=build_keyboard(["1 этаж", "С мансардой", "2 этажа"]))
    await QuizBuild.q1.set()

@dp.callback_query_handler(state=QuizBuild.q1)
async def q1(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(q1=call.data)
    await call.message.edit_text("Материал?")
    await call.message.edit_reply_markup(build_keyboard(["Кирпич", "Монолит", "Газобетон", "Пока не определился"]))
    await QuizBuild.q2.set()

#############################
# LEAD
#############################
@dp.callback_query_handler(lambda c: c.data == "lead_open")
async def lead_open(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer("Введите имя:")
    await FormLead.name.set()

@dp.message_handler(state=FormLead.name)
async def lead_name(msg: types.Message, state: FSMContext):
    await state.update_data(name=msg.text)
    await msg.answer("📱 Отправьте телефон:", reply_markup=phone_kb())
    await FormLead.phone.set()

@dp.message_handler(content_types=types.ContentTypes.CONTACT, state=FormLead.phone)
async def lead_phone(msg: types.Message, state: FSMContext):
    phone = msg.contact.phone_number
    data = await state.get_data()
    await bot.send_message(ADMIN_CHAT_ID, f"Новая заявка:\nИмя: {data.get('name')}\nТелефон: {phone}")
    await msg.answer("Спасибо! Мы свяжемся с вами.", reply_markup=main_menu())
    await state.finish()

#############################
# STARTUP
#############################
async def on_startup(dp):
    await bot.delete_webhook()
    await bot.set_webhook(WEBHOOK_URL)
    dp.loop.create_task(monitor_webhook())
    logging.info(f"Webhook установлен: {WEBHOOK_URL}")
    try: await bot.send_message(ADMIN_CHAT_ID, "🚀 Бот запущен по webhook!")
    except: pass

#############################
# RUN WEBHOOK SERVER
#############################
if __name__ == "__main__":
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        host=HOST,
        port=PORT
    )
