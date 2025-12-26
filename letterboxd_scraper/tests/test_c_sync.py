
import django
django.setup()

from letterboxd_scraper.services import sync_user_watchlist
from letterboxd_scraper.models import User, Film, WatchlistEntry

def test_sync_user():
    username = "sahalwatches"
    user = sync_user_watchlist(username)

    print("User synced:", user.username)

    films = WatchlistEntry.objects.filter(user=user)
    print("Films in watchlist:", films.count())

    assert films.count() > 0
    assert user.last_synced is not None


if __name__ == "__main__":
    test_sync_user()
