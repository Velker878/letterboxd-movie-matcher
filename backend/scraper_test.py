import time, requests
from bs4 import BeautifulSoup

base_url = 'https://letterboxd.com/'
headers = {"User-Agent": "Mozilla/5.0"}

# Acquiring Usernames
def fetch_usernames():
    print('Enter at least two LetterBoxd usernames (Press Enter to stop)')
    usernames = []
    while True: 
        
        #
        while True:
            username = input('Username: ').strip()
            if username == '':
                break
            usernames.append(username)

        valid_usernames = []
        invalid_usernames = []
        for username in usernames:
            url = f'{base_url}{username}/watchlist/'
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    valid_usernames.append(username)
                else:
                    invalid_usernames.append(username)
            except requests.RequestException:
                invalid_usernames.append(username)       

        if invalid_usernames:
            if len(invalid_usernames) == 1:
                print(f"\n{invalid_usernames[0]}'s watchlist could not be retrieved. Please make sure the username is correct and the watchlist is public.")
            else:
                print(f"\nError checking {"'s, ".join(invalid_usernames)} watchlists could not be retrieved. Please make sure the usernames are correct and the watchlists are public.")
            usernames = [u for u in usernames if u not in invalid_usernames]
            continue

        if len(valid_usernames) < 2:
            print('Please add more usernames.')
            continue

        else:
            return valid_usernames

# Acquiring Watchlist URL's
def fetch_watchlist(usernames):
    urls = [f'{base_url}{username}/watchlist/' for username in usernames]
    return urls

# Scraping watchlist data
def watchlist_parser(url):
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
        response = requests.get(page_url, headers=headers, timeout=10)
        film_soup = BeautifulSoup(response.text, "lxml")

        ul = film_soup.find('ul', class_='-p125')
        if not ul:
            print(f'No films found at {page_url}')
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

        page += 1

    return film_dict

# Compares common films between users
def compare_watchlists(user_watchlists):
    watchlists = list(user_watchlists.values())
    if not watchlists:
        return set()
    common_films = set.intersection(*watchlists)
    return common_films

def main():
    usernames = fetch_usernames()
    urls = fetch_watchlist(usernames)
    user_watchlists = {}

    for user, url in zip(usernames, urls):
        data = watchlist_parser(url)
        user_watchlists[user] = set(data['id'])

    common_films = compare_watchlists(user_watchlists)
    print(f"\nCommon films among {', '.join(usernames)}: {common_films}")

if __name__ == '__main__':
    main() 





    

