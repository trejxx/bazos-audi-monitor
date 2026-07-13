import requests
from bs4 import BeautifulSoup
import json
import os
import re


DISCORD_WEBHOOK = os.environ["DISCORD_WEBHOOK"]

SEARCH_URLS = [
    "https://auto.bazos.sk/inzeraty/audi-a4/"
]

BASE_URL = "https://auto.bazos.sk"


def load_seen():
    try:
        with open("seen.json", "r") as f:
            return json.load(f)
    except:
        return []


def save_seen(data):
    with open("seen.json", "w") as f:
        json.dump(data, f, indent=2)


def send_discord(title, price, year, km, location, image, link):

    embed = {
        "title": "🚗 Nová Audi A4",
        "description": title,
        "url": link,
        "fields": [
            {
                "name": "💶 Cena",
                "value": price or "Neuvedená",
                "inline": True
            },
            {
                "name": "📅 Rok",
                "value": year or "Neuvedený",
                "inline": True
            },
            {
                "name": "🛣️ KM",
                "value": km or "Neuvedené",
                "inline": True
            },
            {
                "name": "📍 Lokalita",
                "value": location or "Neuvedená",
                "inline": True
            }
        ],
        "footer": {
            "text": "Audi A4 Bazoš Monitor"
        }
    }

    if image:
        embed["image"] = {
            "url": image
        }

    requests.post(
        DISCORD_WEBHOOK,
        json={
            "embeds": [embed]
        },
        timeout=20
    )


def parse_detail(url):

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    soup = BeautifulSoup(
        r.text,
        "html.parser"
    )


    text = soup.get_text(
        " ",
        strip=True
    )


    title = ""

    h1 = soup.find("h1")

    if h1:
        title = h1.text.strip()


    price = None

    price_match = re.search(
        r"(\d[\d\s]*)\s?€",
        text
    )

    if price_match:
        price = price_match.group(1) + " €"


    year = None

    years = re.findall(
        r"\b(20\d{2})\b",
        text
    )

    if years:
        year = years[0]


    km = None

    km_match = re.search(
        r"(\d[\d\s]*)\s?km",
        text.lower()
    )

    if km_match:
        km = km_match.group(1) + " km"


    location = None

    for word in [
        "Bratislava",
        "Trenčín",
        "Žilina",
        "Košice",
        "Nitra",
        "Prešov"
    ]:
        if word in text:
            location = word
            break


    image = None

    img = soup.find("img")

    if img:
        image = img.get("src")


    return (
        title,
        price,
        year,
        km,
        location,
        image
    )


def check():

    seen = load_seen()

    headers = {
        "User-Agent": "Mozilla/5.0"
    }


    for search in SEARCH_URLS:

        r = requests.get(
            search,
            headers=headers,
            timeout=30
        )


        soup = BeautifulSoup(
            r.text,
            "html.parser"
        )


        for a in soup.find_all(
            "a",
            href=True
        ):

            href = a["href"]


            if "/inzerat/" not in href:
                continue


            if href in seen:
                continue


            if not href.startswith("http"):
                href = BASE_URL + href


            title = a.text.lower()


            if "a4" not in title:
                continue


            data = parse_detail(href)


            send_discord(
                data[0],
                data[1],
                data[2],
                data[3],
                data[4],
                data[5],
                href
            )


            seen.append(href)



    save_seen(seen)


if __name__ == "__main__":
    check()
