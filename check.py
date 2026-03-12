import os
import requests
import asyncio
from telegram import Bot

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

bot = Bot(token=BOT_TOKEN)
NEWS_URL = "https://cache-cms.directuscloud.tlscontact.com/items/news"
TRANSLATION_URL = "https://cache-cms.directuscloud.tlscontact.com/items/news_translations"

async def send(msg):
    await bot.send_message(chat_id=CHAT_ID, text=msg)
    print("Telegram message sent!")

from datetime import datetime, timezone

def get_latest_news():
    r = requests.get(NEWS_URL)
    data = r.json()

    valid_news = [
        n for n in data.get("data", [])
        if n.get("status") == "published"
        and n.get("tenant") == "visa-it"
        and n.get("show_on_homepage") is True
        and any(t.startswith("by") for t in n.get("tags", []))  # проверка тегов
    ]

    if not valid_news:
        raise ValueError("Нет актуальных новостей")

    # сортируем по дате публикации
    valid_news.sort(key=lambda n: n.get("publish_date"), reverse=True)
    news = valid_news[0]

    news_id = str(news["id"])
    
    # находим перевод на английский
    title = None
    for translation_id in news["translations"]:
        r2 = requests.get(f"{TRANSLATION_URL}/{translation_id}")
        translation_data = r2.json()
        if translation_data["data"].get("languages_code") == "en-US":
            title = translation_data["data"]["title"]
            break
    if not title:  # если английский не найден, берем первый
        r2 = requests.get(f"{TRANSLATION_URL}/{news['translations'][0]}")
        title = r2.json()["data"]["title"]

    return news_id, title

async def main():
    try:
        latest_id, latest_title = get_latest_news()
    except Exception as e:
        await send(f"❗ Ошибка API: {e}")
        latest_id = None

    try:
        with open("last.txt") as f:
            last = f.read().strip()
    except FileNotFoundError:
        last = ""

    if latest_id and latest_id != last:
        await send(f"🚨 Новая новость TLSContact:\n\n{latest_title}")
        with open("last.txt", "w") as f:
            f.write(latest_id)

# asyncio.run безопасно создаёт loop
asyncio.run(main())
