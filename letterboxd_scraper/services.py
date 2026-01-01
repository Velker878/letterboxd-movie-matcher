from datetime import timedelta
from django.db import transaction
from django.utils.timezone import now
from .models import User, Film, WatchlistEntry
from .utils import scrape_watchlist, validate_usernames, BASE_URL
from . import tmdb_service

def sync_user_watchlist(username):
    print(f"--- DEBUG: Syncing user: {username} ---") # DEBUG
    user, created = User.objects.get_or_create(username=username)
    
    if not created and user.last_synced:
        age = now() - user.last_synced
        if age < timedelta(hours=12):
            return user
        
    url = f'{BASE_URL}/{username}/watchlist/'
    parsed_data = scrape_watchlist(url)

    print(f"--- DEBUG: Saving {len(parsed_data)} films to DB for {username} ---") # DEBUG

    try:
        with transaction.atomic():
            WatchlistEntry.objects.filter(user=user).delete()

            for film_data in parsed_data:
                # DEBUG: print the first film being saved to check for errors
                if parsed_data.index(film_data) == 0:
                     print(f"--- DEBUG: Saving first film: {film_data} ---")

                film, _ = Film.objects.update_or_create(
                    letterboxd_id=film_data['slug'], # Ensure this is letterboxd_id NOT film_id
                    defaults={
                        'title': film_data['title'],
                        'year': film_data['year'],
                        'letterboxd_slug': film_data['slug'],
                    }
                )
                WatchlistEntry.objects.get_or_create(user=user, film=film)

            user.last_synced = now()
            user.save()
            print(f"--- DEBUG: Database save complete for {username} ---") # DEBUG
    except Exception as e:
        print(f"--- DEBUG: CRITICAL DATABASE ERROR: {e} ---") # DEBUG
        raise e # Re-raise to let Django handle it

    return user

def compare_users(usernames):
    validation = validate_usernames(usernames)
    valid_usernames = list(validation['valid'].keys())
    
    users = [sync_user_watchlist(u) for u in valid_usernames]

    if not users:
        return {'error': 'No valid users', 'common_films': []}
    
    watchlists = []
    for user in users:
        film_ids = set(
            WatchlistEntry.objects.filter(user=user).values_list('film__letterboxd_slug', flat=True)
        )
        watchlists.append(film_ids)

    common_ids = set.intersection(*watchlists) if watchlists else set()
    common_films = Film.objects.filter(letterboxd_slug__in=common_ids)

    tmdb_cache = {}

    enriched_films = []
    for film in common_films:
        if not film.tmdb_id or not film.poster_image:
            key = (film.title, film.year)

            if key in tmdb_cache:
                tmdb_data = tmdb_cache[key]
            else:
                tmdb_data = tmdb_service.search_movie(film.title, film.year)
                tmdb_cache[key] = tmdb_data
            
            if tmdb_data:
                film.tmdb_id = tmdb_data.get('id')
                film.poster_image = tmdb_service.get_poster_url(tmdb_data.get('poster_path'))
                film.genres = tmdb_data.get('genre_ids', [])
                film.save()
        
        enriched_films.append(film)

    return {
        'valid_users': validation['valid'],
        'invalid_usernames': validation['invalid'],
        'common_films': list(common_films),
    }
