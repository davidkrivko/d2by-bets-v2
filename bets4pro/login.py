import os

from telnetlib import EC

from selenium import webdriver
from selenium.webdriver.common.by import By

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import DEFAULT_BETS4PRO_HEADERS, BETS4PRO_USERNAME, BETS4PRO_PASSWORD

CHROME_OPTIONS = webdriver.ChromeOptions()

CHROME_OPTIONS.add_argument("--window-size=1300,800")
if os.environ.get("CHROME_OPTIONS") == "true":
    CHROME_OPTIONS.add_argument("--disable-gpu")
    CHROME_OPTIONS.add_argument("--headless")
    CHROME_OPTIONS.add_argument("--no-sandbox")
    CHROME_OPTIONS.add_argument("--disable-dev-shm-usage")


def login():
    driver = webdriver.Chrome(options=CHROME_OPTIONS)
    driver.get("https://bets4.org")

    wait = WebDriverWait(driver, 10)
    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "button.button_for_js_in_div.white_button.login")
        )
    )
    login_button = driver.find_element(
        By.CSS_SELECTOR,
        "button.button_for_js_in_div.white_button.login",
    )
    login_button.click()

    wait = WebDriverWait(driver, 10)
    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "button.steam.white_button")
        )
    )
    steam_button = driver.find_element(
        By.CSS_SELECTOR,
        "button.steam.white_button",
    )
    steam_button.click()

    cookie_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div#acceptAllButton")))
    cookie_button.click()

    username_input = driver.find_element(By.CSS_SELECTOR, "input[type='text']")
    password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")

    # Find the submit button
    submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

    # Input your username and password
    username_input.send_keys(BETS4PRO_USERNAME)
    password_input.send_keys(BETS4PRO_PASSWORD)

    # Click the submit button
    submit_button.click()

    wait = WebDriverWait(driver, 120)
    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input.btn_green_white_innerfade")
        )
    )
    steam_login_button = driver.find_element(By.CSS_SELECTOR, "input.btn_green_white_innerfade")
    steam_login_button.click()

    cookies = driver.get_cookies()

    token = None
    for cookie in cookies:
        if cookie["name"] == "PHPSESSID":
            token = cookie["value"]

    print("Bets4PRO login success")
    DEFAULT_BETS4PRO_HEADERS.update({"cookie": f"PHPSESSID={token}; lang=ru;"})

    return DEFAULT_BETS4PRO_HEADERS


def create_new_token():
    new_token = login()
    DEFAULT_BETS4PRO_HEADERS.update(new_token)

    return DEFAULT_BETS4PRO_HEADERS
