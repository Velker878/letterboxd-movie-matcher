from datetime import timedelta
from django.db import transaction
from django.utils.timezone import now
from .models import User, Film, WatchlistEntry
from .utils import scrape_watchlist, validate_usernames, BASE_URL

def sync_user_watchlist(username):
    """
    Scrape + store a user's watchlist into the database.
    Only rescrapes if last sync is stale.
    """
    user, created = User.objects.get_or_create(username=username)
    
    if not created and user.last_synced:
        age = now() - user.last_synced
        if age < timedelta(hours=12):
            return user
        
    url = f'{BASE_URL}/{username}/watchlist/'
    parsed_data = scrape_watchlist(url)

    with transaction.atomic():
        WatchlistEntry.objects.filter(user=user).delete()
        for i in range(len(parsed_data['id'])):
            film, _ = Film.objects.update_or_create(
                film_id = parsed_data['id'][i],
                defaults={
                    'title': parsed_data['title'][i],
                    'link': parsed_data['link'][i],
                    'poster_image': parsed_data['poster_image'][i],
                    'genres': parsed_data['genres'][i],
                }
            )
            WatchlistEntry.objects.get_or_create(user=user, film=film)

        user.last_synced = now()
        user.save()
    return user

def compare_users(usernames):
    """
    Validate → Sync → Compute intersection of watchlists from DB only.
    """
    validation = validate_usernames(usernames)

    valid_users = validation['valid']
    valid_usernames = list(valid_users.keys())
    invalid_usernames = validation['invalid']

    if invalid_usernames:
        return {
            'error': 'invalid_usernames',
            'valid_users': valid_users,
            'invalid_usernames': invalid_usernames,
            'common_films': []
        }
    
    users = [sync_user_watchlist(u) for u in valid_usernames]
    
    watchlists = []
    for user in users:
        film_ids = set(
            WatchlistEntry.objects.filter(user=user).values_list('film__film_id', flat=True)
        )
        watchlists.append(film_ids)

    common_ids = set.intersection(*watchlists) if watchlists else set()
    common_films = list(Film.objects.filter(film_id__in=common_ids))

    return {
        'valid_users': valid_users,
        'invalid_usernames': {},
        'common_films': common_films,
    }
