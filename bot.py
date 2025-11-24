@dp.message_handler(lambda msg: msg.text == "📁 Каталог проектов")
async def catalog_handler(message: types.Message) -> None:
    await message.answer(CATALOG_TEXT)


@dp.message_handler(lambda msg: msg.text == "🌐 Сайты компании")
async def sites_handler(message: types.Message) -> None:
    await message.answer("Выберите сайт:", reply_markup=sites_keyboard())


@dp.message_handler(lambda msg: msg.text == "📞 Контакты")
async def contacts_handler(message: types.Message) -> None:
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
