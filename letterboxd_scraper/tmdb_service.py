import requests
from django.conf import settings

TMDB_BASE = "https://api.themoviedb.org/3"

_GENRE_CACHE = {
    "movie": None,
    "tv": None,
}

MAX_PAGES = 3

# ---------- HELPERS ----------

def normalize_title(title):
    return title.strip().lower()

def year_matches(date_str, target_year, tolerance=1):
    if not date_str or target_year is None:
        return False
    
    try:
        item_year = int(date_str.split("-")[0])
        return abs(item_year - int(target_year)) <= tolerance
    except ValueError:
        return False

# ---------- SEARCH ----------

def _search_single_media(media_type, title, year):
    """
    media_type: 'movie' or 'tv'
    Returns best exact-title match or None
    """

    params = {
        "api_key": settings.TMDB_API_KEY,
        "query": title,
        "year": year,
    }

    title_norm = normalize_title(title)
    candidates = []

    for page in range(1, MAX_PAGES + 1):
        params["page"] = page

        resp = requests.get(
            f"{TMDB_BASE}/search/{media_type}",
            params=params,
            timeout=10
        )
        results = resp.json().get("results", [])

        if not results:
            break

        for item in results:
            item_title = (
                item.get("title") if media_type == "movie"
                else item.get("name")
            )
            if not item_title:
                continue

            if normalize_title(item_title) != title_norm:
                continue

            date_field = (
                item.get("release_date") if media_type == "movie"
                else item.get("first_air_date")
            )
            if not year_matches(date_field, year):
                continue

            if not item.get("poster_path"):
                continue

            candidates.append({
                **item,
                "media_type": media_type
            })
    
    if not candidates:
        return None
    
    if len(candidates) >= 2:
        if candidates[0]["vote_count"] > candidates[1]["vote_count"] * 5:
            return candidates[0]

    candidates.sort(
        key=lambda x: (
            x.get("vote_count", 0),
            x.get("vote_average", 0),
        ),
        reverse=True
    )

    return candidates[0]


def search_tmdb(title, year=None):
    """
    Movie-first TMDB search with TV fallback.
    Returns matched item dict with media_type or None.
    """

    movie = _search_single_media("movie", title, year)
    if movie:
        return movie

    tv = _search_single_media("tv", title, year)
    if tv:
        return tv
    
    return None

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
