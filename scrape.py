import requests
import json




# Setup session to act like a browser
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    'Accept': 'application/json'
})

# Optional: set any Shopify-related cookies (not required here)
session.cookies.set('cart_currency', 'USD')
session.cookies.set('localization', 'US')

# Fetch product data
url = "https://kith.com/products.json"
response = session.get(url)

# Parse and write to file
if response.status_code == 200:
    data = response.json()
    with open("products_clean.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Saved {len(data['products'])} products to products_clean.json")
else:
    print(f"❌ Failed to fetch products: HTTP {response.status_code}")
