import os
from telnetlib import EC

from selenium import webdriver
from selenium.webdriver.common.by import By

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


CHROME_OPTIONS = webdriver.ChromeOptions()


CHROME_OPTIONS.add_argument("--window-size=1300,800")
if os.environ.get("CHROME_OPTIONS") == "true":
    CHROME_OPTIONS.add_argument("--disable-gpu")
    CHROME_OPTIONS.add_argument("--headless")
    CHROME_OPTIONS.add_argument("--no-sandbox")
    CHROME_OPTIONS.add_argument("--disable-dev-shm-usage")


headers = {
    "cookie": "lang=en; _ym_uid=1698496197361582594; _ym_d=1698496197; _gcl_au=1.1.2103616613.1698496197; _ga=GA1.1.1692695333.1698496197; _fbp=fb.1.1698496197487.1957987306; overwatch=true; hs=true; soccer=true; dota2=true; PHPSESSID=co0tp0rn0o2sn41if7va91dr24; _ym_isad=2; cf_clearance=bBd_ujiRye4KITmr23U27_ki08M77MmDuz9IuNu7leE-1704307437-0-2-c1af11bd.ae1faf2b.e28cf9c4-0.2.1704307437; cs_go=true; basketball=false; hockey=true; lol=true; sc=true; valorant=true; other=true; _ga_S9E0G3W1VY=GS1.1.1704307434.5.1.1704308876.0.0.0",
    "authority": "bets4.net",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "referer": "https://bets4.net/express-bets/",
    "sec-ch-ua": "^\^Not_A",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "^\^Windows^^",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


def login(username, password):
    driver = webdriver.Chrome()
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
    username_input.send_keys("shashka_sidr")
    password_input.send_keys("HfpHwp20qkx.Pq!K")

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


if __name__ == "__main__":
    login("a", "b")
