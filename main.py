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


def send_discord(embed):
    requests.post(
        DISCORD_WEBHOOK,
        json={
            "embeds": [embed]
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


    # názov
    h1 = soup.find("h1")

    title = h1.text.strip() if h1 else ""


    # fotka cez og:image
    image = None

    og = soup.find(
        "meta",
        property="og:image"
    )

    if og:
        image = og.get("content")


    price = None

    p = re.search(
        r"(\d[\d\s]*)\s?€",
        text
    )

    if p:
        price = p.group(1).replace(" ","") + " €"


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


            if not href.startswith("http"):
                href = BASE_URL + href


            if href in seen:
                continue


            info = get_detail(href)


            title = info["title"].lower()


            # HLAVNY FILTER
            if "audi" not in title:
                continue

            if "a4" not in title:
                continue


            if any(x in title for x in [
                "diel",
                "svetlo",
                "nárazník",
                "disk",
                "koleso"
            ]):
                continue



            if info["year"]:
                if int(info["year"]) < MIN_YEAR:
                    continue


            if info["price"]:
                price = int(
                    info["price"]
                    .replace("€","")
                    .replace(" ","")
                )

                if price > MAX_PRICE:
                    continue



            embed = {
                "title": "🚗 Audi A4",
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


            send_discord(embed)

            seen.append(href)


    save_seen(seen)



if __name__ == "__main__":
    check()
