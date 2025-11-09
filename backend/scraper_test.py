import time, requests
from bs4 import BeautifulSoup

base_url = 'https://letterboxd.com/'
headers = {"User-Agent": "Mozilla/5.0"}

# Acquiring Usernames
def fetch_usernames():
    usernames = []

    while True:
        username = input("Enter at least 2 LetterBoxd Username (Press Enter to stop): ")
        if username == '':
            break
        usernames.append(username)

    return usernames

# Acquiring Watchlist URL's
def fetch_watchlist(usernames):
    urls = []
    invalid_urls = []
    for username in usernames:
        url = f'{base_url}{username}/watchlist/'
        try:
            response = requests.get(url)
            if response.status_code == 200:
                urls.append(url)
            else:
                invalid_urls.append(url)
        except requests.RequestException:
            invalid_urls.append(url)       

    if invalid_urls:
        if len(invalid_urls) == 1:
            print(f"\nError checking {invalid_urls[0]}. Please make sure the username is correct and the watchlist is public.")
            fetch_usernames()
        else:
            print(f"\nError checking {', '.join(invalid_urls)}. Please make sure the usernames are correct and the watchlists are public.")
            fetch_usernames()
    else:
        pass

    return urls

def watchlist_parser(url):
    film_dict = {
    'id': [],
    'title': [],
    'link': [],
    'poster_image': [],
    'genre': []
    }

    response = requests.get(url, headers=headers, timeout=10)
    film_soup = BeautifulSoup(response.text, "lxml")

    ul = film_soup.find('ul', class_='-p125')
    if not ul:
        print(f'No films found at {url}')
        return film_dict
    
    films = ul.find_all('li')
    for film in films:
        div = film.find('div')
        if not div:
            continue

        film_id = div.get('data-film-id')
        title = div.get('data-item-full-display-name')
        link = div.get('data-item-link')
        poster = film.find('img')['src']

        # Fetch genres per film
        genres = []
        try:
            genres_response = requests.get(f"{base_url}{link}genres/", headers=headers, timeout=10)
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

    return film_dict

def multiple_users():
    lb_users = fetch_usernames()
    watchlist_urls = fetch_watchlist(lb_users)

    for url in watchlist_urls:
        watchlist_data = watchlist_parser(url)
        print(watchlist_data)

multiple_users()





    

