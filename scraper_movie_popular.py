from playwright.sync_api import sync_playwright
import json
from datetime import datetime
import config

def scrape_movies_popular():
    url = config.MOVIES_POPULAR_URL
    base_url = config.BASE_URL

    print(f"🌐 Caricamento pagina film popolari: {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto(url, timeout=20000)
            # 🔥 ATTENDE che appaiano i link dei titoli (classe specifica per trending)
            page.wait_for_selector("a.slider-tile-mobile", timeout=15000)
        except Exception as e:
            print(f"❌ Errore nel caricamento: {e}")
            browser.close()
            return []

        # Scorri per caricare più elementi (se necessario)
        for _ in range(3):
            page.mouse.wheel(0, 800)
            page.wait_for_timeout(1000)

        # 🔥 SELEZIONA TUTTI I LINK DEI TITOLI
        items = page.query_selector_all("a.slider-tile-mobile")
        print(f"📦 Trovati {len(items)} elementi")

        movies = []
        for item in items:
            # Dentro il link, cerca l'immagine
            img = item.query_selector("div.title-boxart img")
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

        with open("movies_popular.json", "w", encoding="utf-8") as f:
            json.dump(unique_movies, f, ensure_ascii=False, indent=2)

        print(f"✅ Salvati {len(unique_movies)} film unici in movies_popular.json")
        return unique_movies

if __name__ == "__main__":
    scrape_movies_popular()
