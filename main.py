import requests
from bs4 import BeautifulSoup
import json
import os
import time


DISCORD_WEBHOOK = os.environ["DISCORD_WEBHOOK"]

SEARCH_URL = "https://auto.bazos.sk/search.php?hledat=Audi+A4"


def load_seen():
    try:
        with open("seen.json", "r") as f:
            return json.load(f)
    except:
        return []


def save_seen(data):
    with open("seen.json", "w") as f:
        json.dump(data, f)


def send_discord(title, price, link):

    message = {
        "content":
        f"🚗 **Nový Audi A4 inzerát!**\n\n"
        f"**{title}**\n"
        f"💶 {price}\n"
        f"🔗 {link}"
    }

    requests.post(
        DISCORD_WEBHOOK,
        json=message
    )


def check_ads():

    seen = load_seen()

    headers = {
        "User-Agent":
        "Mozilla/5.0"
    }

    r = requests.get(
        SEARCH_URL,
        headers=headers
    )

    soup = BeautifulSoup(
        r.text,
        "html.parser"
    )


    ads = soup.find_all(
        "div",
        class_="inzerat"
    )


    for ad in ads:

        link = ad.find("a")

        if not link:
            continue

        url = link.get("href")

        if url in seen:
            continue


        title = link.text.strip()

        price = "Cena neuvedená"

        send_discord(
            title,
            price,
            url
        )


        seen.append(url)


    save_seen(seen)



while True:

    check_ads()

    time.sleep(
        600
    )
