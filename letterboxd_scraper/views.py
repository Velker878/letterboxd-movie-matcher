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
            'title': film.title,
            'link': film.link,
            'poster_image': film.poster_image,
            'genres': film.genres,
        }
        for film in result.get('common_films', [])
    ]

    return JsonResponse({
        'valid_usernames': result.get('valid_usernames', []),
        'invalid_usernames': result.get('invalid_usernames', []),
        'common_films': films,
    })


@require_GET
def validate_user_view(request):
    username = request.GET.get('username', '').strip()

    if not username:
        return JsonResponse({
            'valid': False,
            'username': username
        })

    valid_usernames, invalid_usernames = validate_usernames([username])

    return JsonResponse({
        'username': username,
        'valid': username in valid_usernames,
        'reason': None if username in valid_usernames else 'not_found'
    })

def home_view(request):
    return render(request, 'home.html')