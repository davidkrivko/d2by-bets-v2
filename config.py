import os
from dotenv import load_dotenv

load_dotenv()


DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASS")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")

D2BY_TIME_DELTA = int(os.environ.get("D2BY_TIME_DELTA", 0))
FAN_SPORT_DELTA = int(os.environ.get("FAN_SPORT_DELTA", 0))
SENDING_MESSAGES_DELTA = int(os.environ.get("SENDING_MESSAGES_DELTA", 0))

THRESHOLD = 60
WORD_BLACK_LIST = [
    "vfb",
    "vfl",
    "gaming",
    "esports",
    "ac",
    "fc",
    "esport",
    "team",
    "bitskins",
    "vincere",
    "challengers",
]


TELEGRAM_BOT = os.environ.get("TELEGRAM_BOT")
CHAT_ID = os.environ.get("CHAT_ID")

USERNAME = os.environ.get("LOGIN_USERNAME")
PASSWORD = os.environ.get("LOGIN_PASSWORD")

IS_ALL_MATCHES = bool(os.environ.get("IS_ALL_MATCHES", 0))

DEFAULT_D2BY_HEADERS = {
        "accept": "application/json",
        "content-type": "application/json",
        "origin": "https://d2by.com",
        "referer": "https://d2by.com/",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }

DEFAULT_FAN_HEADERS = {
        "accept": "application/json",
        "content-type": "application/json",
        "origin": "https://fan-sport.cc",
        "referer": "https://fan-sport.cc/",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }

DEFAULT_BETS4PRO_HEADERS = {
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

SECRET_KEY = os.environ.get('SECRET_KEY')
