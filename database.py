import sqlite3


# Создать таблицы с категориями
def create_table():
    category_name = ["Аренда_ноутбуков"]
    for name in category_name:
        with sqlite3.connect("DataBase/db_aura.db") as db:
            cursor = db.cursor()
            cursor.execute(
                f"""CREATE TABLE IF NOT EXISTS {name} (id INTEGER, name TEXT, img_path TEXT, description 
            TEXT,
            price INTEGER)"""
            )


# Создать таблицу для проверенных клиентов
def create_table_for_verify_users():
    table_name = ["Проверенные_клиенты"]
    for name in table_name:
        with sqlite3.connect("DataBase/db_aura.db") as db:
            cursor = db.cursor()
            cursor.execute(
                f"CREATE TABLE IF NOT EXISTS {name} (id_telegram INTEGER, fio TEXT, date_verify, scoring, "
                f"date_birth)"
            )


# Вставить данные продукта в таблицу
async def insert_data_to_db(name, category, description, price, img_path):
    with sqlite3.connect("DataBase/db_aura.db") as db:
        cursor = db.cursor()
        cursor.execute(
            f"INSERT INTO {category} (name, description, price, img_path) VALUES (?, ?, ?, ?)",
            (name, description, price, img_path),
        )
        db.commit()


# Изменить имя продукта
async def change_name_db(name_category, old_name, new_name, new_path_img):
    with sqlite3.connect("DataBase/db_aura.db") as db:
        cursor = db.cursor()
        cursor.execute(
            f"UPDATE {name_category} SET name='%s', img_path='%s' WHERE name='%s'"
            % (new_name, new_path_img, old_name)
        )
        db.commit()


# Изменить описание продукта
async def change_description_db(name_category, old_name, new_description):
    with sqlite3.connect("DataBase/db_aura.db") as db:
        cursor = db.cursor()
        cursor.execute(
            f"UPDATE {name_category} SET description='%s' WHERE name='%s'"
            % (new_description, old_name)
        )
        db.commit()


# Изменить цены продукта
async def change_price_db(name_category, old_name, new_price):
    with sqlite3.connect("DataBase/db_aura.db") as db:
        cursor = db.cursor()
        cursor.execute(
            f"UPDATE {name_category} SET price='%s' WHERE name='%s'"
            % (new_price, old_name)
        )
        db.commit()


# Изменить фото продукта
async def change_img_db(name_category, old_name, new_img):
    with sqlite3.connect("DataBase/db_aura.db") as db:
        cursor = db.cursor()
        cursor.execute(
            f"UPDATE {name_category} SET img_path='%s' WHERE name='%s'"
            % (new_img, old_name)
        )
        db.commit()


# Удаление продукта
async def delete_product_db(name, category):
    with sqlite3.connect("DataBase/db_aura.db") as db:
        cursor = db.cursor()
        cursor.execute(f'DELETE FROM {category} WHERE name = "{name}"')
        db.commit()


# Получить все продукты выбранной категории
async def select_all_product_in_category_db(category):
    with sqlite3.connect("DataBase/db_aura.db") as db:
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM {category}")
        info = cursor.fetchall()
    return info


# Вывод списка всех таблиц(категорий)
def show_list_category_db():
    with sqlite3.connect("DataBase/db_aura.db") as db:
        list_category = []
        cursor = db.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        result = cursor.fetchall()
        for name in result:
            list_category.append(name[0])
    return list_category


# Вывод всех проверенных клиента
def get_list_verify_users_db():
    with sqlite3.connect("DataBase/db_aura.db") as db:
        lst_verify_users = []
        cursor = db.cursor()
        cursor.execute(f"SELECT id_telegram FROM Проверенные_клиенты")
        for id_users in cursor.fetchall():
            lst_verify_users.append(id_users[0])
    return lst_verify_users


# Получить скоринг по id из базы
async def get_scoring_verify_users_db(id_telegram):
    with sqlite3.connect("DataBase/db_aura.db") as db:
        lst_verify_users = []
        cursor = db.cursor()
        cursor.execute(
            f"SELECT scoring FROM Проверенные_клиенты WHERE id_telegram = {id_telegram} "
        )
        for id_users in cursor.fetchall():
            lst_verify_users.append(id_users[0])
    return lst_verify_users[0]


# Получить дату рождения по id из базы
async def get_date_birth_verify_users_db(id_telegram):
    with sqlite3.connect("DataBase/db_aura.db") as db:
        lst_verify_users = []
        cursor = db.cursor()
        cursor.execute(
            f"SELECT date_birth FROM Проверенные_клиенты WHERE id_telegram = {id_telegram} "
        )
        for id_users in cursor.fetchall():
            lst_verify_users.append(id_users[0])
    return lst_verify_users[0]


# Получить ФИО по id из базы
async def get_fio_verify_users_db(id_telegram):
    with sqlite3.connect("DataBase/db_aura.db") as db:
        lst_verify_users = []
        cursor = db.cursor()
        cursor.execute(
            f"SELECT fio FROM Проверенные_клиенты WHERE id_telegram = {id_telegram} "
        )
        for id_users in cursor.fetchall():
            lst_verify_users.append(id_users[0])
    return lst_verify_users[0]


# Добавить проверенного клиента в базу
async def insert_data_to_verify_users_db(
    id_telegram, fio, date_verify, scoring, date_birth
):
    with sqlite3.connect("DataBase/db_aura.db") as db:
        cursor = db.cursor()
        cursor.execute(
            f"INSERT INTO Проверенные_клиенты (id_telegram, fio, date_verify, scoring, date_birth)"
            f" VALUES (?, ?, ?, ?, ?)",
            (id_telegram, fio, date_verify, scoring, date_birth),
        )
        db.commit()


# Возвращает список названий в базе
def get_lst_name_db():
    with sqlite3.connect("DataBase/db_aura.db") as db:
        list_category = []
        list_name_product = []
        cursor = db.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        result = cursor.fetchall()

        for name in result:
            list_category.append(name[0])

        for name_table in list_category:
            try:
                cursor.execute(f"SELECT name FROM {name_table}")
            except sqlite3.OperationalError:
                pass
            all_name = cursor.fetchall()
            for name_product in all_name:
                list_name_product.append(name_product[0])
    return list_name_product
