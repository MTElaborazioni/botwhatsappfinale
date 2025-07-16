import requests, json, time
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Header finto da normale browser (evita pagine “vuote”/403)
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0 Safari/537.36"
    )
}


BASE = "https://www.mtelaborazioni.it"
CAT_URLS = [
    "/product-category/aspirazioni-dirette/",
    "/product-category/intercooler-maggiorati/",
    # ↳ aggiungi qui TUTTE le categorie principali
]

def scrap_category(cat_url):
    """
    cat_url deve *terminare* con "/", es. "/product-category/scarichi/"
    """
    products = []
    page = 1
    while True:
        # ➜  pagina 1  = URL base
        # ➜  pagina 2+ = …/page/<n>/
        url = urljoin(BASE, cat_url if page == 1 else f"{cat_url}page/{page}/")
        print("→", url)

        html = requests.get(url, headers=HEADERS, timeout=20).text
        
# DEBUG: guarda i primi 600 caratteri di HTML
        print("‑‑‑ sorgente inizio ‑‑‑")
        print(html[:600])
        print("‑‑‑ fine ‑‑‑\n")

        soup = BeautifulSoup(html, "lxml")

        items = soup.select("ul.products li.product")
        print(f"   trovati {len(items)} prodotti in questa pagina")
        if not items:
            break   # fine categoria

        for li in items:
            a = li.select_one("a.woocommerce-LoopProduct-link")
            if not a:
                continue
            products.append({
                "name": a.get_text(" ", strip=True),
                "url": a["href"],
                "price": (li.select_one(".price") or "").get_text(" ", strip=True),
                "cat": cat_url.strip("/")
            })

        page += 1
        time.sleep(0.5)

    return products


def run():
    all_prod = []
    for cat in CAT_URLS:
        all_prod += scrap_category(cat)
    print("Totale prodotti:", len(all_prod))
    with open("products.json", "w", encoding="utf-8") as f:
        json.dump(all_prod, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run()
