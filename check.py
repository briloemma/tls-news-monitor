import os
import asyncio
import aiohttp
from telegram import Bot

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

NEWS_URL = "https://cache-cms.directuscloud.tlscontact.com/items/news?limit=1000&sort=-publish_date"
TRANSLATION_URL = "https://cache-cms.directuscloud.tlscontact.com/items/news_translations"
TAGS_URL = "https://cache-cms.directuscloud.tlscontact.com/items/tags"

bot = Bot(token=BOT_TOKEN)


async def send(msg):
    await bot.send_message(chat_id=CHAT_ID, text=msg)
    print("Telegram message sent!")


async def fetch_json(session, url):
    async with session.get(url) as r:
        return await r.json()


async def get_tags(session):
    data = await fetch_json(session, TAGS_URL)
    return {t["id"]: t["slug"] for t in data.get("data", [])}


async def get_latest_news(session):

    tags_map = await get_tags(session)
    data = await fetch_json(session, NEWS_URL)

    valid_news = []

for n in data.get("data", []):

    if not (
        n.get("status") == "published"
        and n.get("tenant") == "visa-it"
        and n.get("show_on_homepage")
    ):
        continue

    tag_slugs = [tags_map.get(t) for t in n.get("tags", [])]

    if any(s and s.startswith("by") for s in tag_slugs):
        valid_news.append(n)
        
    if not valid_news:
        raise ValueError("Нет актуальных новостей")

    news = valid_news[0]
    news_id = str(news["id"])

    title = None

    for tid in news.get("translations", []):

        translation = await fetch_json(
            session,
            f"{TRANSLATION_URL}/{tid}"
        )

        if translation["data"].get("languages_code") == "en-US":
            title = translation["data"]["title"]
            break

    if not title and news.get("translations"):
        translation = await fetch_json(
            session,
            f"{TRANSLATION_URL}/{news['translations'][0]}"
        )
        title = translation["data"]["title"]

    if not title:
        title = "New TLSContact update"

    return news_id, title


async def main():

    async with aiohttp.ClientSession() as session:

        try:
            latest_id, latest_title = await get_latest_news(session)
        except Exception as e:
            await send(f"❗ Ошибка API: {e}")
            return

        try:
            with open("last.txt") as f:
                last = f.read().strip()
        except FileNotFoundError:
            last = ""

        if latest_id != last:

            await send(
                f"🚨 Новая новость TLSContact:\n\n{latest_title}\n\n"
                f"https://visas-it.tlscontact.com/en-us/country/by/vac/byMSQ2it/news/{latest_id}"
            )

            with open("last.txt", "w") as f:
                f.write(latest_id)


if __name__ == "__main__":
    asyncio.run(main())
