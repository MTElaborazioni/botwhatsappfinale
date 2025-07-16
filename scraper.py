# scraper.py
import json, os, time
from woocommerce import API
from dotenv     import load_dotenv

load_dotenv()                       # legge .env se esiste (utile in locale)

wc = API(
    url = os.getenv("WC_SITE"),
    consumer_key    = os.getenv("WC_KEY"),
    consumer_secret = os.getenv("WC_SECRET"),
    version = "wc/v3",
    timeout = 40
)

def fetch_all():
    per_page = 100        # max WooCommerce
    page     = 1
    products = []

    while True:
        resp = wc.get("products", params={"per_page": per_page, "page": page})
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        products.extend(batch)
        page += 1
        print(f"scaricati {len(products)} prodotti…")

    return products

def main(loop=False, delay_h=24):
    while True:
        data = fetch_all()
        with open("/data/products.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 Salvati {len(data)} prodotti — {time.ctime()}")
        if not loop:
            break
        time.sleep(delay_h * 3600)

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--loop", action="store_true")
    args = ap.parse_args()
    main(loop=args.loop)

