import requests
from bs4 import BeautifulSoup
import json
import os
import re


DISCORD_WEBHOOK = os.environ["DISCORD_WEBHOOK"]

SEARCH_URL = "https://auto.bazos.sk/inzeraty/audi-a4/"

BASE_URL = "https://auto.bazos.sk"

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
        json.dump(data, f, indent=2)


def extract_price(text):

    prices = re.findall(
        r"(\d[\d\s]*)\s?€",
        text
    )

    if prices:
        try:
            return int(
                prices[0].replace(" ", "")
            )
        except:
            return None

    return None



def extract_year(text):

    years = re.findall(
        r"\b(20\d{2})\b",
        text
    )

    if years:
        return int(years[0])

    return None



def check():

    seen = load_seen()

    headers = {
        "User-Agent": "Mozilla/5.0"
    }


    response = requests.get(
        SEARCH_URL,
        headers=headers,
        timeout=30
    )


    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )


    new_ads = 0


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


        # ignorovanie dielov
        bad_words = [
            "svetlo",
            "disk",
            "koles",
            "nárazník",
            "sedačka",
            "volant",
            "radio",
            "diel"
        ]


        lower = title.lower()


        if any(
            word in lower
            for word in bad_words
        ):
            continue


        year = extract_year(title)
        price = extract_price(title)


        # ak sa dá vyčítať rok, kontrolujeme ho
        if year and year < MIN_YEAR:
            continue


        # ak sa dá vyčítať cena, kontrolujeme ju
        if price and price > MAX_PRICE:
            continue



        message = (
            "🚗 **Nová Audi A4!**\n\n"
            f"📌 {title}\n"
        )


        if year:
            message += f"📅 Rok: {year}\n"

        if price:
            message += f"💶 Cena: {price} €\n"


        message += (
            f"\n🔗 {full_link}"
        )


        send_discord(message)


        seen.append(link)
        new_ads += 1



    save_seen(seen)


    print(
        f"Hotovo. Nové vhodné Audi: {new_ads}"
    )



if __name__ == "__main__":
    check()
