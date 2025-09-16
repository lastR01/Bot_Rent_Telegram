from amocrm.v2 import tokens, Lead as _Lead, custom_field
from datetime import datetime


class Lead(_Lead):
    responsible_manager = custom_field.TextCustomField("ОБРАБОТАЛ ЗАЯВКУ-БРОНЬ")
    fio_client = custom_field.TextCustomField("ФИО КЛИЕНТА")
    category_product = custom_field.TextCustomField("НАПРАВЛЕНИЕ")
    type_operation = custom_field.TextCustomField("ТИП ОПЕРАЦИИ")
    type_area = custom_field.TextCustomField("ИНТЕРНЕТ ПЛОЩАДКА")
    technique = custom_field.TextCustomField("ТОЧНАЯ ЕДИНИЦА ОБОРУДОВАНИЯ")
    additional = custom_field.TextCustomField("ДОП ОБОРУДОВАНИЕ")
    start_rent = custom_field.TextCustomField("НАЧАЛО АРЕНДЫ")
    end_rent = custom_field.TextCustomField("ЗАВЕРШЕНИЕ АРЕНДЫ")
    off_bots = custom_field.TextCustomField("ОТКЛЮЧИТЬ БОТОВ")
    pledge = custom_field.TextCustomField("ЗАЛОГ")
    where_pledge = custom_field.TextCustomField("ГДЕ ЗАЛОГ?")
    scoring = custom_field.TextCustomField("СКОРИНГ")
    who_gave_product = custom_field.TextCustomField("КТО ВЫДАЛ ОБОРУД.")
    who_accepted_product = custom_field.TextCustomField("Кто ПРИНЯЛ технику")
    responsible_for_money = custom_field.TextCustomField("ОТВЕТВСТЕННЫЙ ЗА ДЕНЬГИ")
    option_payment = custom_field.TextCustomField("ВАРИАНТ ОПЛАТЫ")
    hand_deal = custom_field.TextCustomField("РУЧНАЯ СДЕЛКА")


tokens.default_token_manager(
    client_id="your_client_id",
    client_secret="your_client_secret",
    subdomain="your_subdomain",
    redirect_url="https://ya.ru",
    storage=tokens.FileTokensStorage(),
)


async def create_new_lead_func(lst_data):
    new_lead = Lead.objects.create()

    new_lead.name = lst_data[0]
    new_lead.save()

    new_lead.price = lst_data[1]
    new_lead.save()

    new_lead.responsible_manager = "Родион Л"
    data_lead = new_lead._data["custom_fields_values"]
    for c in data_lead:
        if "field_code" in c:
            del c["field_code"]
        if "values" in c:
            for v in c["values"]:
                if "enum_code" in v:
                    del v["enum_code"]
    new_lead.save()

    new_lead.fio_client = lst_data[2]
    data_lead = new_lead._data["custom_fields_values"]
    for c in data_lead:
        if "field_code" in c:
            del c["field_code"]
        if "values" in c:
            for v in c["values"]:
                if "enum_code" in v:
                    del v["enum_code"]
    new_lead.save()

    new_lead.category_product = "НОУТБУКИ"
    data_lead = new_lead._data["custom_fields_values"]
    for c in data_lead:
        if "field_code" in c:
            del c["field_code"]
        if "values" in c:
            for v in c["values"]:
                if "enum_code" in v:
                    del v["enum_code"]
    new_lead.save()

    new_lead.type_operation = "АРЕНДА"
    data_lead = new_lead._data["custom_fields_values"]
    for c in data_lead:
        if "field_code" in c:
            del c["field_code"]
        if "values" in c:
            for v in c["values"]:
                if "enum_code" in v:
                    del v["enum_code"]
    new_lead.save()

    new_lead.type_area = "TELEGRAM"
    data_lead = new_lead._data["custom_fields_values"]
    for c in data_lead:
        if "field_code" in c:
            del c["field_code"]
        if "values" in c:
            for v in c["values"]:
                if "enum_code" in v:
                    del v["enum_code"]
    new_lead.save()

    # new_lead.technique = lst_data[3]
    # new_lead.technique = '1.04 HP (Celeron, 8gb, ssd, 15,6),CND449C7N5!'
    # data_lead = new_lead._data['custom_fields_values']
    # for c in data_lead:
    #     if 'field_code' in c:
    #         del c['field_code']
    #     if 'values' in c:
    #         for v in c['values']:
    #             if 'enum_code' in v:
    #                 del v['enum_code']
    # new_lead.save()

    new_lead.additional = "ОТСУТСТВУЕТ"
    data_lead = new_lead._data["custom_fields_values"]
    for c in data_lead:
        if "field_code" in c:
            del c["field_code"]
        if "values" in c:
            for v in c["values"]:
                if "enum_code" in v:
                    del v["enum_code"]
    new_lead.save()

    first_date = datetime.combine(lst_data[4], datetime.min.time()).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    new_lead.start_rent = first_date
    data_lead = new_lead._data["custom_fields_values"]
    for c in data_lead:
        if "field_code" in c:
            del c["field_code"]
        if "values" in c:
            for v in c["values"]:
                if "enum_code" in v:
                    del v["enum_code"]
    new_lead.save()

    last_date = datetime.combine(lst_data[5], datetime.min.time()).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    new_lead.end_rent = last_date
    data_lead = new_lead._data["custom_fields_values"]
    for c in data_lead:
        if "field_code" in c:
            del c["field_code"]
        if "values" in c:
            for v in c["values"]:
                if "enum_code" in v:
                    del v["enum_code"]
    new_lead.save()

    new_lead.off_bots = "ДА"
    data_lead = new_lead._data["custom_fields_values"]
    for c in data_lead:
        if "field_code" in c:
            del c["field_code"]
        if "values" in c:
            for v in c["values"]:
                if "enum_code" in v:
                    del v["enum_code"]
    new_lead.save()

    new_lead.pledge = lst_data[6]
    data_lead = new_lead._data["custom_fields_values"]
    for c in data_lead:
        if "field_code" in c:
            del c["field_code"]
        if "values" in c:
            for v in c["values"]:
                if "enum_code" in v:
                    del v["enum_code"]
    new_lead.save()

    new_lead.where_pledge = "ВИТ"
    data_lead = new_lead._data["custom_fields_values"]
    for c in data_lead:
        if "field_code" in c:
            del c["field_code"]
        if "values" in c:
            for v in c["values"]:
                if "enum_code" in v:
                    del v["enum_code"]
    new_lead.save()

    new_lead.scoring = lst_data[7]
    data_lead = new_lead._data["custom_fields_values"]
    for c in data_lead:
        if "field_code" in c:
            del c["field_code"]
        if "values" in c:
            for v in c["values"]:
                if "enum_code" in v:
                    del v["enum_code"]
    new_lead.save()

    new_lead.responsible_for_money = "Вит"
    data_lead = new_lead._data["custom_fields_values"]
    for c in data_lead:
        if "field_code" in c:
            del c["field_code"]
        if "values" in c:
            for v in c["values"]:
                if "enum_code" in v:
                    del v["enum_code"]
    new_lead.save()

    new_lead.option_payment = "Юкасса"
    data_lead = new_lead._data["custom_fields_values"]
    for c in data_lead:
        if "field_code" in c:
            del c["field_code"]
        if "values" in c:
            for v in c["values"]:
                if "enum_code" in v:
                    del v["enum_code"]
    new_lead.save()

    new_lead.hand_deal = "НЕТ"
    data_lead = new_lead._data["custom_fields_values"]
    for c in data_lead:
        if "field_code" in c:
            del c["field_code"]
        if "values" in c:
            for v in c["values"]:
                if "enum_code" in v:
                    del v["enum_code"]
    new_lead.save()

    return new_lead.id
