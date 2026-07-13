import requests
from bs4 import BeautifulSoup
import json
import os


DISCORD_WEBHOOK = os.environ["DISCORD_WEBHOOK"]

SEARCH_URL = "https://auto.bazos.sk/inzeraty/audi-a4/"

BASE_URL = "https://auto.bazos.sk"


def send_discord(message):
    requests.post(
        DISCORD_WEBHOOK,
        json={
            "content": message
        },
        timeout=20
    )


def load_seen():
    try:
        with open("seen.json", "r") as f:
            return json.load(f)
    except:
        return []


def save_seen(data):
    with open("seen.json", "w") as f:
        json.dump(data, f)


def check():

    seen = load_seen()
    new_ads = 0

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        SEARCH_URL,
        headers=headers,
        timeout=30
    )

    print("Status:", response.status_code)

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )


    for a in soup.find_all("a", href=True):

        link = a["href"]
        title = a.text.strip()


        if "/inzerat/" not in link:
            continue


        if link in seen:
            continue


        full_link = link

        if not link.startswith("http"):
            full_link = BASE_URL + link


        message = (
            "🚗 **Nová Audi A4 na Bazoši!**\n\n"
            f"**{title}**\n\n"
            f"🔗 {full_link}"
        )


        send_discord(message)

        seen.append(link)
        new_ads += 1


    save_seen(seen)


    print(
        f"Hotovo. Nové inzeráty: {new_ads}"
    )


if __name__ == "__main__":
    check()
