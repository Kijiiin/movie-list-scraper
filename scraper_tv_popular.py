from playwright.sync_api import sync_playwright
import json
from datetime import datetime
import config  # 👈 importa la configurazione

def scrape_tv():
    # Usa l'URL da config
    url = config.TV_URL
    base_url = config.BASE_URL

    print(f"🌐 Caricamento pagina serie TV: {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
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
                    link = base_url + link
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

        with open("tv_popular.json", "w", encoding="utf-8") as f:
            json.dump(unique_series, f, ensure_ascii=False, indent=2)

        print(f"✅ Salvate {len(unique_series)} serie TV uniche in tv_popular.json")
        return unique_series

if __name__ == "__main__":
    scrape_tv()
