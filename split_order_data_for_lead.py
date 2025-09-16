from datetime import datetime


def find_info_in_order(data, name_info):
    data_line = data.splitlines()
    for name in data_line:
        if name_info in name:
            return name


# Разделить данные заказа для создания лида и акта
async def split_func(order_info):
    lst_data = []
    data = order_info.splitlines()
    number = find_info_in_order(order_info, "Номер телефона:")
    name_and_number = f"{data[0]}. {number}"
    price = find_info_in_order(order_info, "Всего к оплате:").split(": ")[1]
    fio = find_info_in_order(order_info, "ФИО:").split(": ")[1]
    pledge = find_info_in_order(order_info, "Залог:").split(": ")[1]
    scoring = find_info_in_order(order_info, "Скоринг:").split(": ")[1]

    start_rent = find_info_in_order(order_info, "Начало аренды:").split(": ")[1]
    start_rent = datetime.strptime(start_rent.replace(".", ""), "%d%m%Y").date()

    end_rent = find_info_in_order(order_info, "Конец аренды:").split(": ")[1]
    end_rent = datetime.strptime(end_rent.replace(".", ""), "%d%m%Y").date()

    name_product = data[0]

    lst_data.extend(
        [
            name_and_number,
            int(price),
            fio,
            name_product,
            start_rent,
            end_rent,
            pledge,
            scoring,
        ]
    )
    return lst_data
