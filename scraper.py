from playwright.sync_api import sync_playwright
import json
from datetime import datetime

# URL dell'archivio (ordinato per data di uscita)
URL = "https://streamingcommunityz.support/it/archive?type=movie"

def scrape_movies():
    with sync_playwright() as p:
        # Avvia browser (headless = senza interfaccia grafica)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Vai alla pagina archive
        print("🌐 Caricamento pagina...")
        page.goto(URL)

        # Aspetta che appaiano i film (massimo 15 secondi)
        # I film sono dentro .slider-item, come nella home
        page.wait_for_selector(".slider-item a", timeout=15000)

        # Scorri un po' la pagina per caricare più film (se il sito carica all'infinito)
        # Questo simula lo scroll dell'utente per attivare il caricamento lazy
        for _ in range(3):
            page.mouse.wheel(0, 800)
            page.wait_for_timeout(1000)

        # Prendi tutti i link dei film
        items = page.query_selector_all(".slider-item a")
        print(f"📦 Trovati {len(items)} elementi")

        movies = []
        for item in items:
            img = item.query_selector("img")
            if img:
                titolo = img.get_attribute("alt")
                link = item.get_attribute("href")
                if link and not link.startswith("http"):
                    link = "https://streamingcommunityz.support" + link
                if titolo and link:
                    movies.append({
                        "title": titolo.strip(),
                        "url": link,
                        "fetched_at": datetime.now().isoformat()
                    })

        browser.close()

        # Rimuovi duplicati (stesso titolo potrebbe apparire più volte)
        seen = set()
        unique_movies = []
        for m in movies:
            if m["title"] not in seen:
                seen.add(m["title"])
                unique_movies.append(m)

        # Salva in JSON
        with open("movies.json", "w", encoding="utf-8") as f:
            json.dump(unique_movies, f, ensure_ascii=False, indent=2)

        print(f"✅ Salvati {len(unique_movies)} film unici in movies.json")
        return unique_movies

if __name__ == "__main__":
    scrape_movies()
