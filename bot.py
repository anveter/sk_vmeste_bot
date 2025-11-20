import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
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
    raise RuntimeError("❌ BOT_TOKEN / ADMIN_CHAT_ID не заданы в переменных окружения")

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=MemoryStorage())

# ---------------------------------------------
# МЕНЮ
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

# ---------------------------------------------
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
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
        f"📋 <b>Анкета ({name})</b>\n\n"
        f"🧱 Материал: {data.get('q1')}\n"
        f"🏠 Этажность: {data.get('q2')}\n"
        f"📐 Площадь: {data.get('q3')}\n"
        f"📄 Эскиз-проект: {data.get('q4')}\n"
        f"🕒 Сроки: {data.get('q5')}\n"
        f"📞 Телефон: {phone}"
    )

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
        "🏗 Строительная компания <b>СК «Вместе»</b> — это команда архитекторов, инженеров и специалистов, "
        "которые создают надёжные дома, продуманные проекты и комфортные пространства для жизни. "
        "Мы работаем «под ключ» и берём на себя всё: от идеи и проектирования до строительства, инженерии, отделки "
        "и благоустройства территории.\n\n"

        "❤️ Наш принцип прост — делаем так, как сделали бы для себя. Каждый проект — это не просто квадратные метры, "
        "а продуманная система, которая должна служить десятилетиями. Поэтому мы используем современные технологии, "
        "качественные материалы и проводим тщательный контроль на каждом этапе.\n\n"

        "🤝 Мы работаем открыто и честно: фиксированная смета, прозрачные процессы, регулярные отчёты, "
        "фото- и видеоконтроль объектов. Клиенты понимают, за что платят, и получают именно тот результат, который ожидают.\n\n"

        "🏦 Работаем со всеми видами финансирования: ипотека, материнский капитал, военная ипотека и другие форматы, "
        "требующие использования эскроу-счёта.\n\n"

        "🏠 Если вы хотите построить дом, заказать архитектурный проект или подобрать готовое решение — оставьте ваш номер "
        "телефона или напишите нам прямо сейчас.\n"
        "Наш специалист свяжется с вами, уточнит детали и предложит лучшие варианты под ваш бюджет."
    )

    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("📝 Оставить заявку", callback_data="lead_open"),
        InlineKeyboardButton("💬 Написать менеджеру", url="https://t.me/wmeste851")
    )

    await message.answer(text, reply_markup=kb)

# ---------------------------------------------
# ОСТАВИТЬ ЗАЯВКУ
# ---------------------------------------------
@dp.callback_query_handler(lambda c: c.data == "lead_open")
async def lead_open(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.finish()
    await call.message.answer("✍️ Введите ваше имя:")
    await FormLead.name.set()

@dp.message_handler(commands=["lead"])
async def lead(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("✍️ Введите ваше имя:")
    await FormLead.name.set()

@dp.message_handler(state=FormLead.name)
async def lead_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("📱 Теперь отправьте телефон:", reply_markup=phone_kb())
    await FormLead.phone.set()

@dp.message_handler(content_types=types.ContentTypes.CONTACT, state=FormLead.phone)
async def lead_phone(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number
    data = await state.get_data()

    await bot.send_message(
        ADMIN_CHAT_ID,
        f"📝 <b>Новая заявка</b>\n👤 Имя: {data.get('name')}\n📞 Телефон: {phone}"
    )

    await message.answer("✅ Спасибо! Мы свяжемся с вами.", reply_markup=main_menu())
    await state.finish()

# ---------------------------------------------
# КАТАЛОГ
# ---------------------------------------------
@dp.message_handler(lambda m: m.text == "📁 Каталог проектов")
async def catalog(message: types.Message):
    await message.answer("📂 Каталог проектов:\nhttps://disk.yandex.ru/i/UBQkSxjZVyUKPw")

# ---------------------------------------------
# САЙТЫ
# ---------------------------------------------
@dp.message_handler(lambda m: m.text == "🌐 Сайты компании")
async def sites(message: types.Message):
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("🏠 Основной сайт", url="https://ск-вместе.рф"),
        InlineKeyboardButton("📐 Проектирование", url="https://ск-вместе-проектирование.рф")
    )
    await message.answer("🌐 Наши официальные сайты:", reply_markup=kb)

# ---------------------------------------------
# КОНТАКТЫ
# ---------------------------------------------
@dp.message_handler(lambda m: m.text == "📞 Контакты")
async def contacts(message: types.Message):
    kb = InlineKeyboardMarkup(row_width=2)

    kb.add(
        InlineKeyboardButton("💬 Написать нам", url="https://t.me/wmeste851"),
        InlineKeyboardButton("📣 Telegram-канал", url="https://t.me/skVmeste")
    )

    kb.add(
        InlineKeyboardButton("🟢 WhatsApp", url="https://wa.me/79286211105"),
        InlineKeyboardButton("📞 Позвонить", url="tel:+79286211105")
    )

    await message.answer(
        "📞 <b>Контакты СК «Вместе»</b>\n\n"
        "📱 <b>Телефоны:</b>\n"
        "• +7 (928) 621-11-05\n"
        "• +7 (919) 892-94-02\n"
        "• +7 (918) 538-14-55\n\n"
        "📍 <b>Адрес офиса:</b>\n"
        "Ростов-на-Дону,\n"
        "Береговая 8 (Риверсайд), офис 512\n\n"
        "🕘 <i>График работы:</i> ежедневно с 9:00 до 20:00",
        reply_markup=kb
    )

# -------------------------------------------------------
# КВИЗ №1 — РАСЧЁТ СТОИМОСТИ ДОМА (СТАБИЛЬНАЯ РАБОЧАЯ ВЕРСИЯ)
# -------------------------------------------------------
@dp.message_handler(lambda m: m.text == "🏗 Расчёт стоимости дома")
async def quiz_build_intro(message: types.Message, state: FSMContext):
    await state.finish()

    # typing эффект
    await bot.send_chat_action(message.chat.id, "typing")
    await asyncio.sleep(1)

    # Фото
    photo_url = "https://avatars.mds.yandex.net/get-altay/1879888/2a000001865205a565b7f2ceeb5211295fb7/XXL_height"

    await message.answer_photo(
        photo=photo_url,
        caption=(
            "<b>🏗 Разработаем полный проект и 3D визуал вашего дома по СНиП</b>\n"
            "<b>от 400 руб/м² за 30 дней</b>\n\n"
            "💰 Поможем сэкономить <b>до 1 млн рублей</b> за счёт правильно подобранных материалов "
            "и инженерных решений.\n\n"
            "⏳ Срок выполнения — до 30 дней.\n"
            "📐 Рассчитаем смету будущего строительства!"
        )
    )

    await message.answer(
        "Чтобы рассчитать ориентировочную стоимость дома, ответьте на несколько уточняющих вопросов.\n"
        "Это займёт меньше минуты ⏱"
    )

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("➡️ Рассчитать стоимость дома", callback_data="start_quiz_build"))

    await message.answer("Готовы начать?", reply_markup=kb)

# ВОПРОС 1
@dp.callback_query_handler(lambda c: c.data == "start_quiz_build")
async def quiz_start(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.finish()

    await call.message.answer(
        "🏗 Вопрос 1: Сколько этажей будет в доме?",
        reply_markup=build_keyboard([
            "1 этаж",
            "С мансардой",
            "2 этажа"
        ])
    )
    await QuizBuild.q1.set()

# ВОПРОС 2
@dp.callback_query_handler(state=QuizBuild.q1)
async def q1(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(q1=call.data)

    await call.message.answer(
        "Вопрос 2: Из какого материала планируете строить дом?",
        reply_markup=build_keyboard([
            "Кирпич",
            "Каркас / Брус",
            "Газобетон / Монолит",
            "Пока не определился, нужна консультация"
        ])
    )
    await QuizBuild.q2.set()

# ВОПРОС 3
@dp.callback_query_handler(state=QuizBuild.q2)
async def q2(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(q2=call.data)

    await call.message.answer(
        "Вопрос 3: Какую общую площадь Вы рассматриваете?",
        reply_markup=build_keyboard([
            "до 100 м²",
            "100–150 м²",
            "150–200 м²",
            "Больше 200 м²"
        ])
    )
    await QuizBuild.q3.set()

# ВОПРОС 4
@dp.callback_query_handler(state=QuizBuild.q3)
async def q3(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(q3=call.data)

    await call.message.answer(
        "Вопрос 4: У Вас есть проект, который нравится?",
        reply_markup=build_keyboard([
            "Есть готовый проект",
            "Есть картинка, рисунок, чертеж",
            "Выберу из каталога",
            "Хочу индивидуальный проект (для Вас бесплатно)"
        ])
    )
    await QuizBuild.q4.set()

# ВОПРОС 5
@dp.callback_query_handler(state=QuizBuild.q4)
async def q4(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(q4=call.data)

    await call.message.answer(
        "Вопрос 5: Когда Вы планируете строительство?",
        reply_markup=build_keyboard([
            "В ближайшее время",
            "Через 1–3 месяца",
            "Через 3–6 месяцев",
            "Не знаю, нужна консультация"
        ])
    )
    await QuizBuild.q5.set()

# ТЕЛЕФОН
@dp.callback_query_handler(state=QuizBuild.q5)
async def q5(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(q5=call.data)

    await call.message.answer(
        "📲 Оставьте телефон — мы подготовим расчёт стоимости и свяжемся с вами:",
        reply_markup=phone_kb()
    )
    await QuizBuild.phone.set()

# ФИНАЛ
@dp.message_handler(content_types=types.ContentTypes.CONTACT, state=QuizBuild.phone)
async def finish_quiz(message: types.Message, state: FSMContext):
    data = await state.get_data()
    phone = message.contact.phone_number

    await bot.send_message(
        ADMIN_CHAT_ID,
        f"📋 <b>Анкета — Расчёт стоимости дома</b>\n\n"
        f"🏠 Этажность: {data['q1']}\n"
        f"🧱 Материал: {data['q2']}\n"
        f"📐 Площадь: {data['q3']}\n"
        f"📄 Проект: {data['q4']}\n"
        f"🕒 Сроки: {data['q5']}\n"
        f"📞 Телефон: {phone}"
    )

    await message.answer(
        "✅ Спасибо! Мы подготовим ориентировочную стоимость и свяжемся с вами.",
        reply_markup=main_menu()
    )

    await state.finish()

# ---------------------------------------------
# КВИЗ №2 — АРХИТЕКТУРНОЕ ПРОЕКТИРОВАНИЕ
# ---------------------------------------------
@dp.message_handler(lambda m: m.text == "✏️ Архитектурное проектирование")
async def quiz_project_intro(message: types.Message, state: FSMContext):
    await state.finish()

    # 1) Фото
    await message.answer_photo(
        photo="https://ovikv.ru/new/img/podho_130325114/16.jpg",
        caption="📐 <b>Архитектурное проектирование</b>"
    )

    # 2) typing…
    await bot.send_chat_action(message.chat.id, "typing")
    await asyncio.sleep(1.3)

    # 3) Текст приглашения
    await message.answer(
        "<b>🏗 Разработаем полный проект и 3D-визуал вашего дома по СНиП</b>\n"
        "<b>💰 Стоимость от 400 руб/м² · Срок — до 30 дней</b>\n\n"
        "Мы поможем вам сэкономить <b>до 1 млн рублей</b> за счёт правильного подбора "
        "материалов, инженерных решений и грамотной структуры проекта.\n\n"
        "Чтобы рассчитать стоимость проектирования и подготовить персональное предложение — "
        "ответьте, пожалуйста, на несколько коротких вопросов. Это займёт меньше минуты ⏱"
    )

    # 4) typing…
    await bot.send_chat_action(message.chat.id, "typing")
    await asyncio.sleep(1)

    # 5) Кнопка "Начать"
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📐 Рассчитать стоимость проекта", callback_data="start_quiz_project"))
    await message.answer("Готовы начать?", reply_markup=kb)

# КНОПКА «Начать проект»
@dp.callback_query_handler(lambda c: c.data == "start_quiz_project")
async def start_quiz_project(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.finish()

    await call.message.edit_text("✏️ Вопрос 1: Из какого материала планируете строить?")
    await call.message.edit_reply_markup(build_keyboard([
        "Кирпич",
        "Каркас / Брус",
        "Газобетон / Монолит",
        "Пока не определился, нужна консультация"
    ]))

    await QuizProject.q1.set()

# ВОПРОС 2
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

# ВОПРОС 3
@dp.callback_query_handler(state=QuizProject.q2)
async def qp2(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(q2=call.data)

    await call.message.edit_text("Вопрос 3: Какую общую площадь вы рассматриваете?")
    await call.message.edit_reply_markup(build_keyboard([
        "до 150 м²",
        "до 250 м²",
        "до 500 м²",
        "Более 500 м²"
    ]))

    await QuizProject.q3.set()

# ВОПРОС 4
@dp.callback_query_handler(state=QuizProject.q3)
async def qp3(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(q3=call.data)

    await call.message.edit_text("Есть ли у вас эскиз-проект, который нравится?")
    await call.message.edit_reply_markup(build_keyboard([
        "Да, есть проект, который нравится",
        "Есть картинка, рисунок, фото, которые нравятся",
        "Выберу из каталога",
        "Нет"
    ]))

    await QuizProject.q4.set()

# ВОПРОС 5
@dp.callback_query_handler(state=QuizProject.q4)
async def qp4(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(q4=call.data)

    await call.message.edit_text("Когда вы планируете строительство?")
    await call.message.edit_reply_markup(build_keyboard([
        "В ближайшее время",
        "Через 1–3 месяца",
        "Через 3–6 месяцев",
        "Не знаю, нужна консультация"
    ]))

    await QuizProject.q5.set()

# ФИНАЛ — Телефон
@dp.callback_query_handler(state=QuizProject.q5)
async def qp5(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(q5=call.data)

    await call.message.answer("📲 Оставьте ваш телефон для связи:", reply_markup=phone_kb())
    await QuizProject.phone.set()

@dp.message_handler(content_types=types.ContentTypes.CONTACT, state=QuizProject.phone)
async def qp_phone(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number
    data = await state.get_data()

    await bot.send_message(
        ADMIN_CHAT_ID,
        format_quiz(data, "Проектирование", phone)
    )

    await message.answer(
        "✅ Спасибо! Наш архитектор свяжется с вами в ближайшее время.",
        reply_markup=main_menu()
    )
    await state.finish()

# ---------------------------------------------
# STARTUP
# ---------------------------------------------
async def on_startup(dp):
    # На всякий случай очищаем вебхук, вдруг он был настроен раньше
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await bot.send_message(ADMIN_CHAT_ID, "✅ Бот СК «Вместе» запущен (long polling).")
    except Exception as e:
        logging.warning(f"Не удалось отправить сообщение администратору: {e}")

# ---------------------------------------------
# RUN
# ---------------------------------------------
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
