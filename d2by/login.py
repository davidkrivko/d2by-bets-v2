import requests
import datetime
import logging
import os

from config import USERNAME, PASSWORD, TELEGRAM_BOT, CHAT_ID

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from simplegmail.query import construct_query
from bs4 import BeautifulSoup


def send_telegram_message_sync(message):
    telegram_url = f"https://api.telegram.org/{TELEGRAM_BOT}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}

    resp = requests.post(telegram_url, data=data)

    return resp.status_code


def get_verification_code(time, gmail_client):
    current_time = datetime.datetime.now().strftime("%Y/%m/%d")

    is_new = True

    i = 0
    while is_new:
        i += 1

        query_params = {
            "unread": True,
            "sender": "noreply@d2by.com",
            "after": current_time
        }
        messages = gmail_client.get_messages(query=construct_query(query_params))
        if messages:
            message = messages[0]

            sent_at = datetime.datetime.fromisoformat(message.date)
            sent_at = sent_at.astimezone(datetime.timezone.utc).replace(tzinfo=None)
            if sent_at > time:
                is_new = False

        if i == 10:
            send_telegram_message_sync("Email is not coming!")
            return None

    html = message.html
    soup = BeautifulSoup(html, "html.parser")
    font_element = soup.find("font", {"color": "#ff9900", "size": "6"})
    verification_code = font_element.get_text()

    return str(verification_code)


def get_token(username, password, gmail_client):
    CHROME_OPTIONS = webdriver.ChromeOptions()
    CHROME_OPTIONS.add_argument("--window-size=1300,800")
    if os.environ.get("CHROME_OPTIONS") == "true":
        CHROME_OPTIONS.add_argument("--disable-gpu")
        CHROME_OPTIONS.add_argument("--headless")
        CHROME_OPTIONS.add_argument("--no-sandbox")
        CHROME_OPTIONS.add_argument("--disable-dev-shm-usage")

    logging.error("Start login")
    driver = webdriver.Chrome(options=CHROME_OPTIONS)
    driver.get("https://d2by.com/")

    wait = WebDriverWait(driver, 10)
    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".modal-select-items.d2by-deposit-withdraw")
        )
    )

    wait = WebDriverWait(driver, 10)
    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".bg-orange-ff9910.rounded.text-white.py-1.px-6.text-sm.cursor-pointer.font-arial")
        )
    )
    login_button = driver.find_element(
        By.CSS_SELECTOR,
        ".bg-orange-ff9910.rounded.text-white.py-1.px-6.text-sm.cursor-pointer.font-arial",
    )
    login_button.click()

    wait = WebDriverWait(driver, 10)
    wait.until(
        EC.presence_of_element_located(
            (By.NAME, "email")
        )
    )
    email_input = driver.find_element(By.NAME, "email")
    password_input = driver.find_element(By.NAME, "password")

    email_input.send_keys(username)
    password_input.send_keys(password)

    # Click the login button
    time = datetime.datetime.utcnow()

    login_button = driver.find_element(By.CSS_SELECTOR, ".button.to-yellow-f9b80e")
    login_button.click()

    ver_code = get_verification_code(time, gmail_client)
    if ver_code is None:
        return get_token(username, password, gmail_client)

    wait = WebDriverWait(driver, 20)
    wait.until(
        EC.presence_of_element_located(
            (By.NAME, "verifyCode")
        )
    )
    code_input = driver.find_element(By.NAME, "verifyCode")
    code_input.send_keys(ver_code)

    login_button.click()

    wait = WebDriverWait(driver, 10)
    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".font-bold.border-yellow-f99910")
        )
    )

    cookies = driver.get_cookies()

    logging.error("Get cookies")
    driver.close()
    for ck in cookies:
        if ck["name"] == "_cus_token":
            return {"name": ck["name"], "value": ck["value"]}


async def create_new_token(gmail_client):
    new_token = get_token(username=USERNAME, password=PASSWORD, gmail_client=gmail_client)
    global AUTH_TOKEN
    AUTH_TOKEN = new_token

    return AUTH_TOKEN
