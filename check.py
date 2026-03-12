import os
import time
from telegram import Bot
from playwright.sync_api import sync_playwright

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
URL = "https://visas-it.tlscontact.com/en-us/country/by/vac/byMSQ2it/news"

bot = Bot(token=BOT_TOKEN)

def send(msg):
    bot.send_message(chat_id=CHAT_ID, text=msg)

def get_latest():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(URL)
        # Ждём полной загрузки
        page.wait_for_load_state("networkidle")
        # Получаем текст первого заголовка
        title = page.locator("h2").first.inner_text()
        browser.close()
        return title

try:
    latest = get_latest()
except Exception as e:
    send("❗ Ошибка загрузки: " + str(e))
    latest = None

try:
    with open("last.txt") as f:
        last = f.read().strip()
except FileNotFoundError:
    last = ""

if latest and latest != last:
    send(f"🚨 Новая новость:\n\n{latest}\n{URL}")
    with open("last.txt", "w") as f:
        f.write(latest)
