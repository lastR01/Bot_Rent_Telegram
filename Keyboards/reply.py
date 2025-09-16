from aiogram.types import ReplyKeyboardMarkup


def main_menu():
    main = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    main.add("Главное меню")
    return main
