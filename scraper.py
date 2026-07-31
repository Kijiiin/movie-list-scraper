from playwright.sync_api import sync_playwright
import json
import re
from datetime import datetime

# URL dell'archivio con solo film
URL = "https://streamingcommunityz.support/it/archive?type=movie"
# Nome del file JSON esistente (per aggiornamento incrementale)
JSON_FILE = "movies.json"

def extract_tmdb_id(page, film_url):
    """Apre la pagina del film e cerca l'ID TMDB."""
    try:
        page.goto(film_url, timeout=10000)
        page.wait_for_selector("body", timeout=5000)
        html = page.content()
        # Cerca pattern comuni: "tmdb_id":12345 oppure "tmdb":12345
        match = re.search(r'"tmdb_id"\s*:\s*(\d+)', html)
        if not match:
            match = re.search(r'"tmdb"\s*:\s*(\d+)', html)
        if match:
            return int(match.group(1))
        # Alternativa: cerca nell'URL o in un meta
        # Se non trovato, restituisce None
        return None
    except Exception as e:
        print(f"   ⚠️ Errore nel recupero TMDB per {film_url}: {e}")
        return None

def scrape_movies():
    # Carica il file JSON esistente (se c'è)
    existing = {}
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Crea un dizionario per accesso veloce per titolo
            for item in data:
                existing[item["title"]] = item
    except FileNotFoundError:
        existing = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("🌐 Caricamento pagina archive...")
        page.goto(URL)

        # Aspetta che compaiano i link ai film (max 20 secondi)
        page.wait_for_selector("a[href*='/titles/']", timeout=20000)

        # Scroll per caricare più film (ripetere finché non smette di caricare)
        last_count = 0
        for _ in range(5):  # max 5 scroll
            page.mouse.wheel(0, 1000)
            page.wait_for_timeout(2000)
            # Conta i link attuali
            links = page.query_selector_all("a[href*='/titles/']")
            if len(links) == last_count:
                break  # non ci sono più nuovi film
            last_count = len(links)

        # Raccogli tutti i link
        links = page.query_selector_all("a[href*='/titles/']")
        print(f"📦 Trovati {len(links)} link a film.")

        new_movies = []
        updated_count = 0

        for link in links:
            href = link.get_attribute("href")
            if not href:
                continue
            if not href.startswith("http"):
                href = "https://streamingcommunityz.support" + href

            # Cerca l'immagine all'interno del link
            img = link.query_selector("img")
            if not img:
                continue
            title = img.get_attribute("alt")
            if not title:
                continue
            title = title.strip()

            # Se il film esiste già e ha tmdb_id, lo saltiamo
            if title in existing and existing[title].get("tmdb_id"):
                print(f"⏩ Già presente: {title}")
                continue

            # Altrimenti lo elaboriamo
            print(f"🆕 Nuovo film: {title}")
            # Apri la pagina del film per trovare tmdb_id
            tmdb_id = extract_tmdb_id(page, href)

            movie_data = {
                "title": title,
                "url": href,
                "tmdb_id": tmdb_id,
                "fetched_at": datetime.now().isoformat()
            }
            new_movies.append(movie_data)
            updated_count += 1

            # Aggiorna il dizionario esistente (per evitare duplicati nello stesso run)
            existing[title] = movie_data

        browser.close()

        # Ora uniamo i dati esistenti con i nuovi
        # existing contiene già tutti (vecchi + nuovi), ma dobbiamo convertire in lista
        final_list = list(existing.values())

        # Salva in JSON
        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(final_list, f, ensure_ascii=False, indent=2)

        print(f"✅ Aggiornamento completato. Totale film: {len(final_list)}, nuovi aggiunti/aggiornati: {updated_count}")

if __name__ == "__main__":
    scrape_movies()
