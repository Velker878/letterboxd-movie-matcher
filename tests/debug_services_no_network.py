# tests/debug_services_no_network.py
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from letterboxd_scraper import services
from letterboxd_scraper.models import User, Film, WatchlistEntry

# Monkeypatch utils functions
def fake_validate(usernames):
    return (usernames, [])  # all valid

def fake_scrape(url):
    # A small sample matching your scrub format
    return {
        "id": ["f1", "f2"],
        "title": ["Movie 1", "Movie 2"],
        "link": ["https://letterboxd.com/film/movie-1/", "https://letterboxd.com/film/movie-2/"],
        "poster_image": ["https://img/1.jpg", "https://img/2.jpg"],
        "genres": [["Drama"], ["Comedy"]],
    }

# Inject fakes
services.validate_usernames = fake_validate
services.scrape_watchlist = fake_scrape

# Run sync and compare
u1 = services.sync_user_watchlist("alice")
u2 = services.sync_user_watchlist("bob")

print("Users in DB:", list(User.objects.values_list("username", flat=True)))
print("Films in DB:", list(Film.objects.values_list("film_id", "title")))
print("Watchlist entries:", WatchlistEntry.objects.count())

res = services.compare_users(["alice", "bob"])
print("compare_users result:", res)
