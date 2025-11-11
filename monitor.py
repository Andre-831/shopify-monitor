import os
import json
import time
import random
import requests
import sys


DISCORD_WEBHOOK = "your Discord webhook"

STATE_FILE = "products_sizes.json"

# list of Shopify sites:
SITES = [
    'https://en.afew-store.com',
    'https://apbstore.com',
    'https://a-ma-maniere.com',
    'https://atmosusa.com',
    'https://bbcicecream.com',
    'https://bdgastore.com/',
    'https://bowsandarrowsberkeley.com',
    'https://burnrubbersneakers.com',
    'https://corporategotem.com',
    'https://courtsidesneakers.com',
    'https://creme321.com',
    'https://thedarksideinitiative.com',
    'https://deadstockofficial.com',
    'https://dtlr.com',
    'https://shop-us.doverstreetmarket.com',
    'https://extrabutterny.com',
    'https://feature.com',
    'https://gallery.canary---yellow.com',
    'https://gbny.com',
    'https://kicktheory.com',
    'https://kith.com',
    'https://lapstoneandhammer.com',
    'https://likelihood.us',
    'https://notre-shop.com',
    'https://onenessboutique.com',
    'https://packershoes.com',
    'https://rockcitykicks.com',
    'https://rsvpgallery.com',
    'https://ruleofnext.com',
    'https://saintalfred.com',
    'https://shoegallerymiami.com',
    'https://shoepalace.com',
    'https://shopnicekicks.com',
    'https://shopwss.com',
    'https://slamjam.com',
    'https://snkrroom.com',
    'https://sneakerpolitics.com',
    'https://socialstatuspgh.com',
    'https://solefly.com',
    'https://svrn.com',
    'https://thebettergeneration.com',
    'https://trophyroomstore.com',
    'https://thepremierstore.com',
    'https://store.unionlosangeles.com',
    'https://upnycstore.com',
    'https://wishatl.com',
    'https://xhibition.co',
    'https://undefeated.com',
    'https://www.ultrawrld.com',
    'https://www.stussy.com'
]

# in seconds
POLL_INTERVAL = 10


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            return json.load(open(STATE_FILE, "r"))
        except json.JSONDecodeError:
            pass
    return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def load_proxies(proxy_file="proxies.txt"):
    lines = []
    if os.path.exists(proxy_file):
        with open(proxy_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    parts = line.split(":")
                    if len(parts) == 4:
                        lines.append({
                            "http":  f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}",
                            "https": f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}",
                        })
    return lines

def random_user_agent():
    choices = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
        " Chrome/115.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        " AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
    ]
    return random.choice(choices)

def send_discord_embed(site, product, sizes_str):
    """Builds and POSTs an embed to your webhook."""
    clean = site.rstrip("/")
    url   = f"{clean}/products/{product['handle']}"
    embed = {
        "title":       product["title"],
        "url":         url,
        "description": f"🛒 Available Sizes: {sizes_str}",
        "color":       5662170,
        "thumbnail":   {"url": product["images"][0]["src"]} if product.get("images") else {},
        "fields": [
            {
                "name":   v["title"],
                "value":  f"[ATC]({clean}/cart/{v['id']}:1)",
                "inline": True
            }
            for v in product["variants"] if v.get("available")
        ],
        "footer": {"text": f"Shopify Monitor • {clean}"},
        
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    payload = {"username": "Shopify Filtered", "embeds": [embed]}
    try:
        r = requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)
        if r.status_code not in (200, 204):
            print(f"\033[1;91m❌ Discord {r.status_code}: {r.text}\033[0m")
            
    except Exception as e:
        print(f"\033[1;91m❌ Discord error: {e}\033[0m")


def main():
    previous = load_state()
    proxies  = load_proxies()
    print(f"Loaded state for {len(previous)} products, {len(proxies)} proxies.")

    try:

        while True:
            for site in SITES:
                print(f"monitoring {site}...")
                proxy = random.choice(proxies) if proxies else None
                headers = {
                    "Accept":        "application/json",
                    "User-Agent":    random_user_agent(),
                }
                try:
                    resp = requests.get(f"{site.rstrip('/')}/products.json",
                                        headers=headers, proxies=proxy, timeout=15)
                    resp.raise_for_status()
                    data = resp.json()
                except Exception as e:
                    print(f"\033[1;91m❌ Error fetching {site}: {e}\033[0m")
                    continue
                counter = 0

                for prod in data.get("products", []):
                    #print(f"product found on {site}: {prod['title']} ({prod['id']}) at {time.strftime('%H:%M:%S')}")
                    # comma-joined sizes for all available variants
                    sizes = ", ".join(v["title"] for v in prod["variants"] if v.get("available"))
                    pid   = str(prod["id"])

                    # if there are sizes and they differ from last time  notify
                    if pid not in previous or (sizes and sizes != previous[pid]):
                        #print(f"New item or update found on {site}: {prod['title']} ({prod['id']}) at {time.strftime('%H:%M:%S')}")
                        send_discord_embed(site, prod, sizes)
                        previous[pid] = sizes
                        counter += 1
                if counter:
                    print(f"\033[1;92m# {counter} product(s) found/updated on {site}\033[0m")
            

            # persist after each full pass
            save_state(previous)
            print(f"[{time.strftime('%H:%M:%S')}] Sleeping {POLL_INTERVAL}s")
            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print("\nExiting...")
        save_state(previous)
        sys.exit(0)



if __name__ == "__main__":
    main()
