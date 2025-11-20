import os
import logging
import asyncio
from flask import Flask, request
from aiogram import Bot, Dispatcher, types
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

# ==========================================================
# LOGS
# ==========================================================
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")   # Example: https://project.up.railway.app

if not BOT_TOKEN or not ADMIN_CHAT_ID or not WEBHOOK_HOST:
    raise RuntimeError("❌ BOT_TOKEN / ADMIN_CHAT_ID / WEBHOOK_HOST должны быть заданы в Railway > Variables")

WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = WEBHOOK_HOST + WEBHOOK_PATH

# ==========================================================
# BOT + DISPATCHER
# ==========================================================
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=MemoryStorage())

# ==========================================================
# FLASK SERVER (ТОЛЬКО WEBHOOK!)
# ==========================================================
app = Flask(__name__)

@app.route("/")
def home():
    return "СК Вместе бот работает через Webhook 💚"

@app.route(WEBHOOK_PATH, methods=["POST"])
def process_webhook():
    json_update = request.json
    update = types.Update(**json_update)
    asyncio.run(dp.process_update(update))
    return "OK"


# ==========================================================
# MENU
# ==========================================================
def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("📋 О компании", "📁 Каталог проектов")
    kb.row("🏗 Расчёт стоимости дома", "✏️ Архитектурное проектирование")
    kb.row("🌐 Сайты компании", "📞 Контакты")
    return kb

# ==========================================================
# STATES
# ==========================================================
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


# ==========================================================
# HELPERS
# ==========================================================
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
        f"📋 <b>Анкета ({name})</b>\n\n"
        f"🧱 Материал: {data.get('q1')}\n"
        f"🏠 Этажность: {data.get('q2')}\n"
        f"📐 Площадь: {data.get('q3')}\n"
        f"📄 Эскиз-проект: {data.get('q4')}\n"
        f"🕒 Сроки: {data.get('q5')}\n"
        f"📞 Телефон: {phone}"
    )


# ==========================================================
# START
# ==========================================================
@dp.message_handler(commands=["start", "help"])
async def start_handler(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот компании <b>СК «Вместе»</b>\n\n"
        "Помогу рассчитать стоимость дома, подобрать проект "
        "или заказать архитектурное решение.\n\n"
        "Выберите действие из меню ниже 👇",
        reply_markup=main_menu()
    )


# ==========================================================
# ABOUT
# ==========================================================
@dp.message_handler(lambda m: m.text == "📋 О компании")
async def about(message: types.Message):
    text = (
        "🏗 Строительная компания <b>СК «Вместе»</b> — команда архитекторов, инженеров и специалистов.\n\n"
        "❤️ Каждый проект — продуманная система, рассчитанная на десятилетия.\n\n"
        "🤝 Прозрачность, отчёты, контроль качества.\n\n"
        "🏠 Хотите построить дом? Напишите нам!"
    )

    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("📝 Оставить заявку", callback_data="lead_open"),
        InlineKeyboardButton("💬 Написать менеджеру", url="https://t.me/wmeste851")
    )
    await message.answer(text, reply_markup=kb)


# ==========================================================
# LEAD FORM
# ==========================================================
@dp.callback_query_handler(lambda c: c.data == "lead_open")
async def lead_open(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.answer("✍️ Введите ваше имя:")
    await FormLead.name.set()

@dp.message_handler(state=FormLead.name)
async def lead_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("📱 Теперь отправьте телефон:", reply_markup=phone_kb())
    await FormLead.phone.set()

@dp.message_handler(content_types=types.ContentTypes.CONTACT, state=FormLead.phone)
async def lead_finish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    phone = message.contact.phone_number

    await bot.send_message(
        ADMIN_CHAT_ID,
        f"📝 Новая заявка\nИмя: {data['name']}\nТелефон: {phone}"
    )

    await message.answer("✅ Спасибо! Мы свяжемся с вами!", reply_markup=main_menu())
    await state.finish()


# ==========================================================
# CATALOG
# ==========================================================
@dp.message_handler(lambda m: m.text == "📁 Каталог проектов")
async def catalog(message: types.Message):
    await message.answer("📂 Каталог проектов:\nhttps://disk.yandex.ru/i/UBQkSxjZVyUKPw")


# ==========================================================
# CONTACTS
# ==========================================================
@dp.message_handler(lambda m: m.text == "📞 Контакты")
async def contacts(message: types.Message):
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("💬 Telegram", url="https://t.me/wmeste851"),
        InlineKeyboardButton("📣 Канал", url="https://t.me/skVmeste")
    )
    kb.add(
        InlineKeyboardButton("🟢 WhatsApp", url="https://wa.me/79286211105"),
        InlineKeyboardButton("📞 Позвонить", url="tel:+79286211105")
    )
    await message.answer(
        "📍 Адрес: Ростов-на-Дону, Береговая 8 (Риверсайд), офис 512\n\n"
        "📞 +7 (918) 538-14-55",
        reply_markup=kb
    )


# ==========================================================
# QUIZ 1 — BUILD COST
# ==========================================================
@dp.message_handler(lambda m: m.text == "🏗 Расчёт стоимости дома")
async def quiz_build_intro(message: types.Message, state: FSMContext):
    await state.finish()

    await message.answer_photo(
        photo="https://avatars.mds.yandex.net/get-altay/1879888/2a000001865205a565b7f2ceeb5211295fb7/XXL_height",
        caption=(
            "<b>🏗 Разработаем полный проект и 3D визуал вашего дома по СНиП</b>\n"
            "<b>от 400 руб/м² за 30 дней</b>\n\n"
            "💰 Поможем сэкономить до 1 млн рублей.\n"
            "⏳ Срок — до 30 дней.\n"
            "📐 Рассчитаем смету строительства!"
        )
    )

    await message.answer("Чтобы рассчитать стоимость, ответьте на несколько вопросов ⏱")
    await message.answer(
        "Готовы начать?",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("➡️ Рассчитать стоимость дома", callback_data="start_quiz_build")
        )
    )

@dp.callback_query_handler(lambda c: c.data == "start_quiz_build")
async def qb1(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.answer()
    await call.message.answer(
        "🏗 Вопрос 1: Сколько этажей будет в доме?",
        reply_markup=build_keyboard(["1 этаж", "С мансардой", "2 этажа"])
    )
    await QuizBuild.q1.set()

@dp.callback_query_handler(state=QuizBuild.q1)
async def qb2(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(q1=call.data)
    await call.message.answer(
        "Вопрос 2: Из какого материала планируете строить дом?",
        reply_markup=build_keyboard([
            "Кирпич", "Каркас / Брус", "Газобетон / Монолит",
            "Пока не определился, нужна консультация"
        ])
    )
    await QuizBuild.q2.set()

@dp.callback_query_handler(state=QuizBuild.q2)
async def qb3(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(q2=call.data)
    await call.message.answer(
        "Вопрос 3: Какую площадь вы рассматриваете?",
        reply_markup=build_keyboard(["до 100 м²", "100–150 м²", "150–200 м²", "Больше 200 м²"])
    )
    await QuizBuild.q3.set()

@dp.callback_query_handler(state=QuizBuild.q3)
async def qb4(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(q3=call.data)
    await call.message.answer(
        "Вопрос 4: У вас есть проект, который нравится?",
        reply_markup=build_keyboard([
            "Есть готовый проект",
            "Есть картинка или чертёж",
            "Выберу из каталога",
            "Нужен индивидуальный проект"
        ])
    )
    await QuizBuild.q4.set()

@dp.callback_query_handler(state=QuizBuild.q4)
async def qb5(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(q4=call.data)
    await call.message.answer(
        "Вопрос 5: Когда планируете строительство?",
        reply_markup=build_keyboard([
            "В ближайшее время", "1–3 месяца", "3–6 месяцев", "Не знаю"
        ])
    )
    await QuizBuild.q5.set()

@dp.callback_query_handler(state=QuizBuild.q5)
async def qb_phone(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(q5=call.data)
    await call.message.answer(
        "📲 Оставьте телефон:",
        reply_markup=phone_kb()
    )
    await QuizBuild.phone.set()

@dp.message_handler(content_types=types.ContentTypes.CONTACT, state=QuizBuild.phone)
async def qb_finish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    phone = message.contact.phone_number

    await bot.send_message(ADMIN_CHAT_ID, format_quiz(data, "Расчёт стоимости дома", phone))
    await message.answer("✅ Спасибо! Мы свяжемся с вами.", reply_markup=main_menu())
    await state.finish()


# ==========================================================
# QUIZ 2 — PROJECTING
# ==========================================================
@dp.message_handler(lambda m: m.text == "✏️ Архитектурное проектирование")
async def qp_intro(message: types.Message, state: FSMContext):
    await state.finish()

    await message.answer_photo(
        photo="https://ovikv.ru/new/img/podho_130325114/16.jpg",
        caption="📐 <b>Архитектурное проектирование</b>"
    )

    await message.answer(
        "<b>🏗 Разработаем полный проект и 3D-визуал вашего дома по СНиП</b>\n"
        "<b>Стоимость от 400 руб/м² · Срок — до 30 дней</b>\n\n"
        "Ответьте на несколько вопросов ⏱"
    )

    kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton("📐 Рассчитать стоимость проекта", callback_data="start_quiz_project")
    )
    await message.answer("Готовы начать?", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == "start_quiz_project")
async def qp1(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.answer()
    await call.message.edit_text("✏️ Вопрос 1: Из какого материала планируете строить?")
    await call.message.edit_reply_markup(build_keyboard([
        "Кирпич", "Каркас / Брус", "Газобетон / Монолит", "Пока не определился"
    ]))
    await QuizProject.q1.set()

@dp.callback_query_handler(state=QuizProject.q1)
async def qp2(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(q1=call.data)
    await call.message.edit_text("Вопрос 2: Сколько этажей?")
    await call.message.edit_reply_markup(build_keyboard([
        "1 этаж", "2 этажа", "3 этажа", "Другое"
    ]))
    await QuizProject.q2.set()

@dp.callback_query_handler(state=QuizProject.q2)
async def qp3(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(q2=call.data)
    await call.message.edit_text("Вопрос 3: Какая площадь дома?")
    await call.message.edit_reply_markup(build_keyboard([
        "до 150 м²", "до 250 м²", "до 500 м²", "Более 500 м²"
    ]))
    await QuizProject.q3.set()

@dp.callback_query_handler(state=QuizProject.q3)
async def qp4(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(q3=call.data)
    await call.message.edit_text("Есть ли эскиз-проект?")
    await call.message.edit_reply_markup(build_keyboard([
        "Да, есть проект", "Есть картинка/чертёж", "Выберу из каталога", "Нет"
    ]))
    await QuizProject.q4.set()

@dp.callback_query_handler(state=QuizProject.q4)
async def qp5(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(q4=call.data)
    await call.message.edit_text("Когда планируете строительство?")
    await call.message.edit_reply_markup(build_keyboard([
        "В ближайшее время", "1–3 месяца", "3–6 месяцев", "Не знаю"
    ]))
    await QuizProject.q5.set()

@dp.callback_query_handler(state=QuizProject.q5)
async def qp_phone(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(q5=call.data)
    await call.message.answer("📲 Оставьте телефон:", reply_markup=phone_kb())
    await QuizProject.phone.set()

@dp.message_handler(content_types=types.ContentTypes.CONTACT, state=QuizProject.phone)
async def qp_finish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    phone = message.contact.phone_number

    await bot.send_message(ADMIN_CHAT_ID, format_quiz(data, "Проектирование", phone))
    await message.answer("✅ Спасибо! Мы скоро свяжемся!", reply_markup=main_menu())
    await state.finish()



# ==========================================================
# START WEBHOOK SERVER
# ==========================================================
async def on_startup():
    await bot.delete_webhook()
    await bot.set_webhook(WEBHOOK_URL)
    await bot.send_message(ADMIN_CHAT_ID, "✅ Бот СК «Вместе» запущен (Webhook)")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(on_startup())

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
