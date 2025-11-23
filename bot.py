import logging
import os
from typing import Optional

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery, ContentType,
    InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, ReplyKeyboardRemove
)
from dotenv import load_dotenv

# -------------------------------------------
# ENV + LOGGING
# -------------------------------------------
load_dotenv()
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# -------------------------------------------
# FSM
# -------------------------------------------
class LeadForm(StatesGroup):
    waiting_for_name = State()
    waiting_for_contact = State()


class CostQuiz(StatesGroup):
    floors = State()
    material = State()
    area = State()
    project = State()
    timeline = State()
    phone = State()


class DesignQuiz(StatesGroup):
    material = State()
    floors = State()
    area = State()
    draft = State()
    timeline = State()
    phone = State()


# -------------------------------------------
# ТЕКСТЫ
# -------------------------------------------
MAIN_MENU_BUTTONS = [
    ["📋 О компании", "📁 Каталог проектов"],
    ["🏗 Расчёт стоимости дома", "✏️ Архитектурное проектирование"],
    ["🌐 Сайты компании", "📞 Контакты"],
]

ABOUT_TEXT = (
    "🏗 Строительная компания <b>СК «Вместе»</b> — команда архитекторов и инженеров.\n\n"
    "Работаем «под ключ»: проектирование, строительство, инженерия, отделка и благоустройство.\n\n"
    "💚 Делаем так, как делали бы для себя.\n\n"
    "🏦 Работаем со всеми форматами финансирования, включая эскроу.\n\n"
    "Оставьте номер телефона — специалист свяжется и подберёт решение."
)

START_MESSAGE = (
    "👋 Привет! Я бот компании <b>СК «Вместе»</b>\n\n"
    "Помогу рассчитать стоимость дома, подобрать проект или заказать архитектуру.\n\n"
    "Выберите действие из меню ниже 👇\n\n"
    "📝 Или оставьте заявку здесь 👉 /lead"
)

CATALOG_TEXT = (
    "📂 Каталог проектов:\n"
    "https://disk.yandex.ru/i/UBQkSxjZVyUKPw"
)

CONTACTS_TEXT = (
    "📞 <b>Контакты СК «Вместе»</b>\n\n"
    "📱 Телефоны:\n"
    "• +7 (928) 621-11-05\n"
    "• +7 (919) 892-94-02\n"
    "• +7 (918) 538-14-55\n\n"
    "📍 Адрес офиса:\n"
    "Ростов-на-Дону,\nБереговая 8 (Риверсайд), офис 512"
)

COST_INTRO_PHOTO = "https://avatars.mds.yandex.net/get-altay/1879888/2a000001865205a565b7f2ceeb5211295fb7/XXL_height"
COST_INTRO_TEXT = (
    "<b>🏗 Разработаем полный проект и 3D-визуал дома по СНиП</b>\n"
    "<b>от 400 руб/м² за 30 дней</b>\n\n"
    "Поможем сэкономить до 1 млн рублей — материалы, инженерия, оптимизация.\n\n"
    "Чтобы рассчитать ориентировочную стоимость дома, ответьте на несколько вопросов ⏱"
)

DESIGN_INTRO_PHOTO = "https://ovikv.ru/new/img/podho_130325114/16.jpg"
DESIGN_INTRO_TEXT = (
    "📐 <b>Архитектурное проектирование</b>\n\n"
    "🏗 Полный проект + 3D-визуал по СНиП\n"
    "💰 От 400 руб/м² · до 30 дней\n\n"
    "Ответьте на несколько вопросов ⏱"
)

# -------------------------------------------
# KEYBOARDS
# -------------------------------------------
def main_menu() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for row in MAIN_MENU_BUTTONS:
        kb.row(*row)
    return kb


def request_phone_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(types.KeyboardButton("📲 Отправить телефон", request_contact=True))
    return kb


def about_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📝 Оставить заявку", callback_data="lead"))
    kb.add(InlineKeyboardButton("💬 Написать менеджеру", url="https://t.me/wmeste851"))
    return kb


def sites_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🏠 Основной сайт", url="https://ск-вместе.рф"))
    kb.add(InlineKeyboardButton("📐 Проектирование", url="https://ск-вместе-проектирование.рф"))
    return kb


def contacts_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("💬 Написать нам", url="https://t.me/wmeste851"),
        InlineKeyboardButton("📣 Telegram-канал", url="https://t.me/skVmeste"),
        InlineKeyboardButton("🟢 WhatsApp", url="https://wa.me/79286211105"),
        InlineKeyboardButton("📞 Позвонить", url="tel:+79286211105"),
    )
    return kb


def intro_cost_kb():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("➡️ Рассчитать стоимость дома", callback_data="cost_start"))
    return kb


def intro_design_kb():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📐 Рассчитать стоимость проекта", callback_data="design_start"))
    return kb


def q_kb(options):
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for o in options:
        kb.add(o)
    return kb


# -------------------------------------------
# START + LEAD
# -------------------------------------------
@dp.message_handler(commands=["start"])
async def cmd_start(msg: types.Message):
    await msg.answer(START_MESSAGE, reply_markup=main_menu())


@dp.message_handler(commands=["lead"])
async def cmd_lead(msg: types.Message):
    await LeadForm.waiting_for_name.set()
    await msg.answer("Шаг 1 — ваше имя?", reply_markup=ReplyKeyboardRemove())


@dp.callback_query_handler(text="lead")
async def cb_lead(call: CallbackQuery):
    await call.answer()
    await LeadForm.waiting_for_name.set()
    await call.message.answer("Шаг 1 — ваше имя?", reply_markup=ReplyKeyboardRemove())


@dp.message_handler(state=LeadForm.waiting_for_name)
async def lead_name(msg: types.Message, state: FSMContext):
    await state.update_data(name=msg.text)
    await LeadForm.waiting_for_contact.set()
    await msg.answer("Шаг 2 — отправьте телефон", reply_markup=request_phone_kb())


@dp.message_handler(state=LeadForm.waiting_for_contact, content_types=[ContentType.CONTACT, ContentType.TEXT])
async def lead_contact(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    phone = msg.contact.phone_number if msg.contact else msg.text
    admin = ADMIN_CHAT_ID
    if admin:
        await bot.send_message(admin, f"Новая заявка:\nИмя: {data.get('name')}\nТелефон: {phone}")
    await msg.answer("Спасибо! Мы свяжемся с вами.", reply_markup=main_menu())
    await state.finish()

# -------------------------------------------
# ОБЩИЕ РАЗДЕЛЫ
# -------------------------------------------
@dp.message_handler(lambda m: m.text == "📋 О компании")
async def about(msg: types.Message):
    await msg.answer(ABOUT_TEXT, reply_markup=about_keyboard())


@dp.message_handler(lambda m: m.text == "📁 Каталог проектов")
async def catalog(msg: types.Message):
    await msg.answer(CATALOG_TEXT)


@dp.message_handler(lambda m: m.text == "🌐 Сайты компании")
async def sites(msg: types.Message):
    await msg.answer("Выберите сайт:", reply_markup=sites_keyboard())


@dp.message_handler(lambda m: m.text == "📞 Контакты")
async def contacts(msg: types.Message):
    await msg.answer(CONTACTS_TEXT, reply_markup=contacts_keyboard())

# -------------------------------------------
# КВИЗ 1 — СТОИМОСТЬ ДОМА
# -------------------------------------------
@dp.message_handler(lambda m: m.text == "🏗 Расчёт стоимости дома")
async def cost_intro(msg: types.Message):
    await bot.send_photo(msg.chat.id, COST_INTRO_PHOTO, caption=COST_INTRO_TEXT, reply_markup=intro_cost_kb())


@dp.callback_query_handler(text="cost_start")
async def cost_start(call: CallbackQuery):
    await call.answer()
    await CostQuiz.floors.set()
    await call.message.answer("1️⃣ Сколько этажей?", reply_markup=q_kb(["1 этаж", "С мансардой", "2 этажа"]))


@dp.message_handler(state=CostQuiz.floors)
async def q_floors(msg: types.Message, state: FSMContext):
    await state.update_data(floors=msg.text)
    await CostQuiz.material.set()
    await msg.answer("2️⃣ Материал?", reply_markup=q_kb(["Кирпич", "Каркас / Брус", "Газобетон / Монолит", "Консультация"]))


@dp.message_handler(state=CostQuiz.material)
async def q_mat(msg: types.Message, state: FSMContext):
    await state.update_data(material=msg.text)
    await CostQuiz.area.set()
    await msg.answer("3️⃣ Площадь?", reply_markup=q_kb(["до 100", "100–150", "150–200", "200+"]))


@dp.message_handler(state=CostQuiz.area)
async def q_area(msg: types.Message, state: FSMContext):
    await state.update_data(area=msg.text)
    await CostQuiz.project.set()
    await msg.answer("4️⃣ Проект?", reply_markup=q_kb(["Готовый", "Картинка", "Каталог", "Индивидуальный"]))


@dp.message_handler(state=CostQuiz.project)
async def q_proj(msg: types.Message, state: FSMContext):
    await state.update_data(project=msg.text)
    await CostQuiz.timeline.set()
    await msg.answer("5️⃣ Сроки?", reply_markup=q_kb(["Скоро", "1–3 мес", "3–6 мес", "Не знаю"]))


@dp.message_handler(state=CostQuiz.timeline)
async def q_time(msg: types.Message, state: FSMContext):
    await state.update_data(timeline=msg.text)
    await CostQuiz.phone.set()
    await msg.answer("📲 Телефон?", reply_markup=request_phone_kb())


@dp.message_handler(state=CostQuiz.phone, content_types=[ContentType.CONTACT, ContentType.TEXT])
async def q_phone(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    phone = msg.contact.phone_number if msg.contact else msg.text
    admin = ADMIN_CHAT_ID
    summary = (
        "📋 Анкета — Стоимость дома\n\n"
        f"Этажность: {data.get('floors')}\n"
        f"Материал: {data.get('material')}\n"
        f"Площадь: {data.get('area')}\n"
        f"Проект: {data.get('project')}\n"
        f"Сроки: {data.get('timeline')}\n"
        f"Телефон: {phone}"
    )
    if admin:
        await bot.send_message(admin, summary)
    await msg.answer("Спасибо! Наш специалист свяжется с вами.", reply_markup=main_menu())
    await state.finish()

# -------------------------------------------
# КВИЗ 2 — ПРОЕКТИРОВАНИЕ
# -------------------------------------------
@dp.message_handler(lambda m: m.text == "✏️ Архитектурное проектирование")
async def design_intro(msg: types.Message):
    await bot.send_photo(msg.chat.id, DESIGN_INTRO_PHOTO, caption=DESIGN_INTRO_TEXT, reply_markup=intro_design_kb())


@dp.callback_query_handler(text="design_start")
async def design_start(call: CallbackQuery):
    await call.answer()
    await DesignQuiz.material.set()
    await call.message.answer("1️⃣ Материал?", reply_markup=q_kb(["Кирпич", "Каркас / Брус", "Газобетон / Монолит", "Консультация"]))


@dp.message_handler(state=DesignQuiz.material)
async def d_mat(msg: types.Message, state: FSMContext):
    await state.update_data(material=msg.text)
    await DesignQuiz.floors.set()
    await msg.answer("2️⃣ Этажность?", reply_markup=q_kb(["1", "2", "3", "Другое"]))


@dp.message_handler(state=DesignQuiz.floors)
async def d_floors(msg: types.Message, state: FSMContext):
    await state.update_data(floors=msg.text)
    await DesignQuiz.area.set()
    await msg.answer("3️⃣ Площадь?", reply_markup=q_kb(["до 150", "до 250", "до 500", "500+"]))


@dp.message_handler(state=DesignQuiz.area)
async def d_area(msg: types.Message, state: FSMContext):
    await state.update_data(area=msg.text)
    await DesignQuiz.draft.set()
    await msg.answer("4️⃣ Есть эскиз?", reply_markup=q_kb(["Да", "Картинка", "Каталог", "Нет"]))


@dp.message_handler(state=DesignQuiz.draft)
async def d_draft(msg: types.Message, state: FSMContext):
    await state.update_data(draft=msg.text)
    await DesignQuiz.timeline.set()
    await msg.answer("5️⃣ Сроки?", reply_markup=q_kb(["Скоро", "1–3 мес", "3–6 мес", "Не знаю"]))


@dp.message_handler(state=DesignQuiz.timeline)
async def d_time(msg: types.Message, state: FSMContext):
    await state.update_data(timeline=msg.text)
    await DesignQuiz.phone.set()
    await msg.answer("📲 Телефон?", reply_markup=request_phone_kb())


@dp.message_handler(state=DesignQuiz.phone, content_types=[ContentType.CONTACT, ContentType.TEXT])
async def d_phone(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    phone = msg.contact.phone_number if msg.contact else msg.text
    admin = ADMIN_CHAT_ID
    summary = (
        "📋 Анкета — Архитектурное проектирование\n\n"
        f"Материал: {data.get('material')}\n"
        f"Этажи: {data.get('floors')}\n"
        f"Площадь: {data.get('area')}\n"
        f"Эскиз: {data.get('draft')}\n"
        f"Сроки: {data.get('timeline')}\n"
        f"Телефон: {phone}"
    )
    if admin:
        await bot.send_message(admin, summary)
    await msg.answer("Спасибо! Наш архитектор свяжется с вами.", reply_markup=main_menu())
    await state.finish()

# -------------------------------------------
# FALLBACK
# -------------------------------------------
@dp.message_handler()
async def fallback(msg: types.Message):
    await msg.answer("Выберите действие из меню 👇", reply_markup=main_menu())

# -------------------------------------------
# RUN
# -------------------------------------------
def main():
    executor.start_polling(dp, skip_updates=True)

if __name__ == "__main__":
    main()
