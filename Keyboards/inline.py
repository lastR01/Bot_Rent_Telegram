from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import show_list_category_db
from config import admin_id


# Функция для  авт. созд. инлайн кнопки
def auto_create_inline_button_inline():
    for name in show_list_category_db():
        callback = name
        name = name.replace("_", " ")[7:].title()


# Список категорий
def list_category_inline():
    category = InlineKeyboardMarkup(row_width=2)
    category.add(
        InlineKeyboardButton("Ноутбуки", callback_data="Category_Аренда_ноутбуков")
    )
    category.row(InlineKeyboardButton("🔙 Главное меню", callback_data="main_user"))
    return category


# Выбор категории для добавления продукта
def category_add_product_inline():
    category = InlineKeyboardMarkup(row_width=2)
    category.add(InlineKeyboardButton("Ноутбуки", callback_data="Аренда_ноутбуков"))
    return category


# Главное меню пользователя
def main_user_inline():
    main = InlineKeyboardMarkup(row_width=2)
    main.add(
        InlineKeyboardButton("🗂 Каталог", callback_data="catalog"),
        InlineKeyboardButton("📱 Контакты", callback_data="contacts"),
    )
    return main


# Главное меню админа
def main_admin_inline():
    main_admin = InlineKeyboardMarkup(row_width=2)
    main_admin.add(
        InlineKeyboardButton("🗂 Каталог", callback_data="catalog"),
        InlineKeyboardButton("📱 Контакты", callback_data="contacts"),
        InlineKeyboardButton("😎 Админ-панель", callback_data="admin_panel"),
    )
    return main_admin


# Админ-панель
def admin_panel_inline():
    admin_panel = InlineKeyboardMarkup(row_width=2)
    admin_panel.add(
        InlineKeyboardButton("➕ Добавить товар", callback_data="add"),
        InlineKeyboardButton("📢 Сделать рассылку", callback_data="distribution"),
        InlineKeyboardButton("🔙 Главное меню", callback_data="main_user"),
    )

    return admin_panel
