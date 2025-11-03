import logging
import csv
import os
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

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

class Quiz1(StatesGroup):
    q1 = State(); q2 = State(); q3 = State(); q4 = State(); q5 = State(); q6 = State(); name = State(); phone = State()

class Quiz2(StatesGroup):
    q1 = State(); q2 = State(); q3 = State(); q4 = State(); q5 = State(); q6 = State(); name = State(); phone = State()

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

@dp.message_handler(lambda m: m.text == "Отмена", state="*")
async def cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Действие отменено.", reply_markup=main_kb)

# — Квиз 1 —
@dp.message_handler(state=Quiz1.q1)
async def q1(message: types.Message, state: FSMContext):
    await state.update_data(q1=message.text)
    kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Кирпич", "Монолит", "Газобетон", "Пока не определился нужна консультация", "Отмена")
    await message.answer("Из какого материала будем строить дом?", reply_markup=kb)
    await Quiz1.next()

@dp.message_handler(state=Quiz1.q2)
async def q2(message: types.Message, state: FSMContext):
    await state.update_data(q2=message.text)
    kb = ReplyKeyboardMarkup(resize_keyboard=True).add("До 100м2", "100-150м2", "150-200м2", "Больше 200м2", "Отмена")
    await message.answer("Какую общую площадь Вы рассматриваете?", reply_markup=kb)
    await Quiz1.next()

@dp.message_handler(state=Quiz1.q3)
async def q3(message: types.Message, state: FSMContext):
    await state.update_data(q3=message.text)
    kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Есть готовый проект", "Есть картинка рисунок чертеж", "Выберу из каталога", "Хочу индивидуальный проект(Бесплатно)", "Отмена")
    await message.answer("У Вас есть проект, который нравится?", reply_markup=kb)
    await Quiz1.next()

@dp.message_handler(state=Quiz1.q4)
async def q4(message: types.Message, state: FSMContext):
    await state.update_data(q4=message.text)
    kb = ReplyKeyboardMarkup(resize_keyboard=True).add("В ближайшее время", "Через 1-3 месяца", "Через 3-6 месяцев", "Не знаю нужна консультация", "Отмена")
    await message.answer("Когда планируете строительство?", reply_markup=kb)
    await Quiz1.next()

@dp.message_handler(state=Quiz1.q5)
async def q5(message: types.Message, state: FSMContext):
    await state.update_data(q5=message.text)
    kb = ReplyKeyboardMarkup(resize_keyboard=True).add("По телефону", "WhatsApp", "Telegram", "Отмена")
    await message.answer("Куда удобнее получить расчёт и бонусы?", reply_markup=kb)
    await Quiz1.next()

@dp.message_handler(state=Quiz1.q6)
async def q6(message: types.Message, state: FSMContext):
    await state.update_data(q6=message.text)
    await message.answer("Введите имя для связи:")
    await Quiz1.name.set()

@dp.message_handler(state=Quiz1.name)
async def name_handler(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    kb = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("📱 Отправить контакт", request_contact=True))
    await message.answer("📞 Отправьте свой номер:", reply_markup=kb)
    await Quiz1.phone.set()

@dp.message_handler(content_types=["contact"], state=Quiz1.phone)
async def phone_handler(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number
    data = await state.get_data()
    row = {"quiz": "Расчёт стоимости дома", **data, "phone": phone}
    save_to_csv(row)
    text = (f"<b>Новая заявка — Расчёт стоимости дома</b>\n"
            f"Имя: {row['name']}\nТелефон: {row['phone']}\n"
            f"Этажность: {row['q1']}\nМатериал: {row['q2']}\nПлощадь: {row['q3']}\n"
            f"Проект: {row['q4']}\nСрок: {row['q5']}\nСпособ связи: {row['q6']}")
    await notify_admin(text)
    await message.answer("Спасибо! Ваша заявка отправлена. Мы свяжемся с вами в ближайшее время.", reply_markup=main_kb)
    await state.finish()

# — Квиз 2 —
@dp.message_handler(state=Quiz2.q1)
async def a1(message: types.Message, state: FSMContext):
    await state.update_data(q1=message.text)
    kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Кирпич", "Монолит", "Газобетон", "Пока не определился нужна консультация", "Отмена")
    await message.answer("Из какого материала хотите проект?", reply_markup=kb)
    await Quiz2.next()

@dp.message_handler(state=Quiz2.q2)
async def a2(message: types.Message, state: FSMContext):
    await state.update_data(q2=message.text)
    kb = ReplyKeyboardMarkup(resize_keyboard=True).add("До 100м2", "100-150м2", "150-200м2", "Больше 200м2", "Отмена")
    await message.answer("Какую площадь дома рассматриваете?", reply_markup=kb)
    await Quiz2.next()

@dp.message_handler(state=Quiz2.q3)
async def a3(message: types.Message, state: FSMContext):
    await state.update_data(q3=message.text)
    kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Есть готовый проект", "Есть картинка рисунок чертеж", "Выберу из каталога", "Хочу индивидуальный проект(Бесплатно)", "Отмена")
    await message.answer("Есть ли проект, который нравится?", reply_markup=kb)
    await Quiz2.next()

@dp.message_handler(state=Quiz2.q4)
async def a4(message: types.Message, state: FSMContext):
    await state.update_data(q4=message.text)
    kb = ReplyKeyboardMarkup(resize_keyboard=True).add("В ближайшее время", "Через 1-3 месяца", "Через 3-6 месяцев", "Не знаю нужна консультация", "Отмена")
    await message.answer("Когда планируете начать проектирование?", reply_markup=kb)
    await Quiz2.next()

@dp.message_handler(state=Quiz2.q5)
async def a5(message: types.Message, state: FSMContext):
    await state.update_data(q5=message.text)
    kb = ReplyKeyboardMarkup(resize_keyboard=True).add("По телефону", "WhatsApp", "Telegram", "Отмена")
    await message.answer("Где удобнее получить консультацию и расчёт?", reply_markup=kb)
    await Quiz2.next()

@dp.message_handler(state=Quiz2.q6)
async def a6(message: types.Message, state: FSMContext):
    await state.update_data(q6=message.text)
    await message.answer("Введите имя:")
    await Quiz2.name.set()

@dp.message_handler(state=Quiz2.name)
async def a_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    kb = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("📱 Отправить контакт", request_contact=True))
    await message.answer("📞 Отправьте свой номер:", reply_markup=kb)
    await Quiz2.phone.set()

@dp.message_handler(content_types=["contact"], state=Quiz2.phone)
async def a_phone(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number
    data = await state.get_data()
    row = {"quiz": "Архитектурное проектирование", **data, "phone": phone}
    save_to_csv(row)
    text = (f"<b>Новая заявка — Архитектурное проектирование</b>\n"
            f"Имя: {row['name']}\nТелефон: {row['phone']}\n"
            f"Этажность: {row['q1']}\nМатериал: {row['q2']}\nПлощадь: {row['q3']}\n"
            f"Проект: {row['q4']}\nСрок: {row['q5']}\nСпособ связи: {row['q6']}")
    await notify_admin(text)
    await message.answer("Спасибо! Ваша заявка отправлена. Мы свяжемся с вами.", reply_markup=main_kb)
    await state.finish()

@dp.message_handler(content_types=["contact"])
async def save_contact(message: types.Message):
    contact = message.contact
    text = f"<b>Контакт</b>\nИмя: {contact.first_name}\nТелефон: {contact.phone_number}"
    await notify_admin(text)
    save_to_csv({"form": "contact", "name": contact.first_name, "phone": contact.phone_number})
    await message.answer("Спасибо! Мы свяжемся с вами.", reply_markup=main_kb)

@dp.message_handler()
async def fallback(message: types.Message):
    await message.answer("Выберите действие из меню 👇", reply_markup=main_kb)

if __name__ == "__main__":
    from keep_alive import keep_alive
    keep_alive()
    print("Бот запущен...")
    executor.start_polling(dp, skip_updates=True)