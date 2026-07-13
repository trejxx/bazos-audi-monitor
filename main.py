import requests
from bs4 import BeautifulSoup
import json
import os
import re


DISCORD_WEBHOOK = os.environ["DISCORD_WEBHOOK"]

BASE_URL = "https://auto.bazos.sk"

PAGES = [
    "https://auto.bazos.sk/inzeraty/audi-a4/",
    "https://auto.bazos.sk/inzeraty/audi-a4/2/",
    "https://auto.bazos.sk/inzeraty/audi-a4/3/",
    "https://auto.bazos.sk/inzeraty/audi-a4/4/",
    "https://auto.bazos.sk/inzeraty/audi-a4/5/",
]

MIN_YEAR = 2020
MAX_PRICE = 21000


def load_seen():
    try:
        with open("seen.json") as f:
            return json.load(f)
    except:
        return []


def save_seen(data):
    with open("seen.json", "w") as f:
        json.dump(data, f, indent=2)


def discord_send(data):

    requests.post(
        DISCORD_WEBHOOK,
        json={
            "embeds": [data]
        },
        timeout=20
    )


def get_detail(url):

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


    title = soup.find("h1")

    if title:
        title = title.text.strip()
    else:
        title = "Audi A4"


    price = None

    m = re.search(
        r"(\d[\d\s]*)\s?€",
        text
    )

    if m:
        price = m.group(1).replace(" ", "") + " €"


    year = None

    years = re.findall(
        r"\b20\d{2}\b",
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


    image = None

    img = soup.find("img")

    if img:
        image = img.get("src")


    return {
        "title": title,
        "price": price,
        "year": year,
        "km": km,
        "image": image
    }



def check():

    seen = load_seen()


    headers = {
        "User-Agent": "Mozilla/5.0"
    }


    for page in PAGES:

        r = requests.get(
            page,
            headers=headers,
            timeout=30
        )


        soup = BeautifulSoup(
            r.text,
            "html.parser"
        )


        for a in soup.find_all("a", href=True):

            href = a["href"]


            if "/inzerat/" not in href:
                continue


            if href in seen:
                continue


            if not href.startswith("http"):
                href = BASE_URL + href


            info = get_detail(href)


            year = info["year"]

            if year and int(year) < MIN_YEAR:
                continue


            price = info["price"]

            if price:
                price_num = int(
                    price.replace("€","").replace(" ","")
                )

                if price_num > MAX_PRICE:
                    continue


            title = info["title"].lower()


            rating = ""

            keywords = [
                "s line",
                "quattro",
                "matrix",
                "35 tfsi",
                "40 tfsi",
                "40 tdi"
            ]

            if any(x in title for x in keywords):
                rating = "🔥 TOP KUS"


            embed = {
                "title": f"🚗 {rating} Audi A4",
                "description": info["title"],
                "url": href,
                "fields": [
                    {
                        "name":"💶 Cena",
                        "value":info["price"] or "—",
                        "inline":True
                    },
                    {
                        "name":"📅 Rok",
                        "value":info["year"] or "—",
                        "inline":True
                    },
                    {
                        "name":"🛣️ KM",
                        "value":info["km"] or "—",
                        "inline":True
                    }
                ]
            }


            if info["image"]:
                embed["image"] = {
                    "url": info["image"]
                }


            discord_send(embed)


            seen.append(href)


    save_seen(seen)


if __name__ == "__main__":
    check()
