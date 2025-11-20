# ---------------------------------------------
# КВИЗ №1 — РАСЧЁТ СТОИМОСТИ ДОМА (НОВАЯ ВЕРСИЯ)
# ---------------------------------------------
@dp.message_handler(lambda m: m.text == "🏗 Расчёт стоимости дома")
async def quiz_build_intro(message: types.Message, state: FSMContext):
    await state.finish()

    # 1) Фото перед квизом
    await message.answer_photo(
        photo="https://avatars.mds.yandex.net/get-altay/1879888/2a000001865205a565b7f2ceeb5211295fb7/XXL_height",
        caption=(
            "<b>🏗 Разработаем полный проект и 3D-визуал вашего дома по СНиП</b>\n"
            "от <b>400 руб/м²</b> за 30 дней\n\n"
            "Ответьте на несколько уточняющих вопросов — это займёт меньше минуты ⏱"
        )
    )

    # typing эффект
    await bot.send_chat_action(message.chat.id, "typing")
    await asyncio.sleep(1)

    # 2) Текст под фото (как на скрине)
    intro_text = (
        "Поможем сэкономить <b>до 1 млн рублей</b> за счёт подобранных материалов "
        "и инженерных решений.\n\n"
        "⏳ Срок выполнения — до 30 дней.\n"
        "📐 Рассчитаем смету будущего строительства!"
    )

    await message.answer(intro_text)

    # 3) Кнопка
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("➡️ Рассчитать стоимость дома", callback_data="start_quiz_build"))

    await message.answer("Готовы начать?", reply_markup=kb)


# -------------------------------------------------------
# СТАРТ КВИЗА
# -------------------------------------------------------
@dp.callback_query_handler(lambda c: c.data == "start_quiz_build")
async def quiz_build_start(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.finish()

    await bot.send_chat_action(call.message.chat.id, "typing")
    await asyncio.sleep(1)

    await call.message.edit_text("🏗 Вопрос 1: Сколько этажей будет в доме?")
    await call.message.edit_reply_markup(build_keyboard([
        "1 этаж",
        "С мансардой",
        "2 этажа"
    ]))

    await QuizBuild.q1.set()


# -------------------------------------------------------
# ВОПРОС 2 — МАТЕРИАЛ
# -------------------------------------------------------
@dp.callback_query_handler(state=QuizBuild.q1)
async def build_q1(call, state):
    await call.answer()
    await state.update_data(q1=call.data)

    await call.message.edit_text("Вопрос 2: Из какого материала планируете строить дом?")
    await call.message.edit_reply_markup(build_keyboard([
        "Кирпич",
        "Каркас / Брус",
        "Газобетон / Монолит",
        "Пока не определился, нужна консультация"
    ]))

    await QuizBuild.q2.set()


# -------------------------------------------------------
# ВОПРОС 3 — ПЛОЩАДЬ
# -------------------------------------------------------
@dp.callback_query_handler(state=QuizBuild.q2)
async def build_q2(call, state):
    await call.answer()
    await state.update_data(q2=call.data)

    await call.message.edit_text("Вопрос 3: Какую общую площадь Вы рассматриваете?")
    await call.message.edit_reply_markup(build_keyboard([
        "до 100 м²",
        "100–150 м²",
        "150–200 м²",
        "Больше 200 м²"
    ]))

    await QuizBuild.q3.set()


# -------------------------------------------------------
# ВОПРОС 4 — ПРОЕКТ
# -------------------------------------------------------
@dp.callback_query_handler(state=QuizBuild.q3)
async def build_q3(call, state):
    await call.answer()
    await state.update_data(q3=call.data)

    await call.message.edit_text("Вопрос 4: У Вас есть проект, который нравится?")
    await call.message.edit_reply_markup(build_keyboard([
        "Есть готовый проект",
        "Есть картинка, рисунок, чертеж",
        "Выберу из каталога",
        "Хочу индивидуальный проект (для Вас бесплатно)"
    ]))

    await QuizBuild.q4.set()


# -------------------------------------------------------
# ВОПРОС 5 — СРОКИ
# -------------------------------------------------------
@dp.callback_query_handler(state=QuizBuild.q4)
async def build_q4(call, state):
    await call.answer()
    await state.update_data(q4=call.data)

    await call.message.edit_text("Вопрос 5: Когда Вы планируете строительство?")
    await call.message.edit_reply_markup(build_keyboard([
        "В ближайшее время",
        "Через 1–3 месяца",
        "Через 3–6 месяцев",
        "Не знаю, нужна консультация"
    ]))

    await QuizBuild.q5.set()


# -------------------------------------------------------
# КОНТАКТЫ
# -------------------------------------------------------
@dp.callback_query_handler(state=QuizBuild.q5)
async def build_q5(call, state):
    await call.answer()
    await state.update_data(q5=call.data)

    await call.message.answer(
        "📲 Оставьте телефон — мы подготовим расчёт стоимости и свяжемся с вами:",
        reply_markup=phone_kb()
    )

    await QuizBuild.phone.set()


# -------------------------------------------------------
# ФИНАЛ
# -------------------------------------------------------
@dp.message_handler(content_types=types.ContentTypes.CONTACT, state=QuizBuild.phone)
async def build_finish(message, state):
    phone = message.contact.phone_number
    data = await state.get_data()

    await bot.send_message(
        ADMIN_CHAT_ID,
        format_quiz(data, "Расчёт стоимости дома", phone)
    )

    await message.answer(
        "✅ Спасибо! Мы подготовим ориентировочную стоимость и свяжемся с вами.",
        reply_markup=main_menu()
    )

    await state.finish()
