import time, requests, re
from bs4 import BeautifulSoup

BASE_URL = 'https://letterboxd.com'
HEADERS = {"User-Agent": "Mozilla/5.0"}

def validate_usernames(usernames):
    """Validate Letterboxd usernames and return structured results."""
    
    results = {
        'valid': {},
        'invalid': {}
    }

    for username in usernames:
        url = f'{BASE_URL}/{username}/watchlist/'
        try:
            response = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=False)
            status = response.status_code

            if status == 200:
                pfp_url = fetch_user_pfp(username)
                results['valid'][username] = {
                    "pfp": pfp_url
                }
            elif status == 404:
                results['invalid'][username] = 'User not found'
            elif status == 403:
                results['invalid'][username] = 'Watchlist is not public'
            elif status in (301, 302):
                results['invalid'][username] = 'Watchlist unavailable'
            else:
                results['invalid'][username] = f'HTTP error {status}'

        except requests.Timeout:
            results['invalid'][username] = 'Request timed out'
        except requests.RequestException:
            results['invalid'][username] = 'Network error'
        
        time.sleep(0.5)       

    return results

def fetch_user_pfp(username):
    """Fetch the profile picture URL for a validated username (Assumes user exists and profile is accessible)"""
    url = f'{BASE_URL}/{username}/'

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'lxml')
        pfp_div = soup.find('div', class_='profile-avatar')
        if not pfp_div:
            return None
        pfp_img = pfp_div.select_one('img')

        if pfp_img and pfp_img.get('src'):
            return pfp_img['src']
        
    except requests.RequestException:
        pass

    return None

def scrape_watchlist(url):
    """Scrape a user's Letterboxd watchlist and return film identifiers."""
    print(f"--- DEBUG: Starting scrape for {url} ---") # Print Debugging
    films = []
    page = 1

    while True:
        print(f"--- DEBUG: Scraping Page {page} ---") # Print Debugging 
        page_url = url if page == 1 else f"{url}page/{page}/"
        response = requests.get(page_url, headers=HEADERS, timeout=10)
        
        try: #DEBUG
            response = requests.get(page_url, headers=HEADERS, timeout=10)
            print(f"--- DEBUG: Page {page} status code: {response.status_code} ---") # DEBUG
        except Exception as e:
            print(f"--- DEBUG: Network error on page {page}: {e} ---") # DEBUG
            break

        soup = BeautifulSoup(response.text, "lxml")

        ul = soup.find('ul', class_='-p125')
        if not ul:
            print(f"--- DEBUG: No UL found on page {page}. Stopping. ---") # DEBUG
            break

        items_found = len(ul.find_all('li'))
        print(f"--- DEBUG: Found {items_found} items on page {page} ---") # DEBUG
        
        items = ul.find_all('li')
        if not items:
            print(f"--- DEBUG: Page {page} has a list but no movies. Stopping. ---")
            break

        for li in items:
            div = li.find('div')
            if not div:
                continue

            title = div.get('data-item-full-display-name')
            slug = div.get('data-item-slug')

            year = None

            if title:
                match = re.search(r'\((\d{4})\)\s*$', title)
                if match:
                    year = int(match.group(1))
                    title = title[:match.start()].strip()

            films.append({
                "title": title,
                "year": year,
                "slug": slug,
                "letterboxd_url": f"{BASE_URL}/film/{slug}/" if slug else None

            })

        page += 1
        time.sleep(1)
    
    print(f"--- DEBUG: Scrape finished. Total films: {len(films)} ---") # DEBUG
    return films