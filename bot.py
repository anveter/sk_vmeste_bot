import os
import logging
from flask import Flask, request
from aiogram import Bot, Dispatcher, types
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
    BotCommand
)
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.executor import start_webhook

# ---------------------------
# ЛОГИРОВАНИЕ
# ---------------------------
logging.basicConfig(level=logging.INFO)

# ---------------------------
# ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ
# ---------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

if not BOT_TOKEN or not ADMIN_CHAT_ID:
    raise RuntimeError("❌ BOT_TOKEN или ADMIN_CHAT_ID не заданы")

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# ---------------------------
# WEBHOOK URL
# ---------------------------
APP_URL = "https://skvmestebot-production.up.railway.app"  # ← твой домен на Railway
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = APP_URL + WEBHOOK_PATH

# ---------------------------
# FLASK для webhook (ОБЯЗАТЕЛЬНО)
# ---------------------------
app = Flask(__name__)

@app.route("/")
def index():
    return "Бот СК Вместе работает 💚"

@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    update = types.Update.to_object(request.json)
    dp.process_update(update)
    return "OK", 200

# ---------------------------
# ОСНОВНОЕ МЕНЮ
# ---------------------------
def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("📋 О компании", "📁 Каталог проектов")
    kb.row("🏗 Расчёт стоимости дома", "✏️ Архитектурное проектирование")
    kb.row("🌐 Сайты компании", "📞 Контакты")
    return kb

# ---------------------------
# FSM СОСТОЯНИЯ
# ---------------------------
class QuizBuild(StatesGroup):
    q1 = State(); q2 = State(); q3 = State(); q4 = State(); q5 = State(); phone = State()

class QuizProject(StatesGroup):
    q1 = State(); q2 = State(); q3 = State(); q4 = State(); q5 = State(); phone = State()

class FormLead(StatesGroup):
    name = State()
    phone = State()

# ---------------------------
# /START
# ---------------------------
@dp.message_handler(commands=["start", "help"])
async def start(message: types.Message):
    text = (
        "👋 Привет! Я бот компании <b>СК «Вместе»</b>\n\n"
        "Помогу рассчитать стоимость дома, подобрать проект или заказать архитектурное решение.\n\n"
        "Выберите действие из меню ниже 👇\n\n"
        "📝 Или оставьте заявку здесь 👉 /lead"
    )
    await message.answer(text, reply_markup=main_menu())

# ---------------------------
# КНОПКА "О КОМПАНИИ"
# ---------------------------
@dp.message_handler(lambda m: m.text == "📋 О компании")
async def about(message: types.Message):

    text = (
        "🏗 Строительная компания СК «Вместе» — это команда архитекторов, инженеров и специалистов, которые создают надёжные дома 🏡, продуманные проекты 📐 и комфортные пространства для жизни. Мы работаем «под ключ» 🔑 и берём на себя всё: от идеи и проектирования до строительства, инженерии, чистовой отделки и благоустройства территории 🌿.\n\n"
        "Наш принцип прост — делаем так, как сделали бы для себя ❤️. Каждый проект — это не просто квадратные метры 📏, а продуманная система, которая должна служить десятилетиями. Поэтому мы используем современные технологии ⚙️, качественные материалы 🧱 и тщательный контроль на каждом этапе 🔍.\n\n"
        "Мы работаем открыто и честно 🤝: фиксированная смета, прозрачные процессы, регулярные отчёты, фото-видео с объектов 📸🎥. С нами клиенты понимают, за что платят, и получают именно тот результат, который ожидают ✔️.\n\n"
        "Работаем с ипотечниками 🏦, материнским капиталом 👶, военными 🎖 и другими группами населения, которым необходимо использование эскроу-счета для строительства 💼.\n\n"
        "Если вы хотите построить дом 🏠, заказать архитектурный проект ✏️ или подобрать готовое решение — оставьте ваш номер телефона 📲 или напишите нам прямо сейчас 💬. "
        "Наш специалист свяжется с вами, уточнит детали и подскажет оптимальные варианты для вашего бюджета и задач 💡."
    )

    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("📝 Оставить заявку", callback_data="lead"),
        InlineKeyboardButton("💬 Написать нам", url="https://t.me/skVmeste"),
    )

    await message.answer(text, reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == "lead")
async def callback_lead(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.finish()
    await call.message.answer("✍️ Введите ваше имя:")
    await FormLead.name.set()


# ---------------------------
# КАТАЛОГ
# ---------------------------
@dp.message_handler(lambda m: m.text == "📁 Каталог проектов")
async def catalog(message: types.Message):
    await message.answer("📂 Каталог проектов: https://disk.yandex.ru/i/UBQkSxjZVyUKPw")

# ---------------------------
# САЙТЫ КОМПАНИИ
# ---------------------------
@dp.message_handler(lambda m: m.text == "🌐 Сайты компании")
async def sites(message: types.Message):
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("🏠 СК «Вместе»", url="https://ск-вместе.рф"),
        InlineKeyboardButton("📐 Проектирование", url="https://ск-вместе-проектирование.рф")
    )
    await message.answer("🌐 Наши официальные сайты:", reply_markup=kb)

# ---------------------------
# КОНТАКТЫ
# ---------------------------
@dp.message_handler(lambda m: m.text == "📞 Контакты")
async def contacts(message: types.Message):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("💬 Написать в Telegram", url="https://t.me/skVmeste"))

    text = (
        "📞 <b>Контакты СК «Вместе»</b>\n\n"
        "📱 +7 (928) 621-11-05\n"
        "📱 +7 (919) 892-94-02\n"
        "📱 +7 (918) 538-14-55\n\n"
        "📍 Адрес: г. Ростов-на-Дону,\n"
        "Береговая 8 (Риверсайд), 5 этаж, офис 512"
    )

    await message.answer(text, reply_markup=kb)

# ---------------------------
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ---------------------------
def build_keyboard(options):
    kb = InlineKeyboardMarkup(row_width=2)
    for o in options:
        kb.add(InlineKeyboardButton(o, callback_data=o))
    return kb

def phone_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(KeyboardButton("📱 Отправить телефон", request_contact=True))
    return kb

def format_quiz(data, title, phone):
    return (
        f"📋 <b>Анкета ({title})</b>\n\n"
        f"🏠 Этажность: {data['q1']}\n"
        f"🧱 Материал: {data['q2']}\n"
        f"📐 Площадь: {data['q3']}\n"
        f"📄 Проект: {data['q4']}\n"
        f"🕒 Сроки: {data['q5']}\n"
        f"📞 Телефон: {phone}"
    )

# ---------------------------
# КВИЗ — СТРОИТЕЛЬСТВО
# ---------------------------
@dp.message_handler(lambda m: m.text == "🏗 Расчёт стоимости дома")
async def quiz_build_start(message, state):
    await state.finish()
    await message.answer("🏗 Вопрос 1: Сколько этажей будет в доме?",
                         reply_markup=build_keyboard(["1 этаж", "С мансардой", "2 этажа"]))
    await QuizBuild.q1.set()


@dp.callback_query_handler(state=QuizBuild.q1)
async def q1(call, state):
    await call.answer()
    await state.update_data(q1=call.data)
    await call.message.edit_text("Вопрос 2: Из какого материала строим?")
    await call.message.edit_reply_markup(build_keyboard(["Кирпич", "Монолит", "Газобетон", "Пока не определился"]))
    await QuizBuild.q2.set()


@dp.callback_query_handler(state=QuizBuild.q2)
async def q2(call, state):
    await call.answer()
    await state.update_data(q2=call.data)
    await call.message.edit_text("Вопрос 3: Какая площадь интересует?")
    await call.message.edit_reply_markup(build_keyboard([
        "До 100 м²", "100-150 м²", "150-200 м²", "Больше 200 м²"
    ]))
    await QuizBuild.q3.set()


@dp.callback_query_handler(state=QuizBuild.q3)
async def q3(call, state):
    await call.answer()
    await state.update_data(q3=call.data)
    await call.message.edit_text("Вопрос 4: Есть ли проект?")
    await call.message.edit_reply_markup(build_keyboard([
        "Есть готовый проект", "Есть чертёж или картинка",
        "Выберу из каталога", "Хочу индивидуальный проект"
    ]))
    await QuizBuild.q4.set()


@dp.callback_query_handler(state=QuizBuild.q4)
async def q4(call, state):
    await call.answer()
    await state.update_data(q4=call.data)
    await call.message.edit_text("Вопрос 5: Когда планируете строительство?")
    await call.message.edit_reply_markup(build_keyboard([
        "В ближайшее время", "1-3 месяца", "3-6 месяцев", "Нужна консультация"
    ]))
    await QuizBuild.q5.set()


@dp.callback_query_handler(state=QuizBuild.q5)
async def q5(call, state):
    await call.answer()
    await state.update_data(q5=call.data)
    await call.message.answer("📲 Оставьте номер телефона:", reply_markup=phone_kb())
    await QuizBuild.phone.set()


@dp.message_handler(content_types=["contact"], state=QuizBuild.phone)
async def build_finish(message, state):
    phone = message.contact.phone_number
    data = await state.get_data()
    await bot.send_message(ADMIN_CHAT_ID, format_quiz(data, "расчёт строительства", phone))
    await message.answer("✅ Спасибо! Мы свяжемся с вами.", reply_markup=main_menu())
    await state.finish()

# ---------------------------
# КВИЗ — АРХИТЕКТУРНОЕ ПРОЕКТИРОВАНИЕ
# ---------------------------
@dp.message_handler(lambda m: m.text == "✏️ Архитектурное проектирование")
async def quiz_project_start(message, state):
    await state.finish()
    await message.answer("✏️ Вопрос 1: Сколько этажей будет в доме?",
                         reply_markup=build_keyboard(["1 этаж", "С мансардой", "2 этажа"]))
    await QuizProject.q1.set()

@dp.callback_query_handler(state=QuizProject.q1)
async def p1(call, state):
    await call.answer()
    await state.update_data(q1=call.data)
    await call.message.edit_text("Вопрос 2: Из какого материала?")
    await call.message.edit_reply_markup(build_keyboard(["Кирпич", "Монолит", "Газобетон", "Пока не определился"]))
    await QuizProject.q2.set()

@dp.callback_query_handler(state=QuizProject.q2)
async def p2(call, state):
    await call.answer()
    await state.update_data(q2=call.data)
    await call.message.edit_text("Вопрос 3: Какая площадь?")
    await call.message.edit_reply_markup(build_keyboard(["До 100 м²", "100-150 м²", "150-200 м²", "Больше 200 м²"]))
    await QuizProject.q3.set()

@dp.callback_query_handler(state=QuizProject.q3)
async def p3(call, state):
    await call.answer()
    await state.update_data(q3=call.data)
    await call.message.edit_text("Вопрос 4: Есть проект?")
    await call.message.edit_reply_markup(build_keyboard([
        "Есть готовый проект", "Есть чертёж или картинка",
        "Выберу из каталога", "Хочу индивидуальный проект"
    ]))
    await QuizProject.q4.set()

@dp.callback_query_handler(state=QuizProject.q4)
async def p4(call, state):
    await call.answer()
    await state.update_data(q4=call.data)
    await call.message.edit_text("Вопрос 5: Когда начать проектирование?")
    await call.message.edit_reply_markup(build_keyboard([
        "В ближайшее время", "1-3 месяца", "3-6 месяцев", "Нужна консультация"
    ]))
    await QuizProject.q5.set()

@dp.callback_query_handler(state=QuizProject.q5)
async def p5(call, state):
    await call.answer()
    await state.update_data(q5=call.data)
    await call.message.answer("📲 Оставьте телефон:", reply_markup=phone_kb())
    await QuizProject.phone.set()

@dp.message_handler(content_types=["contact"], state=QuizProject.phone)
async def project_finish(message, state):
    phone = message.contact.phone_number
    data = await state.get_data()
    await bot.send_message(ADMIN_CHAT_ID, format_quiz(data, "проектирование", phone))
    await message.answer("✅ Спасибо! Архитектор свяжется с вами.", reply_markup=main_menu())
    await state.finish()

# ---------------------------
# /LEAD — ОСТАВИТЬ ЗАЯВКУ
# ---------------------------
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

@dp.message_handler(content_types=["contact"], state=FormLead.phone)
async def lead_finish(message, state):
    phone = message.contact.phone_number
    data = await state.get_data()

    text = (
        f"📝 <b>Новая заявка</b>\n"
        f"👤 Имя: {data['name']}\n"
        f"📞 Телефон: {phone}"
    )

    await bot.send_message(ADMIN_CHAT_ID, text)
    await message.answer("✅ Спасибо! Мы свяжемся с вами.", reply_markup=main_menu())
    await state.finish()

# ---------------------------
# ЗАПУСК WEBHOOK
# ---------------------------
async def on_startup(dispatcher):
    await bot.delete_webhook()
    await bot.set_webhook(WEBHOOK_URL)

    await bot.send_message(ADMIN_CHAT_ID, "✅ Бот СК «Вместе» запущен (webhook)")

    await bot.set_my_commands([
        BotCommand("start", "Главное меню"),
        BotCommand("lead", "Оставить заявку"),
        BotCommand("help", "Помощь")
    ])


if __name__ == "__main__":
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        skip_updates=True,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8080)),
    )
