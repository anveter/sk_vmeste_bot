import logging
import os
from typing import Optional

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery, ContentType, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


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


MAIN_MENU_BUTTONS = [
    ["📋 О компании", "📁 Каталог проектов"],
    ["🏗 Расчёт стоимости дома", "✏️ Архитектурное проектирование"],
    ["🌐 Сайты компании", "📞 Контакты"],
]


ABOUT_TEXT = (
    "🏗 Строительная компания СК «Вместе» — это команда архитекторов, инженеров и специалистов, "
    "которые создают надёжные дома, продуманные проекты и комфортные пространства для жизни. Мы "
    "работаем «под ключ» и берём на себя всё: от идеи и проектирования до строительства, инженерии, "
    "отделки и благоустройства территории.\n\n"
    "❤️ Наш принцип прост — делаем так, как сделали бы для себя. Каждый проект — это не просто "
    "квадратные метры, а продуманная система, которая должна служить десятилетиями. Поэтому мы "
    "используем современные технологии, качественные материалы и проводим тщательный контроль на "
    "каждом этапе.\n\n"
    "🤝 Мы работаем открыто и честно: фиксированная смета, прозрачные процессы, регулярные отчёты, "
    "фото- и видеоконтроль объектов. Клиенты понимают, за что платят, и получают именно тот результат, "
    "который ожидают.\n\n"
    "🏦 Работаем со всеми видами финансирования: ипотека, материнский капитал, военная ипотека и другие "
    "форматы, требующие использования эскроу-счёта.\n\n"
    "🏠 Если вы хотите построить дом, заказать архитектурный проект или подобрать готовое решение — "
    "оставьте ваш номер телефона или напишите нам прямо сейчас. Наш специалист свяжется с вами, уточнит "
    "детали и предложит лучшие варианты под ваш бюджет."
)


START_MESSAGE = (
    "👋 Привет! Я бот компании СК «Вместе»\n\n"
    "Помогу рассчитать стоимость дома, подобрать проект\n"
    "или заказать архитектурное решение.\n\n"
    "Выберите действие из меню ниже 👇\n\n"
    "📝 Или оставьте заявку здесь 👉 /lead"
)


CATALOG_TEXT = (
    "📂 Каталог проектов:\n"
    "https://disk.yandex.ru/i/UBQkSxjZVyUKPw"
)

CONTACTS_TEXT = (
    "📞 <b>Контакты СК «Вместе»</b>\n\n"
    "📱 <b>Телефоны:</b>\n"
    "• +7 (928) 621-11-05\n"
    "• +7 (919) 892-94-02\n"
    "• +7 (918) 538-14-55\n\n"
    "📍 <b>Адрес офиса:</b>\n"
    "Ростов-на-Дону,\n"
    "Береговая 8 (Риверсайд), офис 512\n\n"
    "🔗 <b>Доп. контакты:</b>\n"
    "• Telegram-канал: https://t.me/skVmeste\n"
    "• Менеджер: https://t.me/wmeste851\n"
    "• WhatsApp: https://wa.me/79286211105"
)

COST_INTRO_PHOTO = "https://avatars.mds.yandex.net/get-altay/1879888/2a000001865205a565b7f2ceeb5211295fb7/XXL_height"
COST_INTRO_TEXT = (
    "Дома из кирпича, газобетона и монолита в Ростове-на-Дону с гарантией 5 лет напрямую от производителя “под ключ”\n\n"
    "Любая цветовая гамма и планировка!\n"
    "Семейная ипотека с применением эскроу-счёта 6%\n\n"
    "☑️ Штатные архитекторы и дизайнеры, без подрядчиков\n"
    "☑️ Фиксированная цена и сроки с поэтапной оплатой\n"
    "☑️ Сделаем бесплатный архитектурный проект — увидите свой дом ещё до постройки\n"
    "☑️ При необходимости снесем 1 объект и расчистим участок бесплатно\n\n"
    "Чтобы рассчитать ориентировочную стоимость дома, ответьте на несколько уточняющих вопросов. Это займёт меньше минуты ⏱"
)


DESIGN_INTRO_PHOTO = "https://ovikv.ru/new/img/podho_130325114/16.jpg"
DESIGN_INTRO_TEXT = (
    "📐 Архитектурное проектирование\n\n"
    "🏗 Разработаем полный проект и 3D-визуал вашего дома по СНиП\n"
    "💰 Стоимость от 400 руб/м² · Срок — до 30 дней\n"
    "Рассчитаем смету будущего строительства!\n\n"
    "Мы поможем вам сэкономить до 1 млн рублей за счёт правильного подбора материалов, инженерных решений и грамотной структуры проекта.\n\n"
    "Чтобы рассчитать стоимость проектирования и подготовить персональное предложение — ответьте на несколько коротких вопросов. Это займёт меньше минуты ⏱"
)


def main_menu() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for row in MAIN_MENU_BUTTONS:
        keyboard.row(*row)
    return keyboard


def contact_request_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton("📲 Отправить контакт", request_contact=True))
    return keyboard


def about_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="📝 Оставить заявку", callback_data="lead"))
    keyboard.add(InlineKeyboardButton(text="💬 Написать менеджеру", url="https://t.me/wmeste851"))
    return keyboard


def sites_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="🏠 Основной сайт — https://ск-вместе.рф", url="https://ск-вместе.рф"))
    keyboard.add(InlineKeyboardButton(text="📐 Проектирование — https://ск-вместе-проектирование.рф", url="https://ск-вместе-проектирование.рф"))
    return keyboard

def contacts_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)

    # Телефоны
    kb.add(InlineKeyboardButton("📞 Позвонить +7 (928) 621-11-05", url="tel:+79286211105"))
    kb.add(InlineKeyboardButton("📞 Позвонить +7 (919) 892-94-02", url="tel:+79198929402"))
    kb.add(InlineKeyboardButton("📞 Позвонить +7 (918) 538-14-55", url="tel:+79185381455"))

    # Остальные контакты
    kb.add(InlineKeyboardButton("📣 Telegram-канал", url="https://t.me/skVmeste"))
    kb.add(InlineKeyboardButton("👤 Менеджер", url="https://t.me/wmeste851"))
    kb.add(InlineKeyboardButton("🟢 Написать в WhatsApp", url="https://wa.me/79286211105"))

    return kb

def cost_intro_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="➡️ Рассчитать стоимость дома", callback_data="cost_quiz_start"))
    return keyboard


def design_intro_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="📐 Рассчитать стоимость проекта", callback_data="design_quiz_start"))
    return keyboard


def question_keyboard(options: list[str]) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for option in options:
        keyboard.add(option)
    return keyboard


def get_admin_chat_id() -> Optional[int]:
    if ADMIN_CHAT_ID and ADMIN_CHAT_ID.isdigit():
        return int(ADMIN_CHAT_ID)
    return None

@dp.message_handler(commands=["start"])
async def start_command(message: types.Message) -> None:
    await message.answer(START_MESSAGE, reply_markup=main_menu())


@dp.message_handler(commands=["lead"])
async def lead_command(message: types.Message) -> None:
    await LeadForm.waiting_for_name.set()
    await message.answer("Шаг 1 – как вас зовут?", reply_markup=ReplyKeyboardRemove())


@dp.callback_query_handler(text="lead")
async def lead_from_callback(callback_query: CallbackQuery) -> None:
    await callback_query.answer()
    await LeadForm.waiting_for_name.set()
    await callback_query.message.answer("Шаг 1 – как вас зовут?", reply_markup=ReplyKeyboardRemove())


@dp.message_handler(state=LeadForm.waiting_for_name, content_types=ContentType.TEXT)
async def lead_name(message: types.Message, state: FSMContext) -> None:
    await state.update_data(name=message.text.strip())
    await LeadForm.waiting_for_contact.set()
    await message.answer("Шаг 2 – отправьте телефон", reply_markup=contact_request_keyboard())


@dp.message_handler(state=LeadForm.waiting_for_contact, content_types=[ContentType.CONTACT, ContentType.TEXT])
async def lead_contact(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    name = data.get("name", "")
    phone = message.contact.phone_number if message.contact else message.text.strip()
    admin_chat_id = get_admin_chat_id()
    if admin_chat_id:
        await bot.send_message(admin_chat_id, f"Новая заявка\nИмя: {name}\nТелефон: {phone}")
    await message.answer("✅ Спасибо! Мы свяжемся с вами.", reply_markup=main_menu())
    await state.finish()


@dp.message_handler(lambda msg: msg.text == "📋 О компании")
async def about_company(message: types.Message) -> None:
    await message.answer(ABOUT_TEXT, reply_markup=about_keyboard())


@dp.message_handler(lambda msg: msg.text == "📁 Каталог проектов")
async def catalog_handler(message: types.Message) -> None:
    await message.answer(CATALOG_TEXT)


@dp.message_handler(lambda msg: msg.text == "🌐 Сайты компании")
async def sites_handler(message: types.Message) -> None:
    await message.answer("Выберите сайт:", reply_markup=sites_keyboard())

@dp.message_handler(lambda msg: msg.text == "📞 Контакты")
async def contacts_handler(message: types.Message):
    await message.answer(CONTACTS_TEXT, reply_markup=contacts_keyboard())
    
@dp.message_handler(lambda msg: msg.text == "🏗 Расчёт стоимости дома")
async def cost_intro(message: types.Message) -> None:
    await bot.send_photo(message.chat.id, COST_INTRO_PHOTO, caption=COST_INTRO_TEXT, reply_markup=cost_intro_keyboard())


@dp.callback_query_handler(text="cost_quiz_start")
async def start_cost_quiz(callback_query: CallbackQuery) -> None:
    await callback_query.answer()
    await CostQuiz.floors.set()
    options = ["1 этаж", "С мансардой", "2 этажа"]
    await callback_query.message.answer("1️⃣ Сколько этажей будет в доме?", reply_markup=question_keyboard(options))


@dp.message_handler(state=CostQuiz.floors, content_types=ContentType.TEXT)
async def cost_floors(message: types.Message, state: FSMContext) -> None:
    await state.update_data(floors=message.text)
    await CostQuiz.material.set()
    options = ["Кирпич", "Каркас / Брус", "Газобетон / Монолит", "Пока не определился, нужна консультация"]
    await message.answer("2️⃣ Из какого материала планируете строить дом?", reply_markup=question_keyboard(options))


@dp.message_handler(state=CostQuiz.material, content_types=ContentType.TEXT)
async def cost_material(message: types.Message, state: FSMContext) -> None:
    await state.update_data(material=message.text)
    await CostQuiz.area.set()
    options = ["до 100 м²", "100–150 м²", "150–200 м²", "Больше 200 м²"]
    await message.answer("3️⃣ Какую общую площадь вы рассматриваете?", reply_markup=question_keyboard(options))


@dp.message_handler(state=CostQuiz.area, content_types=ContentType.TEXT)
async def cost_area(message: types.Message, state: FSMContext) -> None:
    await state.update_data(area=message.text)
    await CostQuiz.project.set()
    options = ["Есть готовый проект", "Есть картинка, рисунок, чертеж", "Выберу из каталога", "Хочу индивидуальный проект (бесплатно)"]
    await message.answer("4️⃣ У вас есть проект, который нравится?", reply_markup=question_keyboard(options))


@dp.message_handler(state=CostQuiz.project, content_types=ContentType.TEXT)
async def cost_project(message: types.Message, state: FSMContext) -> None:
    await state.update_data(project=message.text)
    await CostQuiz.timeline.set()
    options = ["В ближайшее время", "Через 1–3 месяца", "Через 3–6 месяцев", "Не знаю, нужна консультация"]
    await message.answer("5️⃣ Когда планируете строительство?", reply_markup=question_keyboard(options))


@dp.message_handler(state=CostQuiz.timeline, content_types=ContentType.TEXT)
async def cost_timeline(message: types.Message, state: FSMContext) -> None:
    await state.update_data(timeline=message.text)
    await CostQuiz.phone.set()
    await message.answer("6️⃣ Телефон:\n📲 Оставьте телефон — мы подготовим расчёт стоимости и свяжемся с вами.", reply_markup=contact_request_keyboard())


@dp.message_handler(state=CostQuiz.phone, content_types=[ContentType.CONTACT, ContentType.TEXT])
async def cost_phone(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    phone = message.contact.phone_number if message.contact else message.text.strip()
    admin_chat_id = get_admin_chat_id()
    summary = (
        "Анкета — Расчёт стоимости дома\n"
        f"Этажность: {data.get('floors')}\n"
        f"Материал: {data.get('material')}\n"
        f"Площадь: {data.get('area')}\n"
        f"Проект: {data.get('project')}\n"
        f"Сроки: {data.get('timeline')}\n"
        f"Телефон: {phone}"
    )
    if admin_chat_id:
        await bot.send_message(admin_chat_id, summary)
    await message.answer("✅ Спасибо! Мы свяжемся с вами.", reply_markup=main_menu())
    await state.finish()


@dp.message_handler(lambda msg: msg.text == "✏️ Архитектурное проектирование")
async def design_intro(message: types.Message) -> None:
    await bot.send_photo(message.chat.id, DESIGN_INTRO_PHOTO, caption=DESIGN_INTRO_TEXT, reply_markup=design_intro_keyboard())


@dp.callback_query_handler(text="design_quiz_start")
async def start_design_quiz(callback_query: CallbackQuery) -> None:
    await callback_query.answer()
    await DesignQuiz.material.set()
    options = ["Кирпич", "Каркас / Брус", "Газобетон / Монолит", "Пока не определился, нужна консультация"]
    await callback_query.message.answer("1️⃣ Из какого материала планируете строить?", reply_markup=question_keyboard(options))


@dp.message_handler(state=DesignQuiz.material, content_types=ContentType.TEXT)
async def design_material(message: types.Message, state: FSMContext) -> None:
    await state.update_data(material=message.text)
    await DesignQuiz.floors.set()
    options = ["1 этаж", "2 этажа", "3 этажа", "Другое"]
    await message.answer("2️⃣ Сколько этажей будет в доме?", reply_markup=question_keyboard(options))


@dp.message_handler(state=DesignQuiz.floors, content_types=ContentType.TEXT)
async def design_floors(message: types.Message, state: FSMContext) -> None:
    await state.update_data(floors=message.text)
    await DesignQuiz.area.set()
    options = ["до 150 м²", "до 250 м²", "до 500 м²", "Более 500 м²"]
    await message.answer("3️⃣ Какую общую площадь вы рассматриваете?", reply_markup=question_keyboard(options))


@dp.message_handler(state=DesignQuiz.area, content_types=ContentType.TEXT)
async def design_area(message: types.Message, state: FSMContext) -> None:
    await state.update_data(area=message.text)
    await DesignQuiz.draft.set()
    options = ["Да, есть проект, который нравится", "Есть картинка, рисунок, фото", "Выберу из каталога", "Нет"]
    await message.answer("4️⃣ Есть ли у вас эскиз-проект, который нравится?", reply_markup=question_keyboard(options))


@dp.message_handler(state=DesignQuiz.draft, content_types=ContentType.TEXT)
async def design_draft(message: types.Message, state: FSMContext) -> None:
    await state.update_data(draft=message.text)
    await DesignQuiz.timeline.set()
    options = ["В ближайшее время", "Через 1–3 месяца", "Через 3–6 месяцев", "Не знаю, нужна консультация"]
    await message.answer("5️⃣ Когда вы планируете строительство?", reply_markup=question_keyboard(options))


@dp.message_handler(state=DesignQuiz.timeline, content_types=ContentType.TEXT)
async def design_timeline(message: types.Message, state: FSMContext) -> None:
    await state.update_data(timeline=message.text)
    await DesignQuiz.phone.set()
    await message.answer("6️⃣ Телефон:\n📲 Оставьте ваш телефон для связи.", reply_markup=contact_request_keyboard())


@dp.message_handler(state=DesignQuiz.phone, content_types=[ContentType.CONTACT, ContentType.TEXT])
async def design_phone(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    phone = message.contact.phone_number if message.contact else message.text.strip()
    admin_chat_id = get_admin_chat_id()
    summary = (
        "Анкета — Архитектурное проектирование\n"
        f"Материал: {data.get('material')}\n"
        f"Этажи: {data.get('floors')}\n"
        f"Площадь: {data.get('area')}\n"
        f"Эскиз: {data.get('draft')}\n"
        f"Сроки: {data.get('timeline')}\n"
        f"Телефон: {phone}"
    )
    if admin_chat_id:
        await bot.send_message(admin_chat_id, summary)
    await message.answer("✅ Спасибо! Мы свяжемся с вами.", reply_markup=main_menu())
    await state.finish()


@dp.message_handler()
async def fallback(message: types.Message) -> None:
    await message.answer("Выберите действие из меню ниже 👇", reply_markup=main_menu())


def main() -> None:
    executor.start_polling(dp, skip_updates=True)


if __name__ == "__main__":
    main()
