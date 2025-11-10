# 🛒 Shopify Multi-Store Monitor

A lightweight Shopify monitor that watches multiple sneaker/streetwear stores, tracks size availability, and sends **Discord webhook embeds** with direct **add-to-cart (ATC)** links.

---

## 📁 Files

- [monitor.py](monitor.py) – main monitor script (polls `/products.json`, tracks sizes, sends Discord embeds)  
- [scrape.py](scrape.py) – helper script for scraping/processing product data (one-off/utility)  
- [products_raw.json](products_raw.json) – raw shopify data
- [products_clean.json](products_clean.json) – cleaned/filtered product data (debug/logging output)  
- [products_sizes.json](products_sizes.json) – saved state of product → sizes, used to avoid duplicate alerts  
- [proxies.txt](proxies.txt) – rotating proxies list (`host:port:user:pass` per line)

---

## ⚙️ What It Does

- Polls a list of Shopify storefronts (sneaker/boutique sites) every `POLL_INTERVAL` seconds  
- Calls each store’s `/products.json` endpoint  
- Tracks **available sizes** for each product using a local state file  
- When sizes change or a new product appears, sends a **Discord embed** with:
  - Product title and product URL  
  - Thumbnail image  
  - Available sizes  
  - One ATC link per size (`/cart/{variant_id}:1`)

---

## 🔧 Configuration

### 1. Discord Webhook

In [monitor.py](monitor.py), set your Discord webhook:

```python
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/..."
