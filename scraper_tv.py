# scraper_tv.py
from playwright.sync_api import sync_playwright
import json
from datetime import datetime

# 🔥 URL per le SERIE TV (invece di type=movie)
URL = "https://streamingcommunityz.support/it/archive?type=tv"

def scrape_tv():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("🌐 Caricamento pagina serie TV...")
        page.goto(URL)
        page.wait_for_selector(".slider-item a", timeout=15000)
        for _ in range(3):
            page.mouse.wheel(0, 800)
            page.wait_for_timeout(1000)
        items = page.query_selector_all(".slider-item a")
        print(f"📦 Trovati {len(items)} elementi")

        series = []
        for item in items:
            img = item.query_selector("img")
            if img:
                titolo = img.get_attribute("alt")
                link = item.get_attribute("href")
                if link and not link.startswith("http"):
                    link = "https://streamingcommunityz.support" + link
                if titolo and link:
                    series.append({
                        "title": titolo.strip(),
                        "url": link,
                        "fetched_at": datetime.now().isoformat()
                    })
        browser.close()

        seen = set()
        unique_series = []
        for s in series:
            if s["title"] not in seen:
                seen.add(s["title"])
                unique_series.append(s)

        # 🔥 Salva con un nome diverso
        with open("tv.json", "w", encoding="utf-8") as f:
            json.dump(unique_series, f, ensure_ascii=False, indent=2)

        print(f"✅ Salvate {len(unique_series)} serie TV uniche in tv.json")
        return unique_series

if __name__ == "__main__":
    scrape_tv()
