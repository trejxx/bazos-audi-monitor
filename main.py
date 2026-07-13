import requests
from bs4 import BeautifulSoup
import json
import os
import re


DISCORD_WEBHOOK = os.environ["DISCORD_WEBHOOK"]


SEARCH_URLS = [
    "https://auto.bazos.sk/search.php?hledat=Audi+A4",
    "https://auto.bazos.sk/search.php?hledat=A4+B9",
    "https://auto.bazos.sk/search.php?hledat=Audi+A4+Avant",
]


MAX_PRICE = 21000
MIN_YEAR = 2020


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


def extract_price(text):

    numbers = re.findall(
        r'\d[\d\s]*€',
        text
    )

    if numbers:
        value = numbers[0]
        value = value.replace("€","")
        value = value.replace(" ","")

        try:
            return int(value)
        except:
            pass

    return None



def check():

    seen = load_seen()
    new_ads = 0


    headers = {
        "User-Agent": "Mozilla/5.0"
    }


    for url in SEARCH_URLS:

        html = requests.get(
            url,
            headers=headers,
            timeout=30
        ).text


        soup = BeautifulSoup(
            html,
            "html.parser"
        )


        for a in soup.find_all("a", href=True):

            link = a["href"]
            title = a.text.strip()


            if "inzerat" not in link:
                continue


            if link in seen:
                continue


            text = title.lower()


            # musí byť Audi A4
            if "a4" not in text:
                continue


            # vyhodí diely
            bad = [
                "svetlo",
                "disk",
                "koles",
                "nárazník",
                "diel",
                "radio",
                "volant"
            ]

            if any(x in text for x in bad):
                continue



            message = (
                "🚗 **NOVÁ Audi A4 2020+**\n\n"
                f"**{title}**\n\n"
                f"🔗 {link}"
            )


            send_discord(message)

            seen.append(link)
            new_ads += 1


    save_seen(seen)

    print(
        f"Hotovo. Nové autá: {new_ads}"
    )


if __name__ == "__main__":
    check()
