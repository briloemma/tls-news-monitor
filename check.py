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
    today = datetime.now(timezone.utc)

    valid_news = [
        n for n in data.get("data", [])
        if n.get("status") == "published"
        and "by*" in n.get("tags", [])
        #and n.get("show_on_homepage") is True
        #and n.get("tenant") == "visas-it"
        #and n.get("publish_date") <= today.isoformat()
    ]

    if not valid_news:
        raise ValueError("Нет актуальных новостей")

    # сортируем по дате публикации или sort
    valid_news.sort(key=lambda n: n.get("publish_date"), reverse=True)
    news = valid_news[0]

    news_id = str(news["id"])
    translation_id = news["translations"][0]

    r2 = requests.get(f"{TRANSLATION_URL}/{translation_id}")
    translation_data = r2.json()
    title = translation_data["data"]["title"]

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
