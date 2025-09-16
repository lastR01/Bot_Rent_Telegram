import datetime


async def calc_pledge(description, scoring, check_code_in_scoring, count=1):

    if "Celeron" in description:

        if scoring < 500:
            pledge = 7500

        elif 550 > scoring > 500:
            pledge = 3000

        elif 600 > scoring > 550:
            pledge = 0

        elif 650 > scoring > 600:
            pledge = 0

        elif 700 > scoring > 650:
            pledge = 0

        elif 850 > scoring > 700:
            pledge = 0

        elif "код исключения: 3" in check_code_in_scoring:
            pledge = 7500

    if "i3" in description:
        if scoring < 500:
            pledge = 10000

        elif 550 > scoring > 500:
            pledge = 5000

        elif 600 > scoring > 550:
            pledge = 2500

        elif 650 > scoring > 600:
            pledge = 0

        elif 700 > scoring > 650:
            pledge = 0

        elif 850 > scoring > 700:
            pledge = 0

        elif "код исключения: 3" in check_code_in_scoring:
            pledge = 12500

    elif "i5" in description and "(Игровой)" not in description:
        if scoring < 500:
            pledge = 20000

        elif 550 > scoring > 500:
            pledge = 10000

        elif 600 > scoring > 550:
            pledge = 5000

        elif 650 > scoring > 600:
            pledge = 0

        elif 700 > scoring > 650:
            pledge = 0

        elif 850 > scoring > 700:
            pledge = 0

        elif "код исключения: 3" in check_code_in_scoring:
            pledge = 25000

    elif "i5 (Игровой)" in description:

        if scoring < 500:
            pledge = 30000

        elif 550 > scoring > 500:
            pledge = 15000

        elif 600 > scoring > 550:
            pledge = 7500

        elif 650 > scoring > 600:
            pledge = 3000

        elif 700 > scoring > 650:
            if count > 1:
                pledge = 3000

            else:
                pledge = 0

        elif 850 > scoring > 700:
            pledge = 0

        elif "код исключения: 3" in check_code_in_scoring:
            pledge = 37500

    elif "i7" in description and "(Игровой)" not in description:
        if scoring < 500:
            pledge = 32000

        elif 550 > scoring > 500:
            pledge = 16000

        elif 600 > scoring > 550:
            pledge = 8000

        elif 650 > scoring > 600:
            pledge = 5000

        elif 700 > scoring > 650:
            if count > 1:
                pledge = 5000

            else:
                pledge = 0

        elif 850 > scoring > 700:
            pledge = 0

        elif "код исключения: 3" in check_code_in_scoring:
            pledge = 40000

    elif "i7 (Игровой)" in description:
        if scoring < 500:
            pledge = 40000

        elif 550 > scoring > 500:
            pledge = 20000

        elif 600 > scoring > 550:
            pledge = 10000

        elif 650 > scoring > 600:
            pledge = 5000

        elif 700 > scoring > 650:
            if count > 1:
                pledge = 5000

            else:
                pledge = 0

        elif 850 > scoring > 700:
            pledge = 0

        elif "код исключения: 3" in check_code_in_scoring:
            pledge = 50000

    elif "MacBook" in description:

        if "12" in description or "13" in description or "14" in description:
            if scoring < 500:
                pledge = 30000

            elif 550 > scoring > 500:
                pledge = 15000

            elif 600 > scoring > 550:
                pledge = 7500

            elif 650 > scoring > 600:
                pledge = 5000

            elif 700 > scoring > 650:
                if count > 1:
                    pledge = 5000

                else:
                    pledge = 0

            elif 850 > scoring > 700:
                pledge = 0

            elif "код исключения: 3" in check_code_in_scoring:
                pledge = 37500

        else:
            if scoring < 500:
                pledge = 42000

            elif 550 > scoring > 500:
                pledge = 20000

            elif 600 > scoring > 550:
                pledge = 10000

            elif 650 > scoring > 600:
                pledge = 5000

            elif 700 > scoring > 650:
                if count > 1:
                    pledge = 5000

                else:
                    pledge = 0

            elif 850 > scoring > 700:
                pledge = 0

            elif "код исключения: 3" in check_code_in_scoring:
                pledge = 52000

    return count * pledge


async def calc_pledge_without_scoring(description, date_birth, count=1):
    date_birth = datetime.datetime.strptime(date_birth, "%d.%m.%Y").date()

    if "Celeron" in description:
        if date_birth.year > 2000:
            pledge = 3000

        elif date_birth.year < 2000:
            pledge = 0

    elif "i3" in description:
        if date_birth.year > 2000:
            pledge = 5000

        elif date_birth.year < 2000:
            pledge = 2500

    elif "i5" in description and "(Игровой)" not in description:
        if date_birth.year > 2000:
            pledge = 10000

        elif date_birth.year < 2000:
            pledge = 5000

    elif "i5 (Игровой)" in description:
        if date_birth.year > 2000:
            pledge = 15000

        elif date_birth.year < 2000:
            pledge = 7500

    elif "i7" in description and "(Игровой)" not in description:
        if date_birth.year > 2000:
            pledge = 16000

        elif date_birth.year < 2000:
            pledge = 8000

    elif "i7 (Игровой)" in description:
        if date_birth.year > 2000:
            pledge = 20000

        elif date_birth.year < 2000:
            pledge = 10000

    elif "MacBook" in description:

        if "12" in description or "13" in description or "14" in description:
            if date_birth.year > 2000:
                pledge = 15000

            elif date_birth.year < 2000:
                pledge = 7500

        else:
            if date_birth.year > 2000:
                pledge = 20000

            elif date_birth.year < 2000:
                pledge = 10000

    return count * pledge
