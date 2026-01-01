import requests
from django.conf import settings

TMDB_BASE = "https://api.themoviedb.org/3"

_GENRE_CACHE = {
    "movie": None,
    "tv": None,
}

# ---------- SEARCH ----------

def search_multi(title, year=None):
    """
    Search TMDB for both movies and TV shows.
    Returns the best matching result or None.
    """
    params = {
        "api_key": settings.TMDB_API_KEY,
        "query": title,
    }

    resp = requests.get(f"{TMDB_BASE}/search/multi", params=params, timeout=10)
    data = resp.json()
    results = data.get("results", [])

    if not results:
        return None
    
    candidates = [
        r for r in results
        if r.get("media_type") in ("movie", "tv")
    ]

    if not candidates:
        return None
    
    if year:
        target_year = int(year)

        for item in candidates:
            date_str = (
                item.get("release_date") or item.get("first_air_date")
            )
            if not date_str:
                continue

            try:
                item_year = int(date_str.split("-")[0])
            except ValueError:
                continue

            if abs(item_year - target_year) <= 1:
                return item
        
    
    #Fallback to first candidate if no match
    return candidates[0]
 

# ---------- POSTER ----------

def get_poster_url(poster_path, size="w342"):
    if not poster_path:
        return None
    return f"https://image.tmdb.org/t/p/{size}{poster_path}"

# ---------- GENRES ----------

def get_genre_map(media_type):
    """
    media_type: 'movie' or 'tv'
    """
    global _GENRE_CACHE

    if _GENRE_CACHE.get(media_type) is not None:
        return _GENRE_CACHE[media_type]

    resp = requests.get(
        f"{TMDB_BASE}/genre/{media_type}/list",
        params={"api_key": settings.TMDB_API_KEY},
        timeout=10
    )
    data = resp.json()

    genre_map = {g["id"]: g["name"] for g in data.get("genres", [])}
    _GENRE_CACHE[media_type] = genre_map
    return genre_map


def resolve_genres(genre_ids, media_type):
    genre_map = get_genre_map(media_type)
    return [genre_map[g] for g in genre_ids if g in genre_map]
