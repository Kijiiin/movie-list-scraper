import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

# URL della pagina che contiene i film in ordine di uscita
# (possiamo usare la home o la pagina browse)
url = "https://streamingcommunityz.support/"

# Impostiamo un User-Agent per sembrare un browser normale
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

try:
    # 1. Scarichiamo la pagina HTML
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()  # Se c'è un errore, si ferma

    # 2. Analizziamo l'HTML con BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # 3. Cerchiamo tutti i blocchi che contengono i film
    #    guardando il codice che mi hai mandato, i film sono dentro .slider-item
    items = soup.select('.slider-item a')

    movies = []
    for item in items:
        img = item.find('img')
        if img and img.get('alt'):
            titolo = img['alt'].strip()
            link = item.get('href')
            
            # Se il link è relativo (es. /it/titles/...), lo rendiamo assoluto
            if link and not link.startswith('http'):
                link = "https://streamingcommunityz.support" + link

            # Evitiamo di aggiungere voci vuote
            if titolo and link:
                movies.append({
                    "title": titolo,
                    "url": link,
                    "fetched_at": datetime.now().isoformat()
                })

    # 4. Rimuoviamo eventuali duplicati (se uno stesso titolo compare più volte)
    seen = set()
    unique_movies = []
    for m in movies:
        if m['title'] not in seen:
            seen.add(m['title'])
            unique_movies.append(m)

    # 5. Salviamo tutto in un file JSON
    with open('movies.json', 'w', encoding='utf-8') as f:
        json.dump(unique_movies, f, ensure_ascii=False, indent=2)

    print(f"✅ Scraping completato! Trovati {len(unique_movies)} film.")

except Exception as e:
    print(f"❌ Errore: {e}")
    exit(1)  # Uscita con errore per far capire a GitHub che qualcosa è andato storto
