import logging
import csv
import os
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from flask import Flask

# --- Flask для Render ---
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running!"

# --- Переменные окружения ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID", "0"))
SITE_URL = os.environ.get("SITE_URL", "https://ск-вместе.рф/")
TG_CHANNEL = os.environ.get("TG_CHANNEL", "https://t.me/skVmeste")
PHONE_1 = os.environ.get("PHONE_1", "+7 (928) 621-11-05")
PHONE_2 = os.environ.get("PHONE_2", "8 (919) 892-94-02")
PHONE_3 = os.environ.get("PHONE_3", "8 (918) 538-14-55")

if not BOT_TOKEN or ADMIN_CHAT_ID == 0:
    raise RuntimeError("Не заданы BOT_TOKEN или ADMIN_CHAT_ID в переменных окружения")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# --- Определение состояний ---
class Quiz1(StatesGroup):
    q1 = State(); q2 = State(); q3 = State(); q4 = State(); q5 = State(); q6 = State(); name = State(); phone = State()

class Quiz2(StatesGroup):
    q1 = State(); q2 = State(); q3 = State(); q4 = State(); q5 = State(); q6 = State(); name = State(); phone = State()

# --- Клавиатуры ---
main_kb = InlineKeyboardMarkup(row_width=2)
main_kb.add(
    InlineKeyboardButton("📁 Каталог проектов", callback_data="send_catalog"),
    InlineKeyboardButton("🏠 Расчёт стоимости дома", callback_data="quiz1"),
    InlineKeyboardButton("📐 Архитектурное проектирование", callback_data="quiz2"),
)
main_kb.add(
    InlineKeyboardButton("🌐 Сайт", url=SITE_URL),
    InlineKeyboardButton("📢 Канал", url=TG_CHANNEL)
)
main_kb.add(InlineKeyboardButton("📞 Оставить контакт", callback_data="leave_contact"))

cancel_kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Отмена")

CSV_FILE = "leads.csv"

# --- Сохранение данных ---
def save_to_csv(row: dict):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

async def notify_admin(text):
    try:
        await bot.send_message(ADMIN_CHAT_ID, text, parse_mode="HTML")
    except Exception as e:
        logging.error("Ошибка уведомления админа: %s", e)

# --- Основные обработчики ---
@dp.message_handler(commands=["start", "help"])
async def cmd_start(message: types.Message):
    text = (
        "👋 Привет! Я бот компании <b>СК «Вместе»</b>.\n\n"
        "📁 Отправлю каталог проектов\n"
        "🏠 Помогу рассчитать стоимость дома\n"
        "📐 Или подобрать архитектурное решение\n\n"
        "📞 Наши контакты:\n"
        f"{PHONE_1}\n{PHONE_2}\n{PHONE_3}\n"
    )
    await message.answer(text, reply_markup=main_kb, parse_mode="HTML")

# --- Callback ---
@dp.callback_query_handler(lambda c: True)
async def callback_handler(c: types.CallbackQuery):
    data = c.data
    if data == "send_catalog":
        url = "https://disk.yandex.ru/i/UBQkSxjZVyUKPw"
        kb = InlineKeyboardMarkup().add(
            InlineKeyboardButton("📥 Скачать каталог", url=url)
        )
        await bot.send_message(
            c.from_user.id,
            "🏠 Вот каталог проектов СК «Вместе»:\nНажмите на кнопку, чтобы скачать.\n\n"
            f"📁 <a href=\"{url}\">Скачать PDF</a>",
            reply_markup=kb,
            parse_mode="HTML"
        )
        await c.answer()
        return
    if data == "quiz1":
        await bot.send_message(c.from_user.id, "📊 Расчёт стоимости дома\n\nСколько этажей будет в доме?",
                               reply_markup=ReplyKeyboardMarkup(resize_keyboard=True)
                               .add("1 этаж", "С мансардой", "2 этажа").add("Отмена"))
        await Quiz1.q1.set()
        await c.answer()
        return
    if data == "quiz2":
        await bot.send_message(c.from_user.id, "📐 Архитектурное проектирование\n\nСколько этажей планируете?",
                               reply_markup=ReplyKeyboardMarkup(resize_keyboard=True)
                               .add("1 этаж", "С мансардой", "2 этажа").add("Отмена"))
        await Quiz2.q1.set()
        await c.answer()
        return
    if data == "leave_contact":
        kb = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("📱 Отправить контакт", request_contact=True))
        await bot.send_message(c.from_user.id, "📞 Отправьте свой номер для связи:", reply_markup=kb)
        await c.answer()
        return

# --- Обработчик отмены ---
@dp.message_handler(lambda m: m.text == "Отмена", state="*")
async def cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Действие отменено.", reply_markup=main_kb)

# --- Остальные хендлеры (оставь как есть) ---

@dp.message_handler()
async def fallback(message: types.Message):
    await message.answer("Выберите действие из меню 👇", reply_markup=main_kb)

# --- Запуск ---
if __name__ == "__main__":
    import threading
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=10000)).start()
    print("✅ Бот запущен на Render")
    executor.start_polling(dp, skip_updates=True)
