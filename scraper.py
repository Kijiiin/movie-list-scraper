from playwright.sync_api import sync_playwright
import requests
import json
from datetime import datetime
import time

# URL dell'archivio (solo film)
URL = "https://streamingcommunityz.support/it/archive?type=movie"

# La tua API key TMDb (mettila qui o come variabile d'ambiente)
TMDB_API_KEY = "7fe396e6f50677047459e8c173f2bd9d"  # la tua chiave

def search_tmdb_id(title, year=None, media_type='movie'):
    """
    Cerca su TMDb l'ID del film o serie TV.
    Restituisce l'ID oppure None se non trovato.
    """
    # Costruisci la query
    search_url = f"https://api.themoviedb.org/3/search/{media_type}"
    params = {
        'api_key': TMDB_API_KEY,
        'query': title,
        'language': 'it-IT',
        'page': 1
    }
    if year:
        # Aggiungi l'anno per migliorare la ricerca (solo per film)
        if media_type == 'movie':
            params['year'] = year

    try:
        response = requests.get(search_url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data['results']:
            # Prendi il primo risultato
            first = data['results'][0]
            # Se l'anno è specificato e non corrisponde, prova a cercare meglio?
            # Per semplicità prendiamo il primo.
            return first['id']
        else:
            return None
    except Exception as e:
        print(f"⚠️ Errore nella ricerca TMDb per '{title}': {e}")
        return None

def scrape_movies():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("🌐 Caricamento pagina...")
        page.goto(URL)
        page.wait_for_selector(".slider-item a", timeout=15000)

        # Scroll per caricare più film (aumenta il range se vuoi più film)
        for _ in range(5):  # facciamo 5 scroll per caricare più contenuti
            page.mouse.wheel(0, 800)
            page.wait_for_timeout(1000)

        items = page.query_selector_all(".slider-item a")
        print(f"📦 Trovati {len(items)} elementi")

        movies = []
        # Per evitare di cercare troppe volte TMDb, limitiamo il numero di film (es. 50)
        # Puoi rimuovere il limite se vuoi tutti
        for idx, item in enumerate(items[:50]):  # Cambia 50 per avere più film
            img = item.query_selector("img")
            if img:
                titolo = img.get_attribute("alt")
                link = item.get_attribute("href")
                if link and not link.startswith("http"):
                    link = "https://streamingcommunityz.support" + link

                if titolo and link:
                    # Tentativo di estrarre l'anno dal titolo? 
                    # Potremmo prendere l'anno dal titolo se presente tra parentesi
                    # Esempio: "Fúria (2025)" - ma potrebbe non esserci.
                    # Per semplicità, lo saltiamo.
                    year = None

                    # Cerca TMDb ID
                    tmdb_id = search_tmdb_id(titolo, year, 'movie')
                    # Se non trovato come film, prova come serie TV? 
                    # Ma vogliamo solo film, quindi skip se non trovato.
                    if tmdb_id is None:
                        # Potresti voler salvare comunque il film senza ID? 
                        # Decidi tu. Per ora lo saltiamo.
                        print(f"⚠️ ID TMDb non trovato per '{titolo}', salto...")
                        continue

                    movies.append({
                        "title": titolo.strip(),
                        "url": link,
                        "tmdb_id": tmdb_id,
                        "fetched_at": datetime.now().isoformat()
                    })
                    # Pausa per evitare rate limit (0.5 secondi tra una ricerca e l'altra)
                    time.sleep(0.5)

        browser.close()

        # Rimuovi duplicati (lo facciamo già con il controllo dell'ID TMDb? 
        # Potrebbero esserci duplicati se lo stesso film compare due volte)
        seen_ids = set()
        unique_movies = []
        for m in movies:
            if m['tmdb_id'] not in seen_ids:
                seen_ids.add(m['tmdb_id'])
                unique_movies.append(m)

        # Salva in JSON
        with open('movies.json', 'w', encoding='utf-8') as f:
            json.dump(unique_movies, f, ensure_ascii=False, indent=2)

        print(f"✅ Salvati {len(unique_movies)} film unici con TMDb ID in movies.json")
        return unique_movies

if __name__ == "__main__":
    scrape_movies()
