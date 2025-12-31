import requests
from django.conf import settings

TMDB_BASE = "https://api.themoviedb.org/3"

def search_movie(title, year=None):
    # Strict search
    params = {
        "api_key": settings.TMDB_API_KEY,
        "query": title,
    }
    if year:
        params["year"] = year

    resp = requests.get(f"{TMDB_BASE}/search/movie", params=params, timeout=10)
    data = resp.json()

    # If direct match is found
    if data.get("results"):
        return data["results"][0]

    # 2. Fallback search
    if year:
        params.pop("year")
        resp = requests.get(f"{TMDB_BASE}/search/movie", params=params, timeout=10)
        data = resp.json()
        
        if data.get("results"):
            target_year = int(year)
            for movie in data["results"][:3]:
                release_date = movie.get("release_date", "")
                if release_date:
                    movie_year = int(release_date.split("-")[0])
                    if abs(movie_year - target_year) <= 1:
                        return movie

    return None

def get_poster_url(poster_path, size="w342"):
    if not poster_path:
        return None
    return f"https://image.tmdb.org/t/p/{size}{poster_path}"

