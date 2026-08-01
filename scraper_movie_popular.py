from playwright.sync_api import sync_playwright
import json
from datetime import datetime
import config

def scrape_tv_popular():
    url = config.TV_POPULAR_URL
    base_url = config.BASE_URL

    print(f"🌐 Caricamento pagina serie TV popolari: {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto(url, timeout=20000)
            # 🔥 ATTENDE che appaiano i link dei titoli
            page.wait_for_selector("a.slider-tile-mobile", timeout=15000)
        except Exception as e:
            print(f"❌ Errore nel caricamento: {e}")
            browser.close()
            return []

        for _ in range(3):
            page.mouse.wheel(0, 800)
            page.wait_for_timeout(1000)

        items = page.query_selector_all("a.slider-tile-mobile")
        print(f"📦 Trovati {len(items)} elementi")

        series = []
        for item in items:
            img = item.query_selector("div.title-boxart img")
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
    scrape_tv_popular()
