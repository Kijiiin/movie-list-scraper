from playwright.sync_api import sync_playwright
import json
from datetime import datetime
import config  # 👈 importa la configurazione

def scrape_movies():
    # Usa l'URL da config
    url = config.MOVIES_URL
    base_url = config.BASE_URL

    print(f"🌐 Caricamento pagina film: {url}")

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

        movies = []
        for item in items:
            img = item.query_selector("img")
            if img:
                titolo = img.get_attribute("alt")
                link = item.get_attribute("href")
                if link and not link.startswith("http"):
                    link = base_url + link
                if titolo and link:
                    movies.append({
                        "title": titolo.strip(),
                        "url": link,
                        "fetched_at": datetime.now().isoformat()
                    })

        browser.close()

        seen = set()
        unique_movies = []
        for m in movies:
            if m["title"] not in seen:
                seen.add(m["title"])
                unique_movies.append(m)

        with open("movies.json", "w", encoding="utf-8") as f:
            json.dump(unique_movies, f, ensure_ascii=False, indent=2)

        print(f"✅ Salvati {len(unique_movies)} film unici in movies.json")
        return unique_movies

if __name__ == "__main__":
    scrape_movies()
