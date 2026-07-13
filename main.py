import requests
from bs4 import BeautifulSoup
import json
import os
import re
from datetime import datetime


DISCORD_WEBHOOK = os.environ["DISCORD_WEBHOOK"]

BASE_URL = "https://auto.bazos.sk"

PAGES = [
    f"{BASE_URL}/inzeraty/audi-a4/",
    f"{BASE_URL}/inzeraty/audi-a4/2/",
    f"{BASE_URL}/inzeraty/audi-a4/3/",
    f"{BASE_URL}/inzeraty/audi-a4/4/",
    f"{BASE_URL}/inzeraty/audi-a4/5/",
    f"{BASE_URL}/inzeraty/audi-a4/6/",
    f"{BASE_URL}/inzeraty/audi-a4/7/",
    f"{BASE_URL}/inzeraty/audi-a4/8/",
    f"{BASE_URL}/inzeraty/audi-a4/9/",
    f"{BASE_URL}/inzeraty/audi-a4/10/",
]


DATABASE = "database.json"


def load_database():
    try:
        with open(DATABASE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_database(data):
    with open(DATABASE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)



def discord_send(embed):

    requests.post(
        DISCORD_WEBHOOK,
        json={
            "embeds": [embed]
        },
        timeout=20
    )



def parse_price(text):

    m = re.search(
        r"(\d[\d\s]*)\s?€",
        text
    )

    if m:
        return int(
            m.group(1).replace(" ", "")
        )

    return None



def parse_km(text):

    text = text.lower()

    patterns = [
        r"(\d+)\s?xxx\s?km",
        r"(\d[\d\s]*)\s?km",
        r"(\d+)\s?(tis|tkm)"
    ]

    for p in patterns:

        m = re.search(p, text)

        if m:

            value = int(
                m.group(1).replace(" ", "")
            )

            if "tis" in m.group(0) or "tkm" in m.group(0):
                value *= 1000

            return value

    return None



def parse_year(text):

    patterns = [
        r"r\.v\.\s?(20\d{2})",
        r"rok výroby\s?(20\d{2})",
        r"vyrobené\s?(20\d{2})",
        r"(20\d{2})\s?ročník"
    ]

    for p in patterns:

        m = re.search(
            p,
            text.lower()
        )

        if m:
            return int(m.group(1))

    return None



def get_score(title):

    score = 0
    title = title.lower()

    words = {
        "avant": 2,
        "quattro": 2,
        "s line": 2,
        "matrix": 1,
        "35 tfsi": 1,
        "40 tfsi": 1,
        "40 tdi": 1,
    }

    for word, points in words.items():

        if word in title:
            score += points

    return score



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


    h1 = soup.find("h1")

    title = h1.text.strip() if h1 else ""


    image = None

    img = soup.find(
        "meta",
        property="og:image"
    )

    if img:
        image = img.get("content")


    return {
        "title": title,
        "price": parse_price(text),
        "km": parse_km(text),
        "year": parse_year(text),
        "image": image
    }



def send_new_car(info, href):

    score = get_score(info["title"])

    label = ""

    if score >= 5:
        label = "🔥 TOP KUS"


    embed = {

        "title": f"🚗 {label} Audi A4",

        "description": info["title"],

        "url": href,

        "fields": [

            {
                "name": "💶 Cena",
                "value": f"{info['price']} €" if info["price"] else "Neudaná",
                "inline": True
            },

            {
                "name": "📅 Rok",
                "value": str(info["year"]) if info["year"] else "Neoverený",
                "inline": True
            },

            {
                "name": "🛣️ Km",
                "value": f"{info['km']} km" if info["km"] else "Neudané",
                "inline": True
            }

        ]
    }


    if info["image"]:
        embed["image"] = {
            "url": info["image"]
        }


    discord_send(embed)



def send_price_drop(info, href, old_price, new_price):

    difference = old_price - new_price


    embed = {

        "title": "🚨 Audi A4 ZNÍŽENIE CENY",

        "description": info["title"],

        "url": href,

        "fields": [

            {
                "name": "💶 Pôvodná cena",
                "value": f"{old_price} €",
                "inline": True
            },

            {
                "name": "💰 Nová cena",
                "value": f"{new_price} €",
                "inline": True
            },

            {
                "name": "⬇️ Rozdiel",
                "value": f"-{difference} €",
                "inline": True
            }

        ]

    }


    if info["image"]:
        embed["image"] = {
            "url": info["image"]
        }


    discord_send(embed)



def check():

    database = load_database()


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


            info = get_detail(href)


            title = info["title"].lower()


            if "audi" not in title:
                continue


            if "a4" not in title:
                continue



            # EXISTUJÚCE AUTO - KONTROLA CENY

            if href in database:


                old_price = database[href].get("price")

                new_price = info["price"]


                if (
                    old_price
                    and new_price
                    and new_price < old_price
                ):

                    send_price_drop(
                        info,
                        href,
                        old_price,
                        new_price
                    )


                database[href]["price"] = new_price

                continue



            # NOVÉ AUTO

            send_new_car(
                info,
                href
            )


            database[href] = {

                "title": info["title"],

                "first_seen": datetime.now().isoformat(),

                "price": info["price"]

            }



    save_database(database)



if __name__ == "__main__":
    check()
