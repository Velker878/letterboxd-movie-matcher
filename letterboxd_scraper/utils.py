import time, requests
from bs4 import BeautifulSoup

BASE_URL = 'https://letterboxd.com/'
HEADERS = {"User-Agent": "Mozilla/5.0"}

def validate_usernames(usernames):
    """Check which usernames are valid"""
    valid_usernames = []
    invalid_usernames = []
    for username in usernames:
        url = f'{BASE_URL}{username}/watchlist/'
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                valid_usernames.append(username)
            else:
                invalid_usernames.append(username)
        except requests.RequestException:
            invalid_usernames.append(username)       

    return valid_usernames, invalid_usernames

def fetch_watchlist(usernames):
    """Build a list of watchlist urls"""
    urls = [f'{BASE_URL}{username}/watchlist/' for username in usernames]
    return urls

def watchlist_parser(url):
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
        
        films = ul.find_all('li')
        if not films:
            break
        
        for film in films:
            div = film.find('div')
            if not div:
                continue

            film_id = div.get('data-film-id')
            title = div.get('data-item-full-display-name')
            link = div.get('data-item-link')
            poster = film.find('img')['src']

            # Fetch genres per film
            try:
                genres_response = requests.get(f"{BASE_URL}{link}genres/", headers=HEADERS, timeout=10)
                genre_soup = BeautifulSoup(genres_response.text, "lxml")
                genre_div = genre_soup.select_one('div.text-sluglist.capitalize')
                if genre_div:
                    genres = [a.text.strip() for a in genre_div.find_all('a')]
                else:
                    genres = ['Miscellaneous']
            except Exception:
                genres = ['Miscellaneous']

            # Add parsed data to dict
            film_dict['id'].append(film_id)
            film_dict['title'].append(title)
            film_dict['link'].append(link)
            film_dict['poster_image'].append(poster)
            film_dict['genre'].append(genres)

        page += 1

    return film_dict

def compare_watchlists(user_watchlists):
    """Find common films between users"""
    watchlists = list(user_watchlists.values())
    if not watchlists:
        return set()
    common_films = set.intersection(*watchlists)
    return common_films