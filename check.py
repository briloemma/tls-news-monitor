import os
import asyncio
import aiohttp
from telegram import Bot

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

NEWS_URL = "https://cache-cms.directuscloud.tlscontact.com/items/news"
NEWS_URL = "https://cache-cms.directuscloud.tlscontact.com/items/news?limit=1000"
TRANSLATION_URL = "https://cache-cms.directuscloud.tlscontact.com/items/news_translations"

bot = Bot(token=BOT_TOKEN)
        n for n in data.get("data", [])
        if n.get("status") == "published"
        and n.get("tenant") == "visa-it"
        and any(t in ["byMSQ2it", "by*"] for t in n.get("tags", []))
    ]

    if not valid_news:
        raise ValueError("Нет актуальных новостей")

    # сортируем по дате
    valid_news.sort(key=lambda n: n.get("publish_date"), reverse=True)

    news = valid_news[0]

    news_id = str(news["id"])

    # ищем английский перевод
    title = None

    for tid in news.get("translations", []):

        translation = await fetch_json(
            session,
            f"{TRANSLATION_URL}/{tid}"
        )

        if translation["data"].get("languages_code") == "en-US":
            title = translation["data"]["title"]
            break

    # fallback если английского нет
    if not title:
        translation = await fetch_json(
            session,
            f"{TRANSLATION_URL}/{news['translations'][0]}"
        )
        title = translation["data"]["title"]

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
