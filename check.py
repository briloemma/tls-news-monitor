import os
import requests
import asyncio
from telegram import Bot

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

bot = Bot(token=BOT_TOKEN)
URL = "https://cache-cms.directuscloud.tlscontact.com/items/news"

async def send(msg):
    await bot.send_message(chat_id=CHAT_ID, text=msg)
    print("Telegram message sent!")

def get_latest_news():
    r = requests.get(URL)
    data = r.json()
    news = data["data"][0]
    return str(news["id"]), news["title"]

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
