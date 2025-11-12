from django.http import JsonResponse
from .utils import validate_usernames, fetch_watchlist, watchlist_parser, compare_watchlists

def compare_view(request):
    usernames = request.GET.getlist('usernames')
    if len(usernames) < 2:
        return JsonResponse({'error': 'Please provide at least two usernames.'}, status=400)
    
    valid_usernames, invalid_usernames = validate_usernames(usernames)
    if not valid_usernames:
        return JsonResponse({'error': 'No valid usernames found'}, status=400)
    if invalid_usernames:
        return JsonResponse({
            'error': 'Some usernames are invalid.',
            'invalid_usernames': invalid_usernames
        }, status=400)
    
    urls = fetch_watchlist(valid_usernames)

    user_watchlists = {}
    for username, url in zip(usernames, urls):
        data = watchlist_parser(url)
        user_watchlists[username] = set(data['id'])

    common_films = compare_watchlists(user_watchlists)
    
    return JsonResponse({
        'valid_usernames': valid_usernames,
        'common_films': list(common_films)
    })
