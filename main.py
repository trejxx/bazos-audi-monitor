import requests
from bs4 import BeautifulSoup

URL = "https://auto.bazos.sk/search.php?hledat=Audi+A4"

headers = {
    "User-Agent": "Mozilla/5.0"
}

r = requests.get(URL, headers=headers)

print("Status:", r.status_code)
print("Dĺžka stránky:", len(r.text))

soup = BeautifulSoup(r.text, "html.parser")

for a in soup.find_all("a", href=True)[:30]:
    print(a.text.strip(), a["href"])
