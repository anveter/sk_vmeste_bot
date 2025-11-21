import logging
import os

from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
WEBHOOK_BASE = os.getenv("WEBHOOK_BASE_URL") or os.getenv("WEBHOOK_URL") or os.getenv("WEB_APP_URL")

if not BOT_TOKEN or not ADMIN_CHAT_ID:
    raise RuntimeError("BOT_TOKEN и ADMIN_CHAT_ID обязательны!")

if not WEBHOOK_BASE:
    raise RuntimeError("WEBHOOK_BASE_URL или WEBHOOK_URL обязательны для вебхука!")

PORT = int(os.getenv("PORT", 8080))
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_BASE.rstrip('/')}{WEBHOOK_PATH}"

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# ==================== КЛАВИАТУРЫ ====================
def main_menu() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("📋 О компании", "📁 Каталог проектов")
    kb.row("🏗 Расчёт стоимости дома", "✏️ Архитектурное проектирование")
    kb.row("🌐 Сайты компании", "📞 Контакты")
    return kb


def phone_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(KeyboardButton("📱 Отправить телефон", request_contact=True))
    kb.add(KeyboardButton("Отправлю позже"))
    return kb


def ikb(options) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    for text, code in options:
        kb.add(InlineKeyboardButton(text, callback_data=code))
    return kb


# ==================== СОСТОЯНИЯ ====================
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


# ==================== СТАРТ ====================
@dp.message_handler(commands=["start", "help"])
async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
        "👋 Привет! Я бот компании <b>СК «Вместе</b>\n\n"
        "Помогу рассчитать стоимость дома, подобрать проект "
        "или заказать архитектурное решение.\n\n"
        "Выберите действие из меню ниже 👇\n\n"
        "📝 Или оставьте заявку здесь 👉 /lead",
        reply_markup=main_menu(),
    )


# ==================== ОСТАЛЬНЫЕ РАЗДЕЛЫ ====================
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
    kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton("📝 Оставить заявку", callback_data="lead_open"),
        InlineKeyboardButton("💬 Написать менеджеру", url="https://t.me/wmeste851"),
    )
    await message.answer(text, reply_markup=kb)


@dp.message_handler(lambda m: m.text == "📁 Каталог проектов")
async def catalog(message: types.Message):
    await message.answer("📂 Каталог проектов:\nhttps://disk.yandex.ru/i/UBQkSxjZVyUKPw")


@dp.message_handler(lambda m: m.text == "🌐 Сайты компании")
async def sites(message: types.Message):
    kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton("🏠 Основной сайт", url="https://ск-вместе.рф"),
        InlineKeyboardButton("📐 Проектирование", url="https://ск-вместе-проектирование.рф"),
    )
    await message.answer("🌐 Наши официальные сайты:", reply_markup=kb)


@dp.message_handler(lambda m: m.text == "📞 Контакты")
async def contacts(message: types.Message):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("💬 Написать нам", url="https://t.me/wmeste851"),
        InlineKeyboardButton("📣 Telegram-канал", url="https://t.me/skVmeste"),
    )
    kb.add(
        InlineKeyboardButton("🟢 WhatsApp", url="https://wa.me/79286211105"),
        InlineKeyboardButton("📞 Позвонить", url="tel:+79286211105"),
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
        reply_markup=kb,
    )


# ==================== ЗАЯВКА ====================
@dp.callback_query_handler(lambda c: c.data == "lead_open")
async def lead_open(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.finish()
    await call.message.answer("✍️ Введите ваше имя:")
    await FormLead.name.set()


@dp.message_handler(commands=["lead"])
async def lead_cmd(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("✍️ Введите ваше имя:")
    await FormLead.name.set()


@dp.message_handler(state=FormLead.name)
async def lead_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("📱 Теперь отправьте телефон:", reply_markup=phone_kb())
    await FormLead.phone.set()


# ==================== УНИВЕРСАЛЬНЫЙ КОНТАКТ ====================
async def _send_lead_to_admin(state_name: str, phone: str, data: dict):
    if state_name == FormLead.phone.state:
        text = f"📝 <b>Новая заявка</b>\n👤 Имя: {data['name']}\n📞 Телефон: {phone}"
    elif state_name == QuizBuild.phone.state:
        text = (
            f"📋 <b>Анкета — Расчёт стоимости дома</b>\n\n"
            f"🏠 Этажность: {data.get('q1')}\n"
            f"🧱 Материал: {data.get('q2')}\n"
            f"📐 Площадь: {data.get('q3')}\n"
            f"📄 Проект: {data.get('q4')}\n"
            f"🕒 Сроки: {data.get('q5')}\n"
            f"📞 Телефон: {phone}"
        )
    elif state_name == QuizProject.phone.state:
        text = (
            f"📋 <b>Анкета — Архитектурное проектирование</b>\n\n"
            f"🧱 Материал: {data.get('q1')}\n"
            f"🏠 Этажность: {data.get('q2')}\n"
            f"📐 Площадь: {data.get('q3')}\n"
            f"📄 Эскиз: {data.get('q4')}\n"
            f"🕒 Сроки: {data.get('q5')}\n"
            f"📞 Телефон: {phone}"
        )
    else:
        text = f"📞 Получен контакт: {phone}"

    await bot.send_message(ADMIN_CHAT_ID, text)


async def _finalize_phone(message: types.Message, state: FSMContext, phone: str):
    data = await state.get_data()
    state_name = await state.get_state()
    await _send_lead_to_admin(state_name, phone, data)
    await message.answer("✅ Спасибо! Мы свяжемся с вами в ближайшее время.", reply_markup=main_menu())
    await state.finish()


@dp.message_handler(content_types=types.ContentType.CONTACT, state="*")
async def any_contact(message: types.Message, state: FSMContext):
    await _finalize_phone(message, state, message.contact.phone_number)


@dp.message_handler(state=[FormLead.phone, QuizBuild.phone, QuizProject.phone])
async def phone_text(message: types.Message, state: FSMContext):
    await _finalize_phone(message, state, message.text)


# ==================== КВИЗ 1 — РАСЧЁТ СТОИМОСТИ ДОМА ====================
async def _qb_send_q1(message: types.Message):
    await message.edit_text(
        "Вопрос 1 из 5\n\n🏗 Сколько этажей будет в доме?",
        reply_markup=ikb([
            ("1 этаж", "qb1_1"),
            ("С мансардой", "qb1_m"),
            ("2 этажа", "qb1_2"),
        ]),
    )


async def _qb_send_q2(call: types.CallbackQuery, state: FSMContext):
    answers = {"qb1_1": "1 этаж", "qb1_m": "С мансардой", "qb1_2": "2 этажа"}
    await state.update_data(q1=answers[call.data])
    await QuizBuild.q2.set()
    await call.message.edit_text(
        "Вопрос 2 из 5\n\n🧱 Из какого материала планируете строить дом?",
        reply_markup=ikb([
            ("Кирпич", "qb2_1"),
            ("Каркас / Брус", "qb2_2"),
            ("Газобетон / Монолит", "qb2_3"),
            ("Пока не определился, нужна консультация", "qb2_4"),
        ]),
    )


async def _qb_send_q3(call: types.CallbackQuery, state: FSMContext):
    answers = {
        "qb2_1": "Кирпич",
        "qb2_2": "Каркас / Брус",
        "qb2_3": "Газобетон / Монолит",
        "qb2_4": "Пока не определился, нужна консультация",
    }
    await state.update_data(q2=answers[call.data])
    await QuizBuild.q3.set()
    await call.message.edit_text(
        "Вопрос 3 из 5\n\n📐 Какую общую площадь Вы рассматриваете?",
        reply_markup=ikb([
            ("до 100 м²", "qb3_1"),
            ("100–150 м²", "qb3_2"),
            ("150–200 м²", "qb3_3"),
            ("Больше 200 м²", "qb3_4"),
        ]),
    )


async def _qb_send_q4(call: types.CallbackQuery, state: FSMContext):
    answers = {
        "qb3_1": "до 100 м²",
        "qb3_2": "100–150 м²",
        "qb3_3": "150–200 м²",
        "qb3_4": "Больше 200 м²",
    }
    await state.update_data(q3=answers[call.data])
    await QuizBuild.q4.set()
    await call.message.edit_text(
        "Вопрос 4 из 5\n\n📄 У Вас есть проект, который нравится?",
        reply_markup=ikb([
            ("Есть готовый проект", "qb4_1"),
            ("Есть картинка, рисунок, чертеж", "qb4_2"),
            ("Выберу из каталога", "qb4_3"),
            ("Хочу индивидуальный проект (для Вас бесплатно)", "qb4_4"),
        ]),
    )


async def _qb_send_q5(call: types.CallbackQuery, state: FSMContext):
    answers = {
        "qb4_1": "Есть готовый проект",
        "qb4_2": "Есть картинка, рисунок, чертеж",
        "qb4_3": "Выберу из каталога",
        "qb4_4": "Хочу индивидуальный проект (для Вас беспатно)",
    }
    await state.update_data(q4=answers[call.data])
    await QuizBuild.q5.set()
    await call.message.edit_text(
        "Вопрос 5 из 5\n\n🕒 Когда Вы планируете строительство?",
        reply_markup=ikb([
            ("В ближайшее время", "qb5_1"),
            ("Через 1–3 месяца", "qb5_2"),
            ("Через 3–6 месяцев", "qb5_3"),
            ("Не знаю, нужна консультация", "qb5_4"),
        ]),
    )


async def _qb_request_phone(call: types.CallbackQuery, state: FSMContext):
    answers = {
        "qb5_1": "В ближайшее время",
        "qb5_2": "Через 1–3 месяца",
        "qb5_3": "Через 3–6 месяцев",
        "qb5_4": "Не знаю, нужна консультация",
    }
    await state.update_data(q5=answers[call.data])
    await QuizBuild.phone.set()
    await call.message.edit_text("Отлично! Остался последний шаг\n\n📲 Оставьте телефон — мы подготовим расчёт и свяжемся с вами:")
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(
        "Отлично! Остался последний шаг\n\n📲 Оставьте телефон — мы подготовим расчёт и свяжемся с вами:",
        reply_markup=phone_kb(),
    )


@dp.message_handler(lambda message: message.text == "🏗 Расчёт стоимости дома")
async def quiz_build_start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer_photo(
        photo="https://avatars.mds.yandex.net/get-altay/1879888/2a000001865205a565b7f2ceeb5211295fb7/XXL_height",
        caption="<b>🏗 Разработаем полный проект и 3D визуал вашего дома по СНиП</b>\n"
                "<b>от 400 руб/м² за 30 дней</b>\n\n"
                "💰 Поможем сэкономить <b>до 1 млн рублей</b> за счёт правильно подобранных материалов "
                "и инженерных решений.\n\n"
                "⏳ Срок выполнения — до 30 дней.\n"
                "📐 Рассчитаем смету будущего строительства!",
    )
    await message.answer(
        "Чтобы рассчитать ориентировочную стоимость дома, ответьте на несколько вопросов.\n"
        "Это займёт меньше минуты ⏱"
    )
    await message.answer(
        "Готовы начать?",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("➡️ Рассчитать стоимость дома", callback_data="qb_start")
        ),
    )


@dp.callback_query_handler(lambda c: c.data == "qb_start", state="*")
async def qb_q1(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.finish()
    await QuizBuild.q1.set()
    await _qb_send_q1(call.message)


@dp.callback_query_handler(lambda c: c.data.startswith("qb1_"), state=QuizBuild.q1)
async def qb_q2(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await _qb_send_q2(call, state)


@dp.callback_query_handler(lambda c: c.data.startswith("qb2_"), state=QuizBuild.q2)
async def qb_q3(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await _qb_send_q3(call, state)


@dp.callback_query_handler(lambda c: c.data.startswith("qb3_"), state=QuizBuild.q3)
async def qb_q4(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await _qb_send_q4(call, state)


@dp.callback_query_handler(lambda c: c.data.startswith("qb4_"), state=QuizBuild.q4)
async def qb_q5(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await _qb_send_q5(call, state)


@dp.callback_query_handler(lambda c: c.data.startswith("qb5_"), state=QuizBuild.q5)
async def qb_phone(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await _qb_request_phone(call, state)


# ==================== КВИЗ 2 — АРХИТЕКТУРНОЕ ПРОЕКТИРОВАНИЕ ====================
async def _qp_send_q1(call: types.CallbackQuery):
    await call.message.edit_caption(
        caption="Вопрос 1 из 5\n\nИз какого материала планируете строить?",
        reply_markup=ikb([
            ("Кирпич", "qp1_1"),
            ("Каркас / Брус", "qp1_2"),
            ("Газобетон / Монолит", "qp1_3"),
            ("Пока не определился, нужна консультация", "qp1_4"),
        ]),
        parse_mode="HTML",
    )


async def _qp_send_q2(call: types.CallbackQuery, state: FSMContext):
    mapping = {
        "qp1_1": "Кирпич",
        "qp1_2": "Каркас / Брус",
        "qp1_3": "Газобетон / Монолит",
        "qp1_4": "Пока не определился, нужна консультация",
    }
    await state.update_data(q1=mapping[call.data])
    await QuizProject.q2.set()
    await call.message.edit_caption(
        caption="Вопрос 2 из 5\n\nСколько этажей будет в доме?",
        reply_markup=ikb([
            ("1 этаж", "qp2_1"),
            ("2 этажа", "qp2_2"),
            ("3 этажа", "qp2_3"),
            ("Другое", "qp2_4"),
        ]),
        parse_mode="HTML",
    )


async def _qp_send_q3(call: types.CallbackQuery, state: FSMContext):
    mapping = {"qp2_1": "1 этаж", "qp2_2": "2 этажа", "qp2_3": "3 этажа", "qp2_4": "Другое"}
    await state.update_data(q2=mapping[call.data])
    await QuizProject.q3.set()
    await call.message.edit_caption(
        caption="Вопрос 3 из 5\n\nКакую общую площадь вы рассматриваете?",
        reply_markup=ikb([
            ("до 150 м²", "qp3_1"),
            ("до 250 м²", "qp3_2"),
            ("до 500 м²", "qp3_3"),
            ("Более 500 м²", "qp3_4"),
        ]),
        parse_mode="HTML",
    )


async def _qp_send_q4(call: types.CallbackQuery, state: FSMContext):
    mapping = {
        "qp3_1": "до 150 м²",
        "qp3_2": "до 250 м²",
        "qp3_3": "до 500 м²",
        "qp3_4": "Более 500 м²",
    }
    await state.update_data(q3=mapping[call.data])
    await QuizProject.q4.set()
    await call.message.edit_caption(
        caption="Вопрос 4 из 5\n\nЕсть ли у вас эскиз-проект, который нравится?",
        reply_markup=ikb([
            ("Да, есть проект, который нравится", "qp4_1"),
            ("Есть картинка, рисунок, фото, которые нравятся", "qp4_2"),
            ("Выберу из каталога", "qp4_3"),
            ("Нет", "qp4_4"),
        ]),
        parse_mode="HTML",
    )


async def _qp_send_q5(call: types.CallbackQuery, state: FSMContext):
    mapping = {
        "qp4_1": "Да, есть проект, который нравится",
        "qp4_2": "Есть картинка, рисунок, фото, которые нравятся",
        "qp4_3": "Выберу из каталога",
        "qp4_4": "Нет",
    }
    await state.update_data(q4=mapping[call.data])
    await QuizProject.q5.set()
    await call.message.edit_caption(
        caption="Вопрос 5 из 5\n\nКогда вы планируете строительство?",
        reply_markup=ikb([
            ("В ближайшее время", "qp5_1"),
            ("Через 1–3 месяца", "qp5_2"),
            ("Через 3–6 месяцев", "qp5_3"),
            ("Не знаю, нужна консультация", "qp5_4"),
        ]),
        parse_mode="HTML",
    )


async def _qp_request_phone(call: types.CallbackQuery, state: FSMContext):
    mapping = {
        "qp5_1": "В ближайшее время",
        "qp5_2": "Через 1–3 месяца",
        "qp5_3": "Через 3–6 месяцев",
        "qp5_4": "Не знаю, нужна консультация",
    }
    await state.update_data(q5=mapping[call.data])
    await QuizProject.phone.set()
    await call.message.edit_caption(
        caption="Отлично! Остался последний шаг\n\nОставьте ваш телефон для связи:",
        parse_mode="HTML",
    )
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(
        "Отлично! Остался последний шаг\n\nОставьте ваш телефон дя связи:",
        reply_markup=phone_kb(),
    )


@dp.message_handler(lambda m: m.text == "✏️ Архитектурное проектирование")
async def quiz_project_start(message: types.Message, state: FSMContext):
    await state.finish()
    full_text = (
        "<b>🏗 Разработаем полный проект и 3D-визуал вашего дома по СНиП</b>\n"
        "💰 <b>Стоимость от 400 руб/м² · Срок — до 30 дней</b>\n"
        "📐 Рассчитаем смету будущего строительства!\n\n"
        "Мы поможем вам сэкономить <b>до 1 млн рублей</b> за счёт правильного подбора материалов, "
        "инженерных решений и грамотной структуры проекта.\n\n"
        "Чтобы рассчитать стоимость проектирования и подготовить персональное предложение — "
        "ответьте, пожалуйста, на несколько коротких вопросов. Это займёт меньше минуты ⏱"
    )
    await message.answer_photo(
        photo="https://ovikv.ru/new/img/podho_130325114/16.jpg",
        caption=full_text,
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("Рассчитать стоимость проекта", callback_data="qp_start")
        ),
        parse_mode="HTML",
    )


@dp.callback_query_handler(lambda c: c.data == "qp_start", state="*")
async def qp_q1(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.finish()
    await QuizProject.q1.set()
    await _qp_send_q1(call)


@dp.callback_query_handler(lambda c: c.data.startswith("qp1_"), state=QuizProject.q1)
async def qp_q2(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await _qp_send_q2(call, state)


@dp.callback_query_handler(lambda c: c.data.startswith("qp2_"), state=QuizProject.q2)
async def qp_q3(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await _qp_send_q3(call, state)


@dp.callback_query_handler(lambda c: c.data.startswith("qp3_"), state=QuizProject.q3)
async def qp_q4(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await _qp_send_q4(call, state)


@dp.callback_query_handler(lambda c: c.data.startswith("qp4_"), state=QuizProject.q4)
async def qp_q5(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await _qp_send_q5(call, state)


@dp.callback_query_handler(lambda c: c.data.startswith("qp5_"), state=QuizProject.q5)
async def qp_phone(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await _qp_request_phone(call, state)


# ==================== ВЕБХУК И ЗАПУСК ====================
async def handle_webhook(request: web.Request) -> web.Response:
    if request.match_info.get("token") != BOT_TOKEN:
        return web.Response(status=403)

    update_data = await request.json()
    update = types.Update(**update_data)
    await dp.process_update(update)
    return web.Response(text="ok")


async def on_startup(app: web.Application):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    await bot.send_message(ADMIN_CHAT_ID, "✅ Бот СК «Вместе» запущен и готов к работе!")


async def on_shutdown(app: web.Application):
    await bot.delete_webhook()
    await dp.storage.close()
    await dp.storage.wait_closed()
    await bot.session.close()


def main():
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle_webhook)
    app.router.add_get("/", lambda _: web.Response(text="OK"))
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    web.run_app(app, host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    main()
