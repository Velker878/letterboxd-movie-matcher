from django.http import JsonResponse
from .services import compare_users
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

def home_view(request):
    return render(request, 'home.html')