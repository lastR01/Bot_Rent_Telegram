import os
from docxtpl import DocxTemplate
from docx2pdf import convert
from datetime import datetime
import num2words


def product_price_func(description):

    if "Celeron" in description:
        evaluative_price = 15000
        return evaluative_price

    elif "i3" in description:
        evaluative_price = 20000
        return evaluative_price

    elif "i5" in description and "(Игровой)" not in description:
        evaluative_price = 30000
        return evaluative_price

    elif "i5 (Игровой)" in description:
        evaluative_price = 40000
        return evaluative_price

    elif "i7" in description and "(Игровой)" not in description:
        evaluative_price = 45000
        return evaluative_price

    elif "i7 (Игровой)" in description:
        evaluative_price = 50000
        return evaluative_price
    elif "MacBook" in description:

        if "12" in description or "13" in description or "14" in description:
            evaluative_price = 30000

        else:
            evaluative_price = 40000

        return evaluative_price


def find_info_in_order(data, name_info):
    data_line = data.splitlines()
    for name in data_line:
        if name_info in name:
            return name


async def insert_data_to_act_func(act_number, fio, order_info):
    doc = DocxTemplate("Шаблон Акта и Договора/Акт.docx")
    name_product = order_info.splitlines()[0]
    evaluative_price = product_price_func(name_product)

    price_order = int(
        find_info_in_order(order_info, "Стоимость аренды на выбранные даты:").split(
            ": "
        )[1]
    )
    pledge = find_info_in_order(order_info, "Залог:").split(": ")[1]

    if "Количество:" not in order_info:
        count = 1

    else:
        count = int(find_info_in_order(order_info, "Количество:").split(": ")[1])

    number = find_info_in_order(order_info, "Номер телефона: ").split(": ")[1]
    if "-" in number or " " in number:
        number = str(number).replace(" ", "").replace("-", "")
    if "+7" in number:
        number = str(number)[2:].replace(" ", "").replace("-", "")

    if len(number) == 11:
        number = number[1:]
    number = f"Номер тел.: +7 (  {number[:3]}  )  {number[3:6]} -  {number[6:8]}  -  {number[8:10]}    "

    start_rent = find_info_in_order(order_info, "Начало аренды:").split(": ")[1]
    start_rent = datetime.strptime(start_rent.replace(".", ""), "%d%m%Y").date()

    end_rent = find_info_in_order(order_info, "Конец аренды:").split(": ")[1]
    end_rent = datetime.strptime(end_rent.replace(".", ""), "%d%m%Y").date()

    date = end_rent - start_rent
    diff_date = int(date.days)
    if diff_date == 0:
        diff_date = 1

    words_price_order = str(num2words.num2words(number=price_order, lang="ru"))
    words_price_order = (
        words_price_order[0].upper() + words_price_order[1:] + " рублей(я) 00 копеек"
    )

    words_pledge = str(num2words.num2words(number=pledge, lang="ru"))
    words_pledge = words_pledge[0].upper() + words_pledge[1:] + " рублей(я) 00 копеек"

    count_charger = f"Зарядное устройство - {count} шт."
    count_mouse = f"Мышь USB проводная - {count} шт."
    count_bag = f"Сумка для ноутбука - {count} шт."

    bag = count * 500
    charger = count * 2500
    mouse = count * 500

    context = {
        "number_act": act_number,
        "start_rent": start_rent.strftime("%d.%m.%Y"),
        "end_rent": end_rent.strftime("%d.%m.%Y"),
        "diff_date": diff_date,
        "count_charger": count_charger,
        "count_mouse": count_mouse,
        "count_bag": count_bag,
        "name_product": name_product,
        "charger": charger,
        "mouse": mouse,
        "bag": bag,
        "product_price": evaluative_price,
        "price_order": price_order,
        "pledge": pledge,
        "status_product": "\u0332".join(" Исправном "),
        "status_product_2": "\u0332".join(" Нет "),
        "number": number,
        "words_price_order": words_price_order,
        "words_pledge": words_pledge,
        "fio": "\u0332".join(f" {fio}/                      "),
    }

    doc.render(context)
    contract_path = f"All_Acts/Акт_{act_number}.docx"
    doc.save(contract_path)

    pdf_path = f"All_Acts/Акт_{act_number}.pdf"
    convert(contract_path, pdf_path)
    os.remove(contract_path)

    return pdf_path


async def create_contract(client_id, split_data):
    doc = DocxTemplate("Шаблон Акта и Договора/Договор аренды.docx")

    context = {
        "number_contract": "\u0332".join(f"{client_id} "),
        "date": "\u0332".join(f'{datetime.today().date().strftime("%d.%m.%Y")} '),
        "fio": "\u0332".join(f"{split_data[0]} "),
        "date_birth": "\u0332".join(f"{split_data[1]} "),
        "passport_serial": "\u0332".join(f'{split_data[2].split(" ")[0]} '),
        "passport_number": "\u0332".join(f'{split_data[2].split(" ")[1]} '),
        "date_issue": "\u0332".join(f"{split_data[3]} "),
        "department_code": "\u0332".join(f"{split_data[4]} "),
        "who_gave": "\u0332".join(f"{split_data[5]} "),
        "registr_address": "\u0332".join(f"{split_data[6]} "),
        "residence_address": "\u0332".join(f"{split_data[7]} "),
        "number": "\u0332".join("                 "),
    }

    doc.render(context)
    contract_path = f"All_Contracts/Договор_{client_id}.docx"
    doc.save(contract_path)

    pdf_path = f"All_Contracts/Договор_{client_id}.pdf"
    convert(contract_path, pdf_path)
    os.remove(contract_path)

    return pdf_path
