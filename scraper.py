from playwright.sync_api import sync_playwright
import json
import re
from datetime import datetime

URL = "https://streamingcommunityz.support/it/archive?type=movie"
JSON_FILE = "movies.json"

def extract_tmdb_id(page, film_url):
    """Apre la pagina del film e cerca l'ID TMDB."""
    try:
        page.goto(film_url, timeout=10000)
        page.wait_for_selector("body", timeout=5000)
        html = page.content()
        
        # Cerca "tmdb_id":12345 o "tmdb":12345
        match = re.search(r'"tmdb_id"\s*:\s*(\d+)', html)
        if not match:
            match = re.search(r'"tmdb"\s*:\s*(\d+)', html)
        if match:
            return int(match.group(1))
        
        # Cerca in un tag meta
        meta = page.query_selector('meta[name="tmdb-id"]')
        if meta:
            return int(meta.get_attribute("content"))
        
        return None
    except Exception as e:
        print(f"   ⚠️ Errore: {e}")
        return None

def scrape_movies():
    # Carica il JSON esistente (se c'è)
    existing_movies = {}
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                existing_movies[item["title"]] = item
        print(f"📂 Caricati {len(existing_movies)} film dal JSON esistente.")
    except FileNotFoundError:
        print("📂 Nessun JSON esistente. Creazione da zero.")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("🌐 Caricamento pagina archive...")
        page.goto(URL)
        page.wait_for_selector(".slider-item a", timeout=15000)

        # Scroll per caricare più film
        for _ in range(3):
            page.mouse.wheel(0, 800)
            page.wait_for_timeout(1000)

        items = page.query_selector_all(".slider-item a")
        print(f"📦 Trovati {len(items)} elementi.")

        new_movies = []
        updated_count = 0

        for item in items:
            img = item.query_selector("img")
            if not img:
                continue
            titolo = img.get_attribute("alt")
            if not titolo:
                continue
            titolo = titolo.strip()
            
            link = item.get_attribute("href")
            if link and not link.startswith("http"):
                link = "https://streamingcommunityz.support" + link

            # Se il film esiste già e ha tmdb_id, saltalo
            if titolo in existing_movies and existing_movies[titolo].get("tmdb_id"):
                print(f"⏩ Già presente: {titolo} (ID: {existing_movies[titolo]['tmdb_id']})")
                continue

            print(f"🆕 Elaborazione: {titolo}")
            tmdb_id = extract_tmdb_id(page, link)

            movie_data = {
                "title": titolo,
                "url": link,
                "tmdb_id": tmdb_id,
                "fetched_at": datetime.now().isoformat()
            }
            existing_movies[titolo] = movie_data
            new_movies.append(movie_data)
            updated_count += 1

            # Se abbiamo già processato 20 nuovi film, fermiamoci (per evitare timeout su GitHub Actions)
            if updated_count >= 20:
                print("⏹️ Limite di 20 nuovi film raggiunto. Interrompo per evitare timeout.")
                break

        browser.close()

        # Salva tutto il dizionario come lista
        final_list = list(existing_movies.values())
        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(final_list, f, ensure_ascii=False, indent=2)

        print(f"✅ Completato! Totale: {len(final_list)} film. Nuovi elaborati: {updated_count}.")

if __name__ == "__main__":
    scrape_movies()
