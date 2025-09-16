import random
from aiogram import Bot, Dispatcher, types, executor
from aiogram.utils.exceptions import BadRequest
from config import admin_id, bot_token, group_id, payment_token
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from Keyboards.reply import main_menu
from Keyboards.inline import (
    main_user_inline,
    main_admin_inline,
    admin_panel_inline,
    list_category_inline,
    category_add_product_inline,
)
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import (
    select_all_product_in_category_db,
    insert_data_to_db,
    change_name_db,
    change_description_db,
    get_lst_name_db,
    change_price_db,
    delete_product_db,
    change_img_db,
    insert_data_to_verify_users_db,
    get_list_verify_users_db,
    get_scoring_verify_users_db,
    get_date_birth_verify_users_db,
    get_fio_verify_users_db,
)
from aiogram.dispatcher.filters.state import StatesGroup, State
from telegram_bot_calendar import DetailedTelegramCalendar, MONTH
from aiogram.dispatcher import FSMContext
from telegram_bot_pagination import InlineKeyboardPaginator
from datetime import date
from verify_users import pool_for_verify
from get_distance_for_delivery import get_distance
from calculation_price_with_scoring import calc_pledge, calc_pledge_without_scoring
from creation_act_and_contract import insert_data_to_act_func, create_contract
import os
import re
from amocrm_create_lead import create_new_lead_func
from split_order_data_for_lead import split_func
import logging


storage = MemoryStorage()
bot = Bot(token=bot_token)
dp = Dispatcher(bot, storage=storage)

private_count = {}
private_info = {}
private_price_delivery = {}
private_message_id = {}


# --- ID ПЛАТЕЖА В ГРУППУ С ЗАКАЗАМИ, ОТПРАВКА НЕСКОЛЬКИХ ФОТО, АТОМАТИЧЕСКИЙ ВЫБОР КАТЕГОРИИ В ЛИД ------


# Группа для добавления продукта
class Add_new_product(StatesGroup):
    step_category = State()
    step_name = State()
    step_description = State()
    step_price = State()
    step_img = State()


# Группа для рассылка
class Distribution(StatesGroup):
    verification = State()
    send_distribution = State()


# Группа для изменения имени
class Name(StatesGroup):
    change_name = State()


# Группа для изменения описания
class Description(StatesGroup):
    change_description = State()


# Группа для изменения цены
class Price(StatesGroup):
    change_price = State()


# Группа для изменения фото
class Img(StatesGroup):
    change_img = State()


# Группа для подтверждения для удаления
class Verification(StatesGroup):
    verification_del = State()


# Группа для выбора даты и проверки паспортных данных
class Choice_date(StatesGroup):
    first_date = State()
    last_date = State()
    rent_verify = State()


# Группа для проверки пользователей
class Verify(StatesGroup):
    start_verify = State()
    verify = State()


# Группа для доставки
class Delivery(StatesGroup):
    address_delivery = State()
    price_delivery = State()


# Группа для выбора количества с доставкой
class Select_count(StatesGroup):
    get_count = State()


# Группа для выбора количества без доставкой
class Select_amount(StatesGroup):
    get_amount = State()


# Группа для отправки заказа на обработку и получения номера с датой доставки
class Status_order(StatesGroup):
    send_to_verify = State()


# Список пользователей бота
list_users_file = open("List_users/list_users.txt", "r")
list_users = set()
for id_users in list_users_file:
    list_users.add(id_users.strip())
list_users_file.close()


# Обработка команды "/start"
@dp.message_handler(commands=["start"])
async def start_func(message: types.message):
    if str(message.chat.id) not in list_users:
        with open("List_users/list_users.txt", "a") as file:
            file.write(str(message.chat.id) + "\n")
        list_users.add(message.chat.id)

    if message.from_user.id in admin_id:
        await message.answer(
            f"Вы авторизовались как администратор!", reply_markup=main_menu()
        )
    else:
        await message.answer(
            f"*Вас приветствует сервис аренды Aura!* " f"⬇️",
            reply_markup=main_menu(),
            parse_mode="Markdown",
        )


# Главное менюa, кнопка которая внизу
@dp.message_handler(content_types=["text"])
async def text_command_func(message: types.Message):
    global private_info, private_price_delivery, private_count
    try:
        del private_info[message.chat.id]
        del private_price_delivery[message.chat.id]
        del private_count[message.chat.id]

    except Exception as ex:
        print("text_command_func", ex)

    if message.text in "Главное меню":
        if message.from_user.id in admin_id:
            await message.answer(
                f"Вы вошли в главное меню как Администратор",
                reply_markup=main_admin_inline(),
            )
        else:
            await message.answer(
                f"Вы вошли в главное меню", reply_markup=main_user_inline()
            )

    else:
        await message.reply("Я тебя не понимаю")


# Обработка кнопоки 'Да' в группе
@dp.callback_query_handler(text="yes_verify")
async def yes_verify_func(call: types.CallbackQuery):
    global private_message_id
    order_info = call.message["text"]
    client_id = int(order_info.splitlines()[2].split(" ")[3])
    fio_client = await get_fio_verify_users_db(client_id)
    lst_data_for_lead = await split_func(order_info)

    await call.message.edit_text(
        text=f"{order_info}\n<b>ОДОБРЕН</b>", parse_mode="html"
    )

    # act_number = await create_new_lead_func(lst_data_for_lead)
    act_number = random.randint(1, 100)

    pdf_act = await insert_data_to_act_func(
        act_number=act_number, fio=fio_client, order_info=order_info
    )

    with open(pdf_act, "rb") as document:
        message_id_act = await bot.send_document(client_id, document)

    # Исключаем id телеги и скоринг для сообщения с информацией о заказе перед отправкой клиенту
    order_info = order_info.split("\n")[:2] + order_info.split("\n")[3:]
    order_info = "\n".join(str(x) for x in order_info)
    order_info = order_info.split("\n")[:2] + order_info.split("\n")[3:]
    info_in_message_for_client = "\n".join(str(x) for x in order_info)

    message_id = call.message.message_id
    private_message_id.setdefault(client_id, []).extend(
        [message_id, message_id_act.message_id, info_in_message_for_client]
    )

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("❌ Передумал", callback_data="no_payload"),
        InlineKeyboardButton("✅ Оплатить", callback_data="client_payload"),
    )
    await bot.send_message(
        client_id,
        f"{info_in_message_for_client}\n<b>Ваш заказ на аренду одобрен!</b>",
        parse_mode="html",
        reply_markup=markup,
    )


# Оплата товара после одобрения
@dp.callback_query_handler(text="client_payload")
async def payload_func(call: types.CallbackQuery):
    global private_message_id

    message_id = private_message_id.get(call.message.chat.id)[0]
    info_in_message = private_message_id.get(call.message.chat.id)[2]

    await bot.edit_message_text(
        f"{info_in_message}\n<b>КЛИЕНТ ПЕРЕХОДИТ К ОПЛАТЕ</b>",
        chat_id=group_id,
        message_id=message_id,
        parse_mode="html",
    )

    await call.message.edit_text(text=info_in_message)
    price = info_in_message.splitlines()[-1]
    price = int(price.split(" ")[3])

    name = info_in_message.splitlines()[0]

    label_price = types.LabeledPrice(label="Оплата услуг", amount=price * 100)
    await bot.send_invoice(
        call.message.chat.id,
        title=name,
        description="Оплата аренды",
        provider_token=payment_token,
        currency="RUB",
        prices=[label_price],
        start_parameter="payment-for-services",
        payload="invoice-payload",
    )


@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


@dp.message_handler(content_types=types.ContentTypes.SUCCESSFUL_PAYMENT)
async def success(message: types.Message):
    global private_message_id

    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton("Главное меню", callback_data="main_user"))
    await bot.send_message(
        message.chat.id,
        "Ожидайте звонка курьера либо менеджера!\nПо любым вопросам можно "
        "обратиться по номеру который указан в контактах. Раздел контакты в "
        "Главном меню",
        reply_markup=markup,
    )

    message_id = private_message_id.get(message.chat.id)[0]
    info_in_message = private_message_id.get(message.chat.id)[2]

    await bot.edit_message_text(
        f"{info_in_message}\n<b>КЛИЕНТ ОПЛАТИЛ</b>",
        chat_id=group_id,
        message_id=message_id,
        parse_mode="html",
    )

    try:
        del private_message_id[message.chat.id]
    except Exception as ex:
        print("success_func", ex)


# Клиент передумал после одобрения
@dp.callback_query_handler(text="no_payload")
async def no_payload_func(call: types.CallbackQuery):
    global private_info, private_price_delivery, private_count, private_message_id

    message_id = private_message_id.get(call.message.chat.id)[0]
    message_id_act = private_message_id.get(call.message.chat.id)[1]

    await bot.delete_message(group_id, message_id=message_id)
    await bot.delete_message(call.message.chat.id, message_id=message_id_act)

    try:
        del private_message_id[call.message.chat.id]
        del private_info[call.message.chat.id]
        del private_price_delivery[call.message.chat.id]
        del private_count[call.message.chat.id]

    except Exception as ex:
        print("no_payload_func", ex)

    if call.message.chat.id in admin_id:
        await call.message.edit_text(
            text="Главное меню", reply_markup=main_admin_inline()
        )
    else:
        await call.message.edit_text(
            text="Главное меню", reply_markup=main_user_inline()
        )


# Обработка кнопоки 'Нет' в группе
@dp.callback_query_handler(text="no_verify")
async def no_verify_func(call: types.CallbackQuery):
    order_info = call.message["text"]
    await call.message.edit_text(
        text=f"{order_info}\n<b>НЕ ОДОБРЕН</b>", parse_mode="html"
    )
    name_product = order_info.splitlines()[0]
    client_id = order_info.splitlines()[2].split(" ")[3]
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("Главное меню", callback_data="main_user"))
    await bot.send_message(
        client_id,
        f"К сожелению Ваш заказ на аренду {name_product} "
        f"был отменен!\nВ скором времени Вас наберет сотрудник для уточнения деталей!",
        reply_markup=markup,
    )


# Контакты
@dp.callback_query_handler(text="contacts")
async def contacts_func(call: types.CallbackQuery):
    exit_ = InlineKeyboardMarkup(row_width=1)
    exit_.row(InlineKeyboardButton("🔙 Главное меню", callback_data="main_user"))
    await call.message.edit_text(
        text="<b>📱 Телефон</b>\n+7 (812) 603-58-44\n<b>📍 Адрес</b>\n"
        "г. Санкт-Петербург, Лиговский проспект 43-45 Лит Б, офис 103\n<b>📧 E-mail</b>\n"
        "spb@aura-rent.ru",
        reply_markup=exit_,
        parse_mode="html",
    )


# Алмин-панель
@dp.callback_query_handler(text="admin_panel")
async def admin_panel_func(call: types.CallbackQuery):
    await call.message.edit_text("🔙 Админ-панель", reply_markup=admin_panel_inline())


# Главное меню
@dp.callback_query_handler(text="main_user")
async def main_func(call: types.CallbackQuery):
    global private_info, private_price_delivery, private_count
    try:
        del private_info[call.message.chat.id]
        del private_price_delivery[call.message.chat.id]
        del private_count[call.message.chat.id]

    except Exception as ex:
        print("main_func", ex)

    if call.message.chat.id in admin_id:
        await call.message.edit_text(
            text="Главное меню", reply_markup=main_admin_inline()
        )
    else:
        await call.message.edit_text(
            text="Главное меню", reply_markup=main_user_inline()
        )


# Каталог
@dp.callback_query_handler(text="catalog")
async def show_catalog_func(call: types.CallbackQuery):
    try:
        await call.message.edit_text("Каталог", reply_markup=list_category_inline())

    except BadRequest as error:
        print("show_catalog", error)
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await bot.send_message(
            call.message.chat.id, "Каталог", reply_markup=list_category_inline()
        )


# Список продуктов в категории
@dp.callback_query_handler(text_contains="Category_")
async def show_products_func(call: types.CallbackQuery, state: FSMContext):
    global private_count, private_info, private_price_delivery
    try:
        del private_info[call.message.chat.id]
        del private_price_delivery[call.message.chat.id]

    except Exception as ex:
        print("show_products", ex)

    # Показать первый продукт
    if "product" not in call.data:

        private_count.update({call.message.chat.id: 1})
        page = private_count.get(call.message.chat.id)

        this_category = call.data[9:]
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        list_products = await select_all_product_in_category_db(this_category)

        if len(list_products) == 1:
            page = 0
        try:
            await send_page_func(call.message, this_category, page)

            async with state.proxy() as data:

                data["description"] = list_products[page][3]
                data["price"] = list_products[page][4]
                data["old_name"] = list_products[page][1]
                data["old_path_img"] = list_products[page][2]
                data["this_category"] = this_category

        except IndexError as index_error:
            print("if 'product' not in call.Product_data:", index_error)
            back = InlineKeyboardMarkup(row_width=1)
            back.row(InlineKeyboardButton("Выйти в каталог", callback_data="catalog"))
            await bot.send_message(
                chat_id=call.message.chat.id,
                text="Товар в этой категории временно отсутствует",
                reply_markup=back,
            )

    # Пагинация
    elif "Category_product_page" in call.data:

        page = int(call.data.split("#")[1])
        private_count.update({call.message.chat.id: page})

        data = await state.get_data()
        this_category = data["this_category"]

        check = 1
        await send_page_func(call.message, this_category, page, check)

    # Выбор даты, и определение цены (после нажатия на цену)
    elif "Category_product_price+" in call.data:

        data = await state.get_data()
        this_category = data["this_category"]

        page = private_count.get(call.message.chat.id)

        list_products = await select_all_product_in_category_db(this_category)
        name = list_products[page - 1][1]
        img_path = list_products[page - 1][2]
        description = list_products[page - 1][3]
        price = list_products[page - 1][4]

        DetailedTelegramCalendar.first_step = MONTH
        calendar, step = DetailedTelegramCalendar(
            locale="ru", min_date=date.today()
        ).build()
        with open(img_path, "rb") as file:
            photo = types.InputMediaPhoto(
                file,
                caption=f"<b>{name}</b>\nОписание: {description}\nЦена за сутки: {price} ₽"
                f"\nНачало аренды: -\nКонец аренды: -"
                f"\n<b>Выберите дату начала и конца аренды ⬇️</b>",
                parse_mode="html",
            )

            await bot.edit_message_media(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                media=photo,
                reply_markup=calendar,
            )

        await Choice_date.first_date.set()

    # Изменение даты продукта
    elif "Category_product+" in call.data:

        this_category = call.data.split("+")[1]
        page = private_count.get(call.message.chat.id)

        async with state.proxy() as new_data:
            new_data["this_category"] = this_category

        list_products = await select_all_product_in_category_db(this_category)
        name = list_products[page - 1][1]
        img_path = list_products[page - 1][2]
        description = list_products[page - 1][3]
        price = list_products[page - 1][4]

        DetailedTelegramCalendar.first_step = MONTH
        calendar, step = DetailedTelegramCalendar(
            locale="ru", min_date=date.today()
        ).build()
        with open(img_path, "rb") as file:
            photo = types.InputMediaPhoto(
                file,
                caption=f"<b>{name}</b>\nОписание: {description}\nЦена за сутки: {price} ₽"
                f"\nНачало аренды: -\nКонец аренды: -"
                f"\n<b>Выберите дату начала и конца аренды ⬇️</b>",
                parse_mode="html",
            )

            await bot.edit_message_media(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                media=photo,
                reply_markup=calendar,
            )

        await Choice_date.first_date.set()


# Пагинация
async def send_page_func(message, this_category, page, check=0):
    list_products = await select_all_product_in_category_db(this_category)
    name = list_products[page - 1][1]
    img_path = list_products[page - 1][2]
    description = list_products[page - 1][3]
    price = list_products[page - 1][4]

    paginator = InlineKeyboardPaginator(
        len(list_products),
        current_page=page,
        data_pattern="Category_product_page#{page}",
    )

    # Если check = 1, то сообщение с продуктом меняется
    if check == 1:
        if message.chat.id in admin_id:
            paginator.add_before(
                InlineKeyboardButton(
                    f"{price} ₽", callback_data="Category_product_price+"
                )
            )
            paginator.add_after(
                InlineKeyboardButton(
                    "✍️ Изм. Название", callback_data="Product_update_name"
                ),
                InlineKeyboardButton(
                    "✍️ Изм. Описание", callback_data="Product_update_description"
                ),
            )

            paginator.add_after(
                InlineKeyboardButton(
                    "💲 Изм. Цену", callback_data="Product_update_price"
                ),
                InlineKeyboardButton("🖼 Изм. Фото", callback_data="Product_update_img"),
            )

            paginator.add_after(
                InlineKeyboardButton("❌ Удалить", callback_data="Product_update_del")
            )
            paginator.add_after(
                InlineKeyboardButton("🔙 Выйти в каталог", callback_data="catalog")
            )
        else:
            paginator.add_before(
                InlineKeyboardButton(
                    f"{price} ₽", callback_data="Category_product_price+"
                )
            )
            paginator.add_after(
                InlineKeyboardButton("🔙 Выйти в каталог", callback_data="catalog")
            )

        with open(img_path, "rb") as file:
            photo = types.InputMediaPhoto(
                file,
                caption=f"<b>{name}</b>\nОписание: {description}\n",
                parse_mode="html",
            )
            try:
                await bot.edit_message_media(
                    chat_id=message.chat.id,
                    message_id=message.message_id,
                    media=photo,
                    reply_markup=paginator.markup,
                )
            except Exception as _ex:
                print(_ex)

    # Если check = 0, то сообщение с продуктом отправляется
    else:
        if message.chat.id in admin_id:
            paginator.add_before(
                InlineKeyboardButton(
                    f"{price} ₽", callback_data="Category_product_price+"
                )
            )
            paginator.add_after(
                InlineKeyboardButton(
                    "✍️ Изм. Название", callback_data="Product_update_name"
                ),
                InlineKeyboardButton(
                    "✍️ Изм. Описание", callback_data="Product_update_description"
                ),
            )

            paginator.add_after(
                InlineKeyboardButton(
                    "💲 Изм. Цену", callback_data="Product_update_price"
                ),
                InlineKeyboardButton("🖼 Изм. Фото", callback_data="Product_update_img"),
            )

            paginator.add_after(
                InlineKeyboardButton("❌ Удалить", callback_data="Product_update_del")
            )
            paginator.add_after(
                InlineKeyboardButton("🔙 Выйти в каталог", callback_data="catalog")
            )
        else:
            paginator.add_before(
                InlineKeyboardButton(
                    f"{price} ₽", callback_data="Category_product_price+"
                )
            )
            paginator.add_after(
                InlineKeyboardButton("🔙 Выйти в каталог", callback_data="catalog")
            )

        await bot.send_photo(
            chat_id=message.chat.id,
            photo=open(img_path, "rb"),
            caption=f"<b>{name}</b>\nОписание: {description}\n",
            parse_mode="html",
            reply_markup=paginator.markup,
        )


# Выбор даты, и определение цены
@dp.callback_query_handler(text_contains="cbcal_", state=Choice_date.first_date)
async def first_cal_func(call: types.CallbackQuery, state: FSMContext):
    global private_count
    first_result, key, step = DetailedTelegramCalendar(
        locale="ru", min_date=date.today()
    ).process(call.data)
    if not first_result and key:
        await call.message.edit_reply_markup(reply_markup=key)

    elif first_result:
        async with state.proxy() as data:
            data["first_result"] = first_result

        try:
            data = await state.get_data()
            this_category = data["this_category"]

        except KeyError as ex:
            print("elif first_result:", ex)
            new_data = await state.get_data()
            this_category = new_data["this_category"]

        page = private_count.get(call.message.chat.id)
        DetailedTelegramCalendar.first_step = MONTH
        calendar, step = DetailedTelegramCalendar(
            locale="ru", min_date=date.today()
        ).build()

        list_products = await select_all_product_in_category_db(this_category)
        name = list_products[page - 1][1]
        img_path = list_products[page - 1][2]
        description = list_products[page - 1][3]
        price = list_products[page - 1][4]
        first_result = first_result.strftime("%d.%m.%Y")

        with open(img_path, "rb") as file:
            photo = types.InputMediaPhoto(
                file,
                caption=f"<b>{name}</b>\nОписание: {description}\nЦена за сутки: {price} ₽"
                f"\nНачало аренды: {first_result}\nКонец "
                f"аренды: -\n<b>Выберите дату начала и конца аренды ⬇️</b>",
                parse_mode="html",
            )

            await bot.edit_message_media(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                media=photo,
                reply_markup=calendar,
            )
        await Choice_date.next()


@dp.callback_query_handler(text_contains="cbcal_", state=Choice_date.last_date)
async def second_cal_func(call: types.CallbackQuery, state: FSMContext):
    global private_count, private_info
    data = await state.get_data()
    this_category = data["this_category"]
    first_result = data["first_result"]

    end_result, key, step = DetailedTelegramCalendar(
        locale="ru", min_date=first_result
    ).process(call.data)
    if not end_result and key:
        await call.message.edit_reply_markup(reply_markup=key)

    elif end_result:

        page = private_count.get(call.message.chat.id)

        list_products = await select_all_product_in_category_db(this_category)
        name = list_products[page - 1][1]
        img_path = list_products[page - 1][2]
        description = list_products[page - 1][3]
        price = list_products[page - 1][4]

        diff = end_result - first_result
        duration_in_s = diff.total_seconds()
        days = divmod(duration_in_s, 86400)[0]
        price_with_date = price * int(days)

        if price_with_date == 0:
            price_with_date = price

        end_result = end_result.strftime("%d.%m.%Y")
        first_result = first_result.strftime("%d.%m.%Y")
        async with state.proxy() as data:
            data["price_with_date"] = price_with_date

        with open(img_path, "rb") as file:
            photo = types.InputMediaPhoto(
                file,
                caption=f"<b>{name}</b>\nОписание: {description}\nЦена за сутки: {price} ₽"
                f"\nНачало аренды: {first_result}\n"
                f"Конец аренды: {end_result}\n<b>Стоимость аренды "
                f"на выбранные "
                f"даты: {price_with_date}</b>",
                parse_mode="html",
            )

            markup = InlineKeyboardMarkup(row_width=2)

            if call.message.chat.id in get_list_verify_users_db():
                markup.add(
                    InlineKeyboardButton(
                        text="Заказать", callback_data=f"rent_verify+{this_category}"
                    )
                )

                private_info.setdefault(call.message.chat.id, []).extend(
                    [description, price_with_date, first_result, end_result]
                )
                await state.finish()

            else:
                markup.add(InlineKeyboardButton(text="Заказать", callback_data="rent"))
                await state.finish()

                private_info.setdefault(call.message.chat.id, []).extend(
                    [
                        description,
                        price_with_date,
                        first_result,
                        end_result,
                        this_category,
                    ]
                )

            markup.add(
                InlineKeyboardButton(
                    text="Изменить дату",
                    callback_data=f"Category_product+{this_category}",
                ),
                InlineKeyboardButton(
                    text="К товарам", callback_data=f"Category_{this_category}"
                ),
            )
            markup.add(
                InlineKeyboardButton(
                    text="Учесть стоимость доставки",
                    callback_data=f"delivery+" f"{this_category}",
                )
            )

            await bot.edit_message_media(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                media=photo,
                reply_markup=markup,
            )


@dp.callback_query_handler(text="rent")
async def rent_product_func(call: types.CallbackQuery):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("✖️ Не сейчас", callback_data="main_user"),
        InlineKeyboardButton("✅ Пройти проверку", callback_data="verify"),
    )

    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await bot.send_message(
        call.message.chat.id,
        "Для новых клиентов необходимо пройти проверку паспортных данных, "
        "чтобы определить залог. Фото отправлять не нужно, достаточно "
        "написать запрашиваемемые данные. Внимательно вводите данные, ведь "
        "при выдаче техники нужно предоставить паспорт! Если у Вас нет "
        "задолжностей то большая вероятность что будем работать без залога. "
        "Проверка проводиться раз в год.",
        reply_markup=markup,
    )


@dp.callback_query_handler(text_contains="rent_verify")
async def rent_verify_product_func(call: types.CallbackQuery):
    global private_info, private_count
    scoring = await get_scoring_verify_users_db(call.message.chat.id)
    date_birth = await get_date_birth_verify_users_db(call.message.chat.id)

    key = call.message.chat.id

    page = private_count.get(key)
    price_with_date = private_info.get(key)[1]
    first_result = private_info.get(key)[2]
    end_result = private_info.get(key)[3]

    this_category = call.data.split("+")[1]
    list_products = await select_all_product_in_category_db(this_category)
    name = list_products[page - 1][1]
    img_path = list_products[page - 1][2]
    description = list_products[page - 1][3]
    price = list_products[page - 1][4]

    check_code_in_scoring = scoring

    if "Информация не найдена" not in scoring:
        scoring = scoring.split("ая")[0][:-1]
        scoring = int(scoring.split(" ")[2])
        price_with_verify = await calc_pledge(
            description, scoring, check_code_in_scoring
        )
    elif "Информация не найдена" in scoring:
        price_with_verify = await calc_pledge_without_scoring(description, date_birth)

    with open(img_path, "rb") as file:
        photo = types.InputMediaPhoto(
            file,
            caption=f"<b>{name}</b>\nОписание: {description}\nЦена за сутки: {price} ₽"
            f"\nНачало аренды: {first_result}\n"
            f"Конец аренды: {end_result}\nСтоимость аренды "
            f"на выбранные "
            f"даты: {price_with_date}\nЗалог: {price_with_verify}\n<b>"
            f"Всего к оплате: {price_with_verify + price_with_date}</b>",
            parse_mode="html",
        )

        markup = InlineKeyboardMarkup(row_width=2)

        markup.add(
            InlineKeyboardButton(text="Оформить", callback_data=f"pay_verify"),
            InlineKeyboardButton(
                text="К товарам", callback_data=f"Category_{this_category}"
            ),
        )
        markup.add(
            InlineKeyboardButton(
                text="Учесть стоимость доставки",
                callback_data=f"delivery+{this_category}",
            )
        )
        markup.add(
            InlineKeyboardButton(
                text="Выбрать количество",
                callback_data=f"select_amount+{this_category}",
            )
        )
        await bot.edit_message_media(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            media=photo,
            reply_markup=markup,
        )

        # Вся инфа для отправки запроса
        private_info.update(
            {
                call.message.chat.id: [
                    description,
                    price_with_date,
                    first_result,
                    end_result,
                    name,
                    price,
                    price_with_verify,
                    scoring,
                ]
            }
        )


@dp.callback_query_handler(text="verify")
async def verify_func(call: types.CallbackQuery):
    await call.message.edit_text(
        text="🔐 *Для прохождения проверки службой безопасности достаточно прислать:*"
        "\n"
        "1)ФИО\n"
        "2)Дату рождения\n"
        "3)Серию и номер паспорта\n"
        "4)Дата выдачи паспорта\n"
        "5)Код подразделения\n"
        "6)Кем выдан паспорт\n"
        "7)Регистрация по месту жительства\n"
        "8)Место жительства\n"
        "Данные отправляйте одним сообщением. Ниже приведен пример ⬇️",
        parse_mode="Markdown",
    )
    await bot.send_message(
        call.message.chat.id,
        "Иванов Иван Иванович\n"
        "01.01.2000\n"
        "1234 123456\n"
        "01.01.2000\n"
        "123-123\n"
        "Кем выдан\n"
        "СПб, Лиговский пр. 43-45Б\n"
        "СПб, Лиговский пр. 43-45Б",
    )

    await Verify.verify.set()


@dp.message_handler(state=Verify.verify)
async def second_verify_func(message: types.Message, state: FSMContext):
    global private_info, private_count
    data = message.text.split("\n")

    try:
        fio = data[0]
        date_birth = data[1]
        seria_number = data[2]
        date_issue = data[3]
        department_code = data[4]

        if (
            len(fio.split()) == 3
            and all([len(x) > 1 for x in fio.split()])
            and re.match("\\d{1,2}.\\d{1,2}.\\d{4}", date_birth)
            and re.match("\\d{4}.\\d{6}", seria_number)
            and re.match("\\d{1,2}.\\d{1,2}.\\d{4}", date_issue)
            and re.match("\\d{3}.\\d{3}", department_code)
        ):

            info = fio.split(" ")
            firstname = info[1]
            lastname = info[0]
            midname = info[2]

            mes_1 = await bot.send_message(message.chat.id, "Проверяю...")
            contract_file = await create_contract(message.chat.id, data)

            seria_number = seria_number.replace(" ", "")
            scoring = await pool_for_verify(
                lastname, firstname, midname, date_birth, seria_number, date_issue
            )
            date_verify = date.today().strftime("%d.%m.%Y")

            await insert_data_to_verify_users_db(
                message.chat.id, fio, date_verify, scoring, date_birth
            )

            await bot.delete_message(message.chat.id, mes_1.message_id)

            scoring = await get_scoring_verify_users_db(message.chat.id)
            date_birth = await get_date_birth_verify_users_db(message.chat.id)

            key = message.chat.id

            page = private_count.get(key)
            price_with_date = private_info.get(key)[1]
            first_result = private_info.get(key)[2]
            end_result = private_info.get(key)[3]
            this_category = private_info.get(key)[4]

            list_products = await select_all_product_in_category_db(this_category)
            name = list_products[page - 1][1]
            img_path = list_products[page - 1][2]
            description = list_products[page - 1][3]
            price = list_products[page - 1][4]

            check_code_in_scoring = scoring

            if "Информация не найдена" not in scoring:
                scoring = scoring.split("ая")[0][:-1]
                scoring = int(scoring.split(" ")[2])
                price_with_verify = await calc_pledge(
                    description, scoring, check_code_in_scoring
                )

            elif "Информация не найдена" in scoring:
                price_with_verify = await calc_pledge_without_scoring(
                    description, date_birth
                )

            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(
                InlineKeyboardButton(text="Оформить", callback_data=f"pay_verify"),
                InlineKeyboardButton(
                    text="К товарам", callback_data=f"Category_{this_category}"
                ),
            )
            markup.add(
                InlineKeyboardButton(
                    text="Учесть стоимость доставки",
                    callback_data=f"delivery+{this_category}",
                )
            )
            markup.add(
                InlineKeyboardButton(
                    text="Выбрать количество",
                    callback_data=f"select_amount+{this_category}",
                )
            )

            await bot.send_photo(
                chat_id=message.chat.id,
                photo=open(img_path, "rb"),
                caption=f"<b>{name}</b>\nОписание: {description}\nЦена за сутки: {price} ₽"
                f"\nНачало аренды: {first_result}\n"
                f"Конец аренды: {end_result}\nСтоимость аренды "
                f"на выбранные "
                f"даты: {price_with_date}\nЗалог: {price_with_verify}\n<b>"
                f"Всего к оплате: {price_with_verify + price_with_date}</b>",
                parse_mode="html",
                reply_markup=markup,
            )

            # Вся инфа для отправки запроса
            private_info.update(
                {
                    message.chat.id: [
                        description,
                        price_with_date,
                        first_result,
                        end_result,
                        name,
                        price,
                        price_with_verify,
                        scoring,
                    ]
                }
            )

            with open(contract_file, "rb") as document:
                pin_message = await bot.send_document(message.chat.id, document)
                await bot.pin_chat_message(
                    message.chat.id, message_id=pin_message.message_id
                )

            await state.finish()

        else:
            await state.finish()
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(
                InlineKeyboardButton("🔄 Ввести заново", callback_data="verify"),
                InlineKeyboardButton("🔙 Выйти", callback_data="main_user"),
            )
            await bot.send_message(
                message.chat.id, "Данные введены не верно!", reply_markup=markup
            )

    except Exception as ex:
        print("verify_1", ex)
        await state.finish()
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("🔄 Ввести заново", callback_data="verify"),
            InlineKeyboardButton("🔙 Выйти", callback_data="main_user"),
        )
        await bot.delete_message(message.chat.id, message_id=message.message_id - 2)
        await bot.delete_message(message.chat.id, message_id=message.message_id - 1)
        await bot.send_message(
            message.chat.id, "Данные введены не верно!", reply_markup=markup
        )


# Расчет доставки
@dp.callback_query_handler(text_contains="delivery+")
async def delivery_func(call: types.CallbackQuery, state: FSMContext):
    if call.message.chat.id not in get_list_verify_users_db():
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("✖️ Не сейчас", callback_data="main_user"),
            InlineKeyboardButton("✅ Пройти проверку", callback_data="verify"),
        )

        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await bot.send_message(
            call.message.chat.id,
            "Для новых клиентов необходимо пройти проверку паспортных данных, "
            "чтобы определить залог. Фото отправлять не нужно, достаточно "
            "написать запрашиваемемые данные. Внимательно вводите данные, ведь "
            "при выдаче техники нужно предоставить паспорт! Если у Вас нет "
            "задолжностей то большая вероятность что будем работать без залога. "
            "Проверка проводиться раз в год.",
            reply_markup=markup,
        )

    else:
        this_category = call.data.split("+")[1]

        async with state.proxy() as data:
            data["this_category"] = this_category

        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await bot.send_message(
            call.message.chat.id,
            "Введите адрес куда нужно доставить. Адрес вводите полный",
        )
        await Delivery.address_delivery.set()


@dp.message_handler(state=Delivery.address_delivery)
async def price_delivery_func(message: types.Message, state: FSMContext):
    global private_info, private_count
    data = await state.get_data()
    this_category = data["this_category"]
    try:
        address = message.text
        min_distance = await get_distance(message.text)
        if min_distance[1] > 1.5:
            minute = 10 * min_distance[1] * 3.5
            km = min_distance[1] * 17.5
            price_delivery = int(350 + 150 + km + minute)
        else:
            metr = min_distance[1] * 1000
            price_delivery = int(350 + 0.20 * metr)

        private_price_delivery.setdefault(message.chat.id, price_delivery)

        scoring = await get_scoring_verify_users_db(message.chat.id)
        date_birth = await get_date_birth_verify_users_db(message.chat.id)

        key = message.chat.id

        page = private_count.get(key)
        price_with_date = private_info.get(key)[1]
        first_result = private_info.get(key)[2]
        end_result = private_info.get(key)[3]

        list_products = await select_all_product_in_category_db(this_category)
        name = list_products[page - 1][1]
        img_path = list_products[page - 1][2]
        description = list_products[page - 1][3]
        price = list_products[page - 1][4]

        check_code_in_scoring = scoring

        if "Информация не найдена" not in scoring:
            scoring = scoring.split("ая")[0][:-1]
            scoring = int(scoring.split(" ")[2])
            price_with_verify = await calc_pledge(
                description, scoring, check_code_in_scoring
            )
        elif "Информация не найдена" in scoring:
            price_with_verify = await calc_pledge_without_scoring(
                description, date_birth
            )

        # Вся инфа для отправки запроса
        private_info.update(
            {
                message.chat.id: [
                    description,
                    price_with_date,
                    first_result,
                    end_result,
                    name,
                    price,
                    price_with_verify,
                    scoring,
                    price_delivery,
                    address,
                ]
            }
        )

        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton(text="Оформить", callback_data=f"pay_verify"),
            InlineKeyboardButton(
                text="К товарам", callback_data=f"Category_{this_category}"
            ),
        )
        markup.add(
            InlineKeyboardButton(
                text="Выбрать количество", callback_data=f"select_count+{this_category}"
            )
        )
        await bot.send_photo(
            chat_id=message.chat.id,
            photo=open(img_path, "rb"),
            caption=f"<b>{name}</b>\nОписание: {description}\nЦена за сутки: {price} ₽"
            f"\nНачало аренды: {first_result}\n"
            f"Конец аренды: {end_result}\nСтоимость аренды "
            f"на выбранные "
            f"даты: {price_with_date}\nЗалог: {price_with_verify}\n"
            f"Стоимость доставки: {price_delivery} р."
            f"\n<b>Всего к оплате: {price_with_verify + price_with_date + price_delivery}"
            f"</b>",
            parse_mode="html",
            reply_markup=markup,
        )

    except Exception as ex:
        print("price_delivery_fucn", ex)
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton("Главное меню"))
        await bot.send_message(
            message.chat.id, "Что-то пошло не так", reply_markup=markup
        )
    await state.finish()


# Выбор количества товара с доставкой
@dp.callback_query_handler(text_contains="select_count")
async def select_count_func(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["this_category"] = call.data.split("+")[1]

    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await bot.send_message(
        call.message.chat.id, "Введите количесвто арендуемой техники(цифрой)."
    )
    await Select_count.get_count.set()


@dp.message_handler(state=Select_count.get_count)
async def end_select_count_func(message: types.Message, state: FSMContext):
    global private_price_delivery, private_info
    data = await state.get_data()
    this_category = data["this_category"]
    try:
        count_product = int(message.text)
        scoring = await get_scoring_verify_users_db(message.chat.id)
        date_birth = await get_date_birth_verify_users_db(message.chat.id)
        price_delivery = int(private_price_delivery.get(message.chat.id))
        key = message.chat.id

        page = private_count.get(key)
        price_with_date = private_info.get(key)[1]
        first_result = private_info.get(key)[2]
        end_result = private_info.get(key)[3]
        address = private_info.get(key)[9]

        list_products = await select_all_product_in_category_db(this_category)
        name = list_products[page - 1][1]
        img_path = list_products[page - 1][2]
        description = list_products[page - 1][3]
        price = list_products[page - 1][4]
        check_code_in_scoring = scoring

        if "Информация не найдена" not in scoring:
            scoring = scoring.split("ая")[0][:-1]
            scoring = int(scoring.split(" ")[2])
            price_with_verify = await calc_pledge(
                description, scoring, check_code_in_scoring, count_product
            )

        elif "Информация не найдена" in scoring:
            price_with_verify = await calc_pledge_without_scoring(
                description, date_birth
            )

        # Вся инфа для отправки запроса
        private_info.update(
            {
                message.chat.id: [
                    description,
                    price_with_date,
                    first_result,
                    end_result,
                    name,
                    price,
                    price_with_verify,
                    scoring,
                    count_product,
                    price_delivery,
                    address,
                ]
            }
        )

        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton(text="Оформить", callback_data=f"pay_verify"),
            InlineKeyboardButton(
                text="К товарам", callback_data=f"Category_{this_category}"
            ),
        )
        await bot.send_photo(
            chat_id=message.chat.id,
            photo=open(img_path, "rb"),
            caption=f"<b>{name}</b>\n"
            f"Описание: {description}\n"
            f"Цена за сутки: {price} ₽\n"
            f"Начало аренды: {first_result}\n"
            f"Конец аренды: {end_result}\n"
            f"Стоимость аренды на выбранные даты: {price_with_date * count_product}\n"
            f"Залог: {price_with_verify * count_product}\n"
            f"Стоимость доставки: {price_delivery} р.\n"
            f"Количество: {count_product}\n"
            f"<b>Всего к оплате:</b> "
            f"{price_with_verify * count_product + price_with_date * count_product + price_delivery}",
            parse_mode="html",
            reply_markup=markup,
        )

    except ValueError as val_err:
        print("end_select_count, val_err", val_err)
        await state.finish()
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton(
                "Ввести заново", callback_data=f"select_count+{this_category}"
            )
        )
        await bot.send_message(message.chat.id, "Неверное число!", reply_markup=markup)

    except Exception as ex:
        print("end_select_count, ex", ex)

    await state.finish()


# Выбор количества товара без доставки
@dp.callback_query_handler(text_contains="select_amount")
async def select_amount_func(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["this_category"] = call.data.split("+")[1]

    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await bot.send_message(
        call.message.chat.id, "Введите количесвто арендуемой техники(цифрой)."
    )
    await Select_amount.get_amount.set()


@dp.message_handler(state=Select_amount.get_amount)
async def end_select_count_func(message: types.Message, state: FSMContext):
    global private_info
    data = await state.get_data()
    this_category = data["this_category"]
    try:
        count_product = int(message.text)

        scoring = await get_scoring_verify_users_db(message.chat.id)
        date_birth = await get_date_birth_verify_users_db(message.chat.id)

        key = message.chat.id
        page = private_count.get(key)
        price_with_date = private_info.get(key)[1]
        first_result = private_info.get(key)[2]
        end_result = private_info.get(key)[3]

        list_products = await select_all_product_in_category_db(this_category)
        name = list_products[page - 1][1]
        img_path = list_products[page - 1][2]
        description = list_products[page - 1][3]
        price = list_products[page - 1][4]
        check_code_in_scoring = scoring

        if "Информация не найдена" not in scoring:
            scoring = scoring.split("ая")[0][:-1]
            scoring = int(scoring.split(" ")[2])
            price_with_verify = await calc_pledge(
                description, scoring, check_code_in_scoring, count_product
            )

        elif "Информация не найдена" in scoring:
            price_with_verify = await calc_pledge_without_scoring(
                description, date_birth
            )

        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton(text="Оформить", callback_data=f"pay_verify"),
            InlineKeyboardButton(
                text="К товарам", callback_data=f"Category_{this_category}"
            ),
        )
        await bot.send_photo(
            chat_id=message.chat.id,
            photo=open(img_path, "rb"),
            caption=f"<b>{name}</b>\n"
            f"Описание: {description}\n"
            f"Цена за сутки: {price} ₽\n"
            f"Начало аренды: {first_result}\n"
            f"Конец аренды: {end_result}\n"
            f"Стоимость аренды на выбранные даты: {price_with_date * count_product}\n"
            f"Залог: {price_with_verify * count_product}\n"
            f"Количество: {count_product}\n"
            f"<b>Всего к оплате: "
            f"{price_with_verify * count_product + price_with_date * count_product}</b>",
            parse_mode="html",
            reply_markup=markup,
        )

        # Вся инфа для отправки запроса
        private_info.update(
            {
                message.chat.id: [
                    description,
                    price_with_date,
                    first_result,
                    end_result,
                    name,
                    price,
                    price_with_verify,
                    scoring,
                    count_product,
                ]
            }
        )

    except ValueError as val_err:
        print("end_select_count, val_err", val_err)
        await state.finish()
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton(
                "Ввести заново", callback_data=f"select_amount+{this_category}"
            )
        )
        await bot.send_message(message.chat.id, "Неверное число!", reply_markup=markup)

    except Exception as ex:
        print("end_select_count, ex", ex)

    await state.finish()


# Обработка оплаты и получения номера с датой доставки
@dp.callback_query_handler(text="pay_verify")
async def get_number_func(call: types.CallbackQuery):
    await bot.send_message(
        call.message.chat.id, "Отправьте номер номер телефона для обратной связи"
    )
    await Status_order.send_to_verify.set()


@dp.message_handler(state=Status_order.send_to_verify)
async def send_to_verify_func(message: types.Message, state: FSMContext):
    global private_info
    client_number = message.text

    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton("Главное меню!", callback_data="main_user"))
    await bot.send_message(
        message.chat.id, "Заявка отправлена, ожидайте результата!", reply_markup=markup
    )

    verify_button = InlineKeyboardMarkup(row_width=2)
    verify_button.add(
        InlineKeyboardButton("✅ Да", callback_data="yes_verify"),
        InlineKeyboardButton("❌ Нет", callback_data="no_verify"),
    )

    # Вся инфа для отправки запроса
    key = message.chat.id

    fio_client = await get_fio_verify_users_db(key)

    name = private_info.get(key)[4]
    description = private_info.get(key)[0]
    price = private_info.get(key)[5]
    first_result = private_info.get(key)[2]
    end_result = private_info.get(key)[3]
    price_with_date = private_info.get(key)[1]
    price_with_verify = private_info.get(key)[6]
    scoring = private_info.get(key)[7]
    if len(private_info.get(key)) == 9:
        try:
            count_product = private_info.get(key)[8]
            await bot.send_message(
                chat_id=group_id,
                text=f"<b>{name}</b>\n"
                f"Описание: {description}\n"
                f"ID в Тг: {key}\n"
                f"Скоринг: {scoring}\n"
                f"ФИО: {fio_client}\n"
                f"<b>Номер телефона:</b> {client_number}\n"
                f"Цена за сутки: {price} ₽\n"
                f"Начало аренды: {first_result}\n"
                f"Конец аренды: {end_result}\n"
                f"Стоимость аренды на выбранные даты: {price_with_date * count_product}\n"
                f"Залог: {price_with_verify * count_product}\n"
                f"Количество: {count_product}\n"
                f"<b>Всего к оплате: "
                f"{price_with_verify * count_product + price_with_date * count_product}</b>",
                parse_mode="html",
                reply_markup=verify_button,
            )
        except Exception as ex:
            print("send_to_verify_func_1", ex)

    elif len(private_info.get(key)) == 10:
        try:
            price_delivery = int(private_info.get(key)[8])
            address = private_info.get(key)[9]
            await bot.send_message(
                chat_id=group_id,
                text=f"<b>{name}</b>\n"
                f"Описание: {description}\n"
                f"ID в Тг: {key}\n"
                f"Скоринг: {scoring}\n"
                f"ФИО: {fio_client}\n"
                f"<b>Номер телефона:</b> {client_number}\n"
                f"Цена за сутки: {price} ₽\n"
                f"Начало аренды: {first_result}\n"
                f"Конец аренды: {end_result}\n"
                f"<b>Дата доставки:</b> {first_result}\n"
                f"Стоимость аренды на выбранные даты: {price_with_date}\n"
                f"Залог: {price_with_verify}\n"
                f"Стоимость доставки: {price_delivery} р.\n"
                f"<b>Адрес доставки:</b> {address}\n"
                f"<b>Всего к оплате: "
                f"{price_with_verify + price_with_date + price_delivery}</b>",
                parse_mode="html",
                reply_markup=verify_button,
            )
        except Exception as ex:
            print("send_to_verify_func_2", ex)
    elif len(private_info.get(key)) == 11:
        try:
            count_product = private_info.get(key)[8]
            price_delivery = int(private_info.get(key)[9])
            address = private_info.get(key)[10]
            await bot.send_message(
                chat_id=group_id,
                text=f"<b>{name}</b>\n"
                f"Описание: {description}\n"
                f"ID в Тг: {key}\n"
                f"Скоринг: {scoring}\n"
                f"ФИО: {fio_client}\n"
                f"<b>Номер телефона:</b> {client_number}\n"
                f"Цена за сутки: {price} ₽\n"
                f"Начало аренды: {first_result}\n"
                f"Конец аренды: {end_result}\n"
                f"<b>Дата доставки:</b> {first_result}\n"
                f"Стоимость аренды на выбранные даты: {price_with_date}\n"
                f"Залог: {price_with_verify}\n"
                f"Стоимость доставки: {price_delivery} р.\n"
                f"<b>Адрес доставки:</b> {address}\n"
                f"Количество: {count_product}\n"
                f"<b>Всего к оплате: "
                f"{price_with_verify + price_with_date + price_delivery}</b>",
                parse_mode="html",
                reply_markup=verify_button,
            )
        except Exception as ex:
            print("send_to_verify_func_3", ex)

    else:
        await bot.send_message(
            chat_id=group_id,
            text=f"<b>{name}</b>\n"
            f"Описание: {description}\n"
            f"ID в Тг: {key}\n"
            f"Скоринг: {scoring}\n"
            f"ФИО: {fio_client}\n"
            f"<b>Номер телефона:</b> {client_number}\n"
            f"Цена за сутки: {price} ₽\n"
            f"Начало аренды: {first_result}\n"
            f"Конец аренды: {end_result}\n"
            f"Стоимость аренды на выбранные даты: {price_with_date}\n"
            f"Залог: {price_with_verify}\n"
            f"<b>Всего к оплате: "
            f"{price_with_verify + price_with_date}</b>",
            parse_mode="html",
            reply_markup=verify_button,
        )

    await state.finish()


# Начало добавления товара
@dp.callback_query_handler(text="add")
async def product_category_func(call: types.CallbackQuery):
    await call.message.edit_text(
        "Укажите категорию продукта", reply_markup=category_add_product_inline()
    )
    await Add_new_product.step_category.set()


@dp.callback_query_handler(state=Add_new_product.step_category)
async def product_name_func(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Укажите название продукта")

    async with state.proxy() as data:
        data["category"] = call.data
    await Add_new_product.next()


@dp.message_handler(state=Add_new_product.step_name)
async def product_description_func(message: types.Message, state: FSMContext):
    name = message.text

    if name not in get_lst_name_db():
        async with state.proxy() as data:
            data["name"] = name
        await message.answer("Укажите описание продукта")
        await Add_new_product.next()

    else:
        await state.finish()
        markup = InlineKeyboardMarkup(row_width=1)
        markup.row(InlineKeyboardButton("🔙 Админ-панель", callback_data="admin_panel"))
        await bot.send_message(
            message.chat.id, "Такое название уже существует!", reply_markup=markup
        )


@dp.message_handler(state=Add_new_product.step_description)
async def product_price_func(message: types.Message, state: FSMContext):
    description = message.text
    async with state.proxy() as data:
        data["description"] = description
    await message.answer("Укажите цену продукта")
    await Add_new_product.next()


@dp.message_handler(state=Add_new_product.step_price)
async def product_img_func(message: types.Message, state: FSMContext):
    try:
        price = int(message.text)
        async with state.proxy() as data:
            data["price"] = price
        await message.answer("Отправьте фото продукта")
        await Add_new_product.next()

    except ValueError as val_err:
        print("product_img", val_err)
        await state.finish()
        markup = InlineKeyboardMarkup(row_width=1)
        markup.row(InlineKeyboardButton("🔙 Админ-панель", callback_data="admin_panel"))
        await bot.send_message(message.chat.id, "Неверная цена!", reply_markup=markup)


@dp.message_handler(content_types=["photo"], state=Add_new_product.step_img)
async def download_img_func(message, state: FSMContext):
    data = await state.get_data()
    name = data["name"]
    description = data["description"]
    category = data["category"]
    price = data["price"]
    await message.photo[-1].download(
        destination_file=f"Product_data/{category}/{name}.jpg"
    )
    img_path = f"Product_data/{category}/{name}.jpg"

    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton("🔙 Админ-панель", callback_data="admin_panel"))

    await message.answer(
        f"Название: {name}\nОписание: {description}\nКатегория: {category}\nЦена за сутки: {price}\nПродукт "
        f"добавлен в базу!",
        reply_markup=markup,
    )
    await insert_data_to_db(name, category, description, price, img_path)
    await state.finish()


# Начало рассылки
@dp.callback_query_handler(text="distribution")
async def distribution_func(call: types.CallbackQuery):
    await call.message.answer(
        f'Для подтвеврждения рассылки напишите без кавычек - "Подтверждаю рассылку"'
    )
    await Distribution.verification.set()


@dp.message_handler(state=Distribution.verification)
async def verif_distribution_func(message: types.Message, state=FSMContext):
    if message.text == "Подтверждаю рассылку":
        await message.answer(f"Ведите сообщение рассылки")
        await Distribution.next()
    else:
        back = InlineKeyboardMarkup(row_width=1)
        back.row(InlineKeyboardButton("🔙 Админ-панель", callback_data="admin_panel"))
        await message.answer(
            "Рассылка не подтверждена!\nАккаратнее! 😉", reply_markup=back
        )
        await state.finish()


@dp.message_handler(state=Distribution.send_distribution)
async def end_distribution_func(message: types.Message, state: FSMContext):
    distribution_text = message.text

    for user in list_users:
        await bot.send_message(user, distribution_text)

    back = InlineKeyboardMarkup(row_width=1)
    back.row(InlineKeyboardButton("🔙 Админ-панель", callback_data="admin_panel"))

    await message.answer("Сделано 😉", reply_markup=back)
    await state.finish()


# Изменения названия
@dp.callback_query_handler(text="Product_update_name")
async def change_name_func(call: types.CallbackQuery):
    await bot.send_message(call.message.chat.id, "Укажите новое название. Без слеша!")
    await Name.change_name.set()


@dp.message_handler(state=Name.change_name)
async def end_change_name_func(message: types.Message, state: FSMContext):
    global private_count

    data = await state.get_data()
    this_category = data["this_category"]

    list_products = await select_all_product_in_category_db(this_category)
    page = private_count.get(message.chat.id)
    old_name = list_products[page - 1][1]
    old_img_path = list_products[page - 1][2]
    new_name = message.text

    try:
        new_path_img = f"Product_data/{this_category}/{new_name}.jpg"
        os.rename(old_img_path, new_path_img)

        await change_name_db(this_category, old_name, new_name, new_path_img)
        back = InlineKeyboardMarkup(row_width=1)
        back.row(
            InlineKeyboardButton("🔙 Назад", callback_data=f"Category_{this_category}")
        )
        await message.answer("Имя успешно изменено", reply_markup=back)
        await state.finish()

    except FileExistsError as error:
        print("end_change_name", error)
        await state.finish()
        markup = InlineKeyboardMarkup(row_width=1)
        markup.row(
            InlineKeyboardButton("🔙 Выйти", callback_data=f"Category_{this_category}")
        )
        await bot.send_message(
            message.chat.id, "Такое имя уже существует!", reply_markup=markup
        )


# Изменения описания
@dp.callback_query_handler(text="Product_update_description")
async def change_description_func(call: types.CallbackQuery):
    await bot.send_message(call.message.chat.id, "Укажите новое описание")
    await Description.change_description.set()


@dp.message_handler(state=Description.change_description)
async def end_change_description_func(message: types.Message, state: FSMContext):
    global private_count

    data = await state.get_data()
    this_category = data["this_category"]

    list_products = await select_all_product_in_category_db(this_category)
    page = private_count.get(message.chat.id)
    old_name = list_products[page - 1][1]

    new_description = message.text

    await change_description_db(this_category, old_name, new_description)

    back = InlineKeyboardMarkup(row_width=1)
    back.row(
        InlineKeyboardButton("🔙 Назад", callback_data=f"Category_{this_category}")
    )
    await message.answer("Описание успешно изменено", reply_markup=back)
    await state.finish()


# Изменения цены
@dp.callback_query_handler(text="Product_update_price")
async def change_price_func(call: types.CallbackQuery):
    await bot.send_message(call.message.chat.id, "Укажите новую цену")
    await Price.change_price.set()


@dp.message_handler(state=Price.change_price)
async def end_change_price_func(message: types.Message, state: FSMContext):
    global private_count

    data = await state.get_data()
    this_category = data["this_category"]

    list_products = await select_all_product_in_category_db(this_category)
    page = private_count.get(message.chat.id)
    old_name = list_products[page - 1][1]

    try:
        new_price = int(message.text)

        await change_price_db(this_category, old_name, new_price)
        back = InlineKeyboardMarkup(row_width=1)
        back.row(
            InlineKeyboardButton("🔙 Назад", callback_data=f"Category_{this_category}")
        )
        await message.answer("Цена успешно изменена", reply_markup=back)
        await state.finish()

    except ValueError as error:
        print("end_change_price", error)
        await state.finish()
        back = InlineKeyboardMarkup(row_width=1)
        back.row(
            InlineKeyboardButton("🔙 Назад", callback_data=f"Category_{this_category}")
        )
        await bot.send_message(message.chat.id, "Неверная цена!", reply_markup=back)


# Подтверждение удаления
@dp.callback_query_handler(text="Product_update_del")
async def confirm_delete_func(call: types.CallbackQuery):
    await call.message.answer(
        'Вы точно хотите удалить товар?\nДля подтверждения напишите без кавычек - "Удалить товар"'
    )
    await Verification.verification_del.set()


@dp.message_handler(state=Verification.verification_del)
async def end_confirm_delete_func(message: types.Message, state: FSMContext):
    global private_count

    data = await state.get_data()
    this_category = data["this_category"]
    list_products = await select_all_product_in_category_db(this_category)
    page = private_count.get(message.chat.id)
    name = list_products[page - 1][1]

    if message.text == "Удалить товар":
        img_path = f"Product_data/{this_category}/{name}.jpg"

        await delete_product_db(name, this_category)
        os.remove(img_path)

        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("🔙 Назад", callback_data=f"Category_{this_category}")
        )

        await message.answer("Товар успешно удален!", reply_markup=markup)
        await state.finish()

    else:
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("🔙 Назад", callback_data=f"Category_{this_category}")
        )
        await message.answer(
            "Подтверждение не прошло!\nАккаратней!", reply_markup=markup
        )
        await state.finish()


# Изменение фото
@dp.callback_query_handler(text="Product_update_img")
async def change_img_func(call: types.CallbackQuery):
    await call.message.answer("Отправьте новое фото")
    await Img.change_img.set()


@dp.message_handler(content_types=["photo"], state=Img.change_img)
async def end_change_img_func(message, state: FSMContext):
    global private_count

    data = await state.get_data()
    this_category = data["this_category"]
    list_products = await select_all_product_in_category_db(this_category)
    page = private_count.get(message.chat.id)
    name = list_products[page - 1][1]

    await message.photo[-1].download(
        destination_file=f"Product_data/{this_category}/{name}.jpg"
    )
    new_img_path = f"Product_data/{this_category}/{name}.jpg"

    back = InlineKeyboardMarkup(row_width=1)
    back.row(
        InlineKeyboardButton("🔙 Назад", callback_data=f"Category_{this_category}")
    )

    await change_img_db(this_category, name, new_img_path)
    await message.answer("Фото успешно изменено", reply_markup=back)
    await state.finish()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=False)
