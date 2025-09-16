from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from concurrent.futures import ProcessPoolExecutor
import asyncio


def idx_verify(lastname, firstname, midname, date_birth, seria_number, date_issue):
    try:
        s = Service(executable_path="ChromeDriver/chromedriver.exe")
        driver = webdriver.Chrome(service=s)

        # Авторизация
        driver.maximize_window()
        driver.get("https://online.iidx.ru/")
        time.sleep(1)

        email_input = driver.find_element(By.ID, "username")
        email_input.clear()
        email_input.send_keys("your_username")
        time.sleep(1)

        password_input = driver.find_element(By.ID, "password")
        password_input.clear()
        password_input.send_keys("your_password")
        time.sleep(1)

        # Переход на страницу проверки
        password_input.send_keys(Keys.ENTER)
        time.sleep(2)

        driver.find_element(By.CLASS_NAME, "jss217").click()
        time.sleep(2)

        driver.find_element(By.PARTIAL_LINK_TEXT, "Финансовый скоринг").click()
        time.sleep(2)

        # Ввод данных на проверку
        lastName = driver.find_element(By.ID, "lastName")
        lastName.send_keys(lastname)
        time.sleep(1)

        firstName = driver.find_element(By.ID, "firstName")
        firstName.send_keys(firstname)
        time.sleep(1)

        midName = driver.find_element(By.ID, "midName")
        midName.send_keys(midname)
        time.sleep(1)

        birthDate = driver.find_element(By.ID, "birthDate")
        birthDate.send_keys(date_birth)
        time.sleep(1)

        passport = driver.find_element(By.ID, "passport")
        passport.send_keys(seria_number)
        time.sleep(1)

        passportDate = driver.find_element(By.ID, "passportDate")
        passportDate.send_keys(date_issue)
        time.sleep(1)

        passportDate.send_keys(Keys.ENTER)
        time.sleep(5)

        data = driver.find_element(By.XPATH, "/html/body").text

        result = data.split("Результат")[2]
        result = result.replace("\n", "")
        result = result.split("описание")[0]

        return result

    except Exception as ex:
        print(ex)

    finally:
        driver.close()
        driver.quit()


async def pool_for_verify(
    lastname, firstname, midname, date_birth, seria_number, date_issue
):
    loop = asyncio.get_running_loop()
    with ProcessPoolExecutor() as pool:
        result = await loop.run_in_executor(
            pool,
            idx_verify,
            lastname,
            firstname,
            midname,
            date_birth,
            seria_number,
            date_issue,
        )
        return result
