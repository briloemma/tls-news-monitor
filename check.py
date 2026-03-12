import os
import asyncio
from telegram import Bot
from playwright.sync_api import sync_playwright

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
URL = "https://visas-it.tlscontact.com/en-us/country/by/vac/byMSQ2it/news"

bot = Bot(token=BOT_TOKEN)

# --- Функция отправки сообщений ---
async def send(msg):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=msg)
        print("Telegram message sent!")
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

# --- Вспомогательная функция для запуска async в любом loop ---
def send_sync(msg):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    if loop.is_running():
        # если loop уже работает (на GitHub Actions), запускаем через create_task
        asyncio.ensure_future(send(msg))
    else:
        loop.run_until_complete(send(msg))

# --- ТЕСТОВОЕ УВЕДОМЛЕНИЕ ---
send_sync("✅ Тест: мониторинг TLS работает")

# --- Функция получения последнего заголовка новости ---
def get_latest_news():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()
        page.goto(URL)
        page.wait_for_load_state("networkidle")
        title_element = page.locator("h2").first
        title = title_element.inner_text().strip() if title_element else None
        browser.close()
        return title

# --- Основная логика проверки новости ---
try:
    latest = get_latest_news()
except Exception as e:
    send_sync(f"❗ Ошибка загрузки страницы: {e}")
    latest = None

# --- Сравнение с предыдущей новостью ---
try:
    with open("last.txt") as f:
        last = f.read().strip()
except FileNotFoundError:
    last = ""

if latest and latest != last:
    send_sync(f"🚨 Новая новость на TLSContact:\n\n{latest}\n{URL}")
    with open("last.txt", "w") as f:
        f.write(latest)
