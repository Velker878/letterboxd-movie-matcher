import time, requests
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

def scrape_watchlist(url):
    """Scrape and parse a users watchlist into a dict."""
    film_dict = {
        'id': [],
        'title': [],
        'link': [],
        'poster_image': [],
        'genres': []
    }
    page = 1

    while True:
        page_url = url if page == 1 else f"{url}page/{page}/"
        response = requests.get(page_url, headers=HEADERS, timeout=10)
        
        soup = BeautifulSoup(response.text, "lxml")
        ul = soup.find('ul', class_='-p125')
        if not ul:
            break

        films = ul.find_all('li')
        if not films:
            break

        for li in films:
            div = li.find('div')
            if not div:
                continue

            film_id = div.get('data-film-id')
            title = div.get('data-item-full-display-name')
            link = div.get('data-item-link')
            poster = div.get('data-poster-url')

            # Fetch genres per film
            try:
                g_url = f"{BASE_URL}{link}genres/"
                g_resp = requests.get(g_url, headers=HEADERS, timeout=10)
                g_soup = BeautifulSoup(g_resp.text, "lxml")
                g_div = g_soup.select_one('div.text-sluglist.capitalize')
                genres = [a.text.strip() for a in g_div.find_all('a')] if g_div else []
            except:
                genres = []

            # Add parsed data to dict
            film_dict['id'].append(film_id)
            film_dict['title'].append(title)
            film_dict['link'].append(f'{BASE_URL}{link}')
            film_dict['poster_image'].append(poster)
            film_dict['genres'].append(genres)

        page += 1
        time.sleep(1)
    
    return film_dict

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

