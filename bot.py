import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from flask import Flask
from threading import Thread

# === Flask для Render / UptimeRobot ===
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот СК Вместе работает 💚"

def run_flask():
    app.run(host="0.0.0.0", port=10000)

# === Telegram Bot ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

if not BOT_TOKEN or not ADMIN_CHAT_ID:
    raise RuntimeError("Не заданы BOT_TOKEN или ADMIN_CHAT_ID в переменных окружения")

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

# === Клавиатуры ===
main_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.add("📁 Каталог проектов", "🏗 Расчёт стоимости дома")
main_kb.add("📞 Контакты", "ℹ️ О компании")

# === Команда /start ===
@dp.message_handler(commands=["start", "help"])
async def cmd_start(message: types.Message):
    text = (
        "👋 Привет! Я бот компании <b>СК «Вместе»</b>.\n\n"
        "📁 Отправлю каталог проектов\n"
        "🏠 Помогу рассчитать стоимость дома\n"
        "📐 Или подобрать архитектурное решение\n\n"
        "📞 Наши контакты:\n"
        "+7 (918) 538-14-55\n"
        "band444@yandex.ru\n\n"
        "🌐 Проектируем мечты, строим желания 💚"
    )
    await message.answer(text, reply_markup=main_kb, parse_mode="HTML")

# === Обработчики кнопок ===
@dp.message_handler(lambda message: message.text == "📁 Каталог проектов")
async def send_catalog(message: types.Message):
    await message.answer("📂 Вот ссылка для скачивания каталога проектов:\nhttps://disk.yandex.ru/d/ваша_ссылка")

@dp.message_handler(lambda message: message.text == "🏗 Расчёт стоимости дома")
async def calc_cost(message: types.Message):
    await message.answer("💬 Сколько этажей будет в доме?", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("1 этаж", "2 этажа", "С мансардой", "Отмена"))

@dp.message_handler(lambda message: message.text == "📞 Контакты")
async def send_contacts(message: types.Message):
    await message.answer("📞 Контакты компании СК «Вместе»:\n\n+7 (918) 538-14-55\nband444@yandex.ru\nhttps://t.me/skVmeste")

@dp.message_handler(lambda message: message.text == "ℹ️ О компании")
async def about_company(message: types.Message):
    await message.answer("🏗 <b>СК «Вместе»</b> — проектируем мечты, строим желания.\n\nЗанимаемся строительством загородных коттеджей под ключ: от фундамента до отделки.", parse_mode="HTML")

# === Flask + Telegram Polling ===
def start_bot():
    executor.start_polling(dp, skip_updates=True)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    Thread(target=start_bot).start()
