import requests
from bs4 import BeautifulSoup
import os

URL = "https://visas-it.tlscontact.com/en-us/country/by/vac/byMSQ2it/news"

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def send(msg):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": msg}
    )

r = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
soup = BeautifulSoup(r.text, "html.parser")

title = soup.find("h2")

if title:
    title = title.text.strip()

    try:
        with open("last.txt") as f:
            last = f.read().strip()
    except:
        last = ""

    if title != last:
        send(f"🚨 Новая новость на TLSContact:\n\n{title}\n{URL}")

        with open("last.txt","w") as f:
            f.write(title)
