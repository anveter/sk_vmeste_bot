import os
import logging
import asyncio
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
from threading import Thread

# ---------------------------------------------
# ЛОГИ
# ---------------------------------------------
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")   # пример: https://captivating-insight-production.up.railway.app

if not BOT_TOKEN or not ADMIN_CHAT_ID or not WEBHOOK_HOST:
    raise RuntimeError("❌ BOT_TOKEN / ADMIN_CHAT_ID / WEBHOOK_HOST не заданы")

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
def home():
    return "Бот СК «Вместе» работает через WEBHOOK 💚"

# ФИКС ДЛЯ WEBHOOK — синхронная функция
@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    update = types.Update(**request.json)
    asyncio.ensure_future(dp.process_update(update))
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
# СОСТОЯНИЯ FSM
# ---------------------------------------------
class QuizBuild(StatesGroup):
    q1 = State(); q2 = State(); q3 = State()
    q4 = State(); q5 = State(); phone = State()

class QuizProject(StatesGroup):
    q1 = State(); q2 = State(); q3 = State()
    q4 = State(); q5 = State(); phone = State()

class FormLead(StatesGroup):
    name = State()
    phone = State()

# ---------------------------------------------
# /START
# ---------------------------------------------
@dp.message_handler(commands=["start", "help"])
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот компании <b>СК «Вместе»</b>\n\n"
        "Помогу рассчитать стоимость дома, подобрать проект "
        "или заказать архитектурное решение.\n\n"
        "Выберите действие из меню ниже 👇\n\n"
        "📝 Или оставьте заявку здесь 👉 /lead",
        reply_markup=main_menu()
    )

# ---------------------------------------------
# О КОМПАНИИ
# ---------------------------------------------
@dp.message_handler(lambda m: m.text == "📋 О компании")
async def about(message: types.Message):

    text = (
        "🏗 Строительная компания СК «Вместе» — это команда архитекторов, инженеров и специалистов, "
        "которые создают надёжные дома 🏡, продуманные проекты 📐 и комфортные пространства для жизни. "
        "Мы работаем «под ключ» 🔑 и берём на себя всё: от идеи и проектирования до строительства, инженерии, "
        "чистовой отделки и благоустройства территории 🌿.\n\n"

        "Наш принцип прост — делаем так, как сделали бы для себя ❤️. Каждый проект — это не просто квадратные метры 📏, "
        "а продуманная система, которая должна служить десятилетиями. Поэтому мы используем современные технологии ⚙️, "
        "качественные материалы 🧱 и тщательный контроль на каждом этапе 🔍.\n\n"

        "Мы работаем открыто и честно 🤝: фиксированная смета, прозрачные процессы, регулярные отчёты, фото-видео с объектов 📸🎥. "
        "С нами клиенты понимают, за что платят, и получают именно тот результат, который ожидают ✔️\n\n"

        "Работаем с ипотечниками 🏦, материнским капиталом 👶, военными 🎖 и другими группами населения, которым необходимо "
        "использование эскроу-счета для строительства 💼.\n\n"

        "Если вы хотите построить дом 🏠, заказать архитектурный проект ✏️ или подобрать готовое решение — "
        "оставьте ваш номер телефона 📲 или напишите нам прямо сейчас 💬.\n"
        "Наш специалист свяжется с вами, уточнит детали и подскажет оптимальные варианты для вашего бюджета и задач 💡."
    )

    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("📝 Оставить заявку", callback_data="lead_open"),
        InlineKeyboardButton("💬 Написать нам", url="https://t.me/skVmeste")
    )

    await message.answer(text, reply_markup=kb)

# ---------------------------------------------
# Оставить заявку из О компании
# ---------------------------------------------
@dp.callback_query_handler(lambda c: c.data == "lead_open")
async def lead_open(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.finish()
    await call.message.answer("✍️ Введите ваше имя:")
    await FormLead.name.set()

# ---------------------------------------------
# КАТАЛОГ
# ---------------------------------------------
@dp.message_handler(lambda m: m.text == "📁 Каталог проектов")
async def catalog(message: types.Message):
    await message.answer("📂 Каталог проектов:\nhttps://disk.yandex.ru/i/UBQkSxjZVyUKPw")

# ---------------------------------------------
# САЙТЫ КОМПАНИИ
# ---------------------------------------------
@dp.message_handler(lambda m: m.text == "🌐 Сайты компании")
async def sites(message: types.Message):
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("🏠 Основной сайт", url="https://ск-вместе.рф"),
        InlineKeyboardButton("📐 Проектирование", url="https://ск-вместе-проектирование.рф"),
    )
    await message.answer("🌐 Наши официальные сайты:", reply_markup=kb)

# ---------------------------------------------
# КОНТАКТЫ
# ---------------------------------------------
@dp.message_handler(lambda m: m.text == "📞 Контакты")
async def contacts(message: types.Message):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Telegram-канал", url="https://t.me/skVmeste"))

    await message.answer(
        "📞 <b>Контакты СК «Вместе»</b>\n\n"
        "📱 +7 (928) 621-11-05\n"
        "📱 +7 (919) 892-94-02\n"
        "📱 +7 (918) 538-14-55\n\n"
        "📍 Адрес: г. Ростов-на-Дону,\n"
        "Береговая 8 (Риверсайд), 5 этаж, офис 512",
        reply_markup=kb
    )

# ---------------------------------------------
# ВСЕ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ---------------------------------------------
def build_keyboard(options):
    kb = InlineKeyboardMarkup(row_width=2)
    for o in options:
        kb.add(InlineKeyboardButton(o, callback_data=o))
    return kb

def phone_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(KeyboardButton("📱 Отправить телефон", request_contact=True))
    kb.add(KeyboardButton("Отправлю позже"))
    return kb

def format_quiz(data, name, phone):
    return (
        f"📋 <b>Анкета клиента ({name})</b>\n\n"
        f"🏠 Этажность: {data.get('q1')}\n"
        f"🧱 Материал: {data.get('q2')}\n"
        f"📐 Площадь: {data.get('q3')}\n"
        f"📄 Проект: {data.get('q4')}\n"
        f"🕒 Сроки: {data.get('q5')}\n"
        f"📞 Телефон: {phone}"
    )

# ---------------------------------------------
# КВИЗ №1 — СТРОИТЕЛЬСТВО
# ---------------------------------------------
@dp.message_handler(lambda m: m.text == "🏗 Расчёт стоимости дома")
async def quiz_build(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
        "🏗 Вопрос 1: Сколько этажей будет в доме?",
        reply_markup=build_keyboard(["1 этаж", "С мансардой", "2 этажа"])
    )
    await QuizBuild.q1.set()

@dp.callback_query_handler(state=QuizBuild.q1)
async def qb1(call, state):
    await call.answer()
    await state.update_data(q1=call.data)
    await call.message.edit_text("Вопрос 2: Материал дома?")
    await call.message.edit_reply_markup(build_keyboard(["Кирпич", "Монолит", "Газобетон", "Пока не определился"]))
    await QuizBuild.q2.set()

@dp.callback_query_handler(state=QuizBuild.q2)
async def qb2(call, state):
    await call.answer()
    await state.update_data(q2=call.data)
    await call.message.edit_text("Вопрос 3: Площадь?")
    await call.message.edit_reply_markup(build_keyboard(["До 100 м²", "100–150 м²", "150–200 м²", "Больше 200 м²"]))
    await QuizBuild.q3.set()

@dp.callback_query_handler(state=QuizBuild.q3)
async def qb3(call, state):
    await call.answer()
    await state.update_data(q3=call.data)
    await call.message.edit_text("Вопрос 4: Проект?")
    await call.message.edit_reply_markup(build_keyboard([
        "Есть готовый проект",
        "Есть чертёж или картинка",
        "Выберу из каталога",
        "Хочу индивидуальный проект"
    ]))
    await QuizBuild.q4.set()

@dp.callback_query_handler(state=QuizBuild.q4)
async def qb4(call, state):
    await call.answer()
    await state.update_data(q4=call.data)
    await call.message.edit_text("Вопрос 5: Сроки?")
    await call.message.edit_reply_markup(build_keyboard([
        "В ближайшее время", "1–3 месяца", "3–6 месяцев", "Нужна консультация"
    ]))
    await QuizBuild.q5.set()

@dp.callback_query_handler(state=QuizBuild.q5)
async def qb5(call, state):
    await call.answer()
    await state.update_data(q5=call.data)
    await call.message.answer("📲 Оставьте номер телефона:", reply_markup=phone_kb())
    await QuizBuild.phone.set()

@dp.message_handler(content_types=types.ContentTypes.CONTACT, state=QuizBuild.phone)
async def qb_phone(message, state):
    phone = message.contact.phone_number
    data = await state.get_data()
    await bot.send_message(ADMIN_CHAT_ID, format_quiz(data, "Строительство", phone))
    await message.answer("✅ Спасибо! Мы свяжемся с вами.", reply_markup=main_menu())
    await state.finish()

# ---------------------------------------------
# КВИЗ №2 — АРХИТЕКТУРНОЕ ПРОЕКТИРОВАНИЕ
# ---------------------------------------------
# ---------------------------------------------
# КВИЗ №2 — АРХИТЕКТУРНОЕ ПРОЕКТИРОВАНИЕ (ОБНОВЛЁННЫЙ)
# ---------------------------------------------
@dp.message_handler(lambda m: m.text == "✏️ Архитектурное проектирование")
async def quiz_project(message, state):
    await state.finish()
    await message.answer(
        "✏️ Вопрос 1: Из какого материала будем строить дом?",
        reply_markup=build_keyboard([
            "Кирпич",
            "Монолит",
            "Газобетон",
            "Пока не определился"
        ])
    )
    await QuizProject.q1.set()


@dp.callback_query_handler(state=QuizProject.q1)
async def qp1(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(q1=call.data)

    await call.message.edit_text("Вопрос 2: Сколько этажей будет в доме?")
    await call.message.edit_reply_markup(build_keyboard([
        "1 этаж",
        "2 этажа",
        "3 этажа",
        "Другое"
    ]))
    await QuizProject.q2.set()


@dp.callback_query_handler(state=QuizProject.q2)
async def qp2(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(q2=call.data)

    await call.message.edit_text("Вопрос 3: Какую общую площадь вы рассматриваете?")
    await call.message.edit_reply_markup(build_keyboard([
        "До 150 м²",
        "До 250 м²",
        "До 500 м²",
        "Более 500 м²"
    ]))
    await QuizProject.q3.set()


@dp.callback_query_handler(state=QuizProject.q3)
async def qp3(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(q3=call.data)

    await call.message.edit_text("Вопрос 4: Есть ли у вас эскиз-проект, который нравится?")
    await call.message.edit_reply_markup(build_keyboard([
        "Да, есть проект который нравится",
        "Есть картинка / фото / рисунок",
        "Выберу из каталога",
        "Нет"
    ]))
    await QuizProject.q4.set()


@dp.callback_query_handler(state=QuizProject.q4)
async def qp4(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(q4=call.data)

    await call.message.answer("📲 Оставьте телефон для связи:", reply_markup=phone_kb())
    await QuizProject.phone.set()


@dp.message_handler(content_types=types.ContentTypes.CONTACT, state=QuizProject.phone)
async def qp_phone(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number
    data = await state.get_data()

    await bot.send_message(
        ADMIN_CHAT_ID,
        format_quiz(data, "Архитектурное проектирование", phone)
    )

    await message.answer(
        "✅ Спасибо! Архитектор свяжется с вами в ближайшее время.",
        reply_markup=main_menu()
    )
    await state.finish()
# ---------------------------------------------
# /LEAD — ОСТАВИТЬ ЗАЯВКУ
# ---------------------------------------------
@dp.message_handler(commands=["lead"])
async def lead(message, state):
    await state.finish()
    await message.answer("✍️ Введите ваше имя:")
    await FormLead.name.set()

@dp.message_handler(state=FormLead.name)
async def lead_name(message, state):
    await state.update_data(name=message.text)
    await message.answer("📱 Теперь отправьте телефон:", reply_markup=phone_kb())
    await FormLead.phone.set()

@dp.message_handler(content_types=types.ContentTypes.CONTACT, state=FormLead.phone)
async def lead_phone(message, state):
    phone = message.contact.phone_number
    data = await state.get_data()

    await bot.send_message(
        ADMIN_CHAT_ID,
        f"📝 <b>Новая заявка</b>\n👤 Имя: {data.get('name')}\n📞 Телефон: {phone}"
    )

    await message.answer("✅ Спасибо! Мы свяжемся с вами.", reply_markup=main_menu())
    await state.finish()

# ---------------------------------------------
# ИНИЦИАЛИЗАЦИЯ WEBHOOK
# ---------------------------------------------
async def on_startup(dp):
    logging.warning("Удаляю старый webhook…")
    await bot.delete_webhook()

    logging.warning(f"Ставлю новый webhook: {WEBHOOK_URL}")
    await bot.set_webhook(WEBHOOK_URL)

    await bot.send_message(ADMIN_CHAT_ID, "✅ Бот СК «Вместе» запущен через WEBHOOK!")

# ---------------------------------------------
#  ЗАПУСК FLASK + AIOGRAM
# ---------------------------------------------
def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
