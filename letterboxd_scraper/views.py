from django.http import JsonResponse
from .services import compare_users
from .utils import validate_usernames
from django.views.decorators.http import require_GET
from django.shortcuts import render

def compare_view(request):
    usernames = request.GET.getlist('usernames')
    if len(usernames) < 2:
        return JsonResponse({'error': 'Please provide at least two usernames.'}, status=400)
    
    result = compare_users(usernames)

    if 'error' in result and result['error'] == 'invalid_usernames':
        return JsonResponse(result, status=400)
    
    films = [
        {
            'id': film.letterboxd_slug,
            'title': film.title,
            'year': film.year,
            'poster_url': film.poster_image,
            'genres': film.genres,
            'letterboxd_url': f"https://letterboxd.com/film/{film.letterboxd_slug}/"
        }
        for film in result.get('common_films', [])
    ]

    return JsonResponse({
        'valid_users': result.get('valid_users', {}),
        'invalid_usernames': result.get('invalid_usernames', {}),
        'common_films': films,
    })


@require_GET
def validate_user_view(request):
    username = request.GET.get('username', '').strip()

    if not username:
        return JsonResponse({
            'username': username,
            'valid': False,
            'reason': 'empty'
        })

    validation = validate_usernames([username])
    
    if username in validation['valid']:
        return JsonResponse({
            'username': username,
            'valid': True,
            'reason': None,
            'pfp': validation['valid'][username]['pfp']
        })

    return JsonResponse({
        'username': username,
        'valid': False,
        'reason': validation['invalid'].get(username)
    })

def home_view(request):
    return render(request, 'home.html')