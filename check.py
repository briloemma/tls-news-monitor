import os
from telegram import Bot
from playwright.sync_api import sync_playwright

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
URL = "https://visas-it.tlscontact.com/en-us/country/by/vac/byMSQ2it/news"

bot = Bot(token=BOT_TOKEN)

send("✅ Тест: мониторинг TLS работает")

def send(msg):
    bot.send_message(chat_id=CHAT_ID, text=msg)

def get_latest_news():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(URL)
        page.wait_for_load_state("networkidle")  # ждём загрузки JS и контента
        # Берём первый заголовок новости
        title_element = page.locator("h2").first
        title = title_element.inner_text().strip() if title_element else None
        browser.close()
        return title

try:
    latest = get_latest_news()
except Exception as e:
    send(f"❗ Ошибка загрузки страницы: {e}")
    latest = None

# Проверяем, есть ли изменения
try:
    with open("last.txt") as f:
        last = f.read().strip()
except FileNotFoundError:
    last = ""

if latest and latest != last:
    send(f"🚨 Новая новость на TLSContact:\n\n{latest}\n{URL}")
    with open("last.txt", "w") as f:
        f.write(latest)
