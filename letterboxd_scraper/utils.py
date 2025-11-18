import time, requests
from bs4 import BeautifulSoup

BASE_URL = 'https://letterboxd.com/'
HEADERS = {"User-Agent": "Mozilla/5.0"}

def validate_usernames(usernames):
    """Check which usernames are valid"""
    valid = []
    invalid = []
    for username in usernames:
        url = f'{BASE_URL}{username}/watchlist/'
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                valid.append(username)
            else:
                invalid.append(username)
        except Exception:
            invalid.append(username)
        time.sleep(1)       

    return valid, invalid

def scrape_watchlist(url):
    """Scrape and parse a users watchlist into a dict."""
    film_dict = {
    'id': [],
    'title': [],
    'link': [],
    'poster_image': [],
    'genre': []
    }
    page = 1

    while True:
        page_url = url if page == 1 else f"{url}page/{page}/"
        response = requests.get(page_url, headers=HEADERS, timeout=10)
        
        film_soup = BeautifulSoup(response.text, "lxml")
        ul = film_soup.find('ul', class_='-p125')
        if not ul:
            break

        for li in ul.find_all('li'):
            div = li.find('div')
            if not div:
                continue

            film_id = div.get('data-film-id')
            title = div.get('data-item-full-display-name')
            link = div.get('data-item-link')
            poster_img = li.find('img')['src']

            # Fetch genres per film
            try:
                g_resp = requests.get(f"{BASE_URL}{link}genres/", headers=HEADERS, timeout=10)
                g_soup = BeautifulSoup(g_resp.text, "lxml")
                g_div = g_soup.select_one('div.text-sluglist.capitalize')
                genres = [a.text.strip() for a in g_div.find_all('a')] if g_div else []
            except:
                genres = []

            # Add parsed data to dict
            film_dict['id'].append(film_id)
            film_dict['title'].append(title)
            film_dict['link'].append(f'{BASE_URL}{link}')
            film_dict['poster_image'].append(poster_img)
            film_dict['genre'].append(genres)

        time.sleep(1)
        page += 1

    return film_dict