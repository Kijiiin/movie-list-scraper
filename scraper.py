from playwright.sync_api import sync_playwright
import json
from datetime import datetime

url = "https://streamingcommunityz.support/"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url)
    
    # Aspetta che appaia almeno un elemento .slider-item (attesa fino a 15 secondi)
    page.wait_for_selector('.slider-item', timeout=15000)
    
    # Ora prendi tutti i link che contengono le immagini
    items = page.query_selector_all('.slider-item a')
    movies = []
    
    for item in items:
        img = item.query_selector('img')
        if img:
            titolo = img.get_attribute('alt')
            link = item.get_attribute('href')
            if link and not link.startswith('http'):
                link = "https://streamingcommunityz.support" + link
            if titolo and link:
                movies.append({
                    "title": titolo.strip(),
                    "url": link,
                    "fetched_at": datetime.now().isoformat()
                })
    
    browser.close()
    
    # Rimozione duplicati
    seen = set()
    unique_movies = []
    for m in movies:
        if m['title'] not in seen:
            seen.add(m['title'])
            unique_movies.append(m)
    
    with open('movies.json', 'w', encoding='utf-8') as f:
        json.dump(unique_movies, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Trovati {len(unique_movies)} film.")
