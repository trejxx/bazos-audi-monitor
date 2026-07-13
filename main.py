import requests
from bs4 import BeautifulSoup
import json
import os


DISCORD_WEBHOOK = os.environ["DISCORD_WEBHOOK"]

SEARCH_URL = "https://auto.bazos.sk/search.php?hledat=Audi+A4"


def send_discord(message):
    requests.post(
        DISCORD_WEBHOOK,
        json={
            "content": message
        }
    )


def load_seen():
    try:
        with open("seen.json", "r") as f:
            return json.load(f)
    except:
        return []


def save_seen(seen):
    with open("seen.json", "w") as f:
        json.dump(seen, f)


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

    found = 0

    for a in soup.find_all("a", href=True):

        href = a["href"]

        if "inzerat" not in href:
            continue

        if href in seen:
            continue

        title = a.text.strip()

        if "Audi" not in title and "A4" not in title:
            continue

        message = (
            "🚗 **Nový Audi A4 inzerát!**\n\n"
            f"{title}\n"
            f"🔗 {href}"
        )

        send_discord(message)

        seen.append(href)
        found += 1


    save_seen(seen)

    print(f"Hotovo. Nové inzeráty: {found}")


if __name__ == "__main__":
    check()
