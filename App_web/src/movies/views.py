from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import requests

API_BASE_URL = "http://127.0.0.1:8000"  # URL de base de l'API FastAPI

import jwt

SECRET_KEY = "FAKERLEBOSS"

def get_user_id_from_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        return user_id
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    
def search_movies(request):
    if 'token' not in request.session:
        return redirect('login')
    
    query = request.GET.get('query')
    movies = []
    if query:
        token = request.session.get('token')
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{API_BASE_URL}/movies/search", params={'query': query}, headers=headers)
        if response.status_code == 200:
            movies = response.json()
    return render(request, 'movies/search.html', {'movies': movies, 'query': query})

def add_favorite_movie(request, movie_id):
    if 'token' not in request.session:
        return redirect('login')
    
    token = request.session.get('token')
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(f"{API_BASE_URL}/movies/add_favorite/{movie_id}", headers=headers)
    if response.status_code == 200:
        return redirect(request.META.get('HTTP_REFERER', 'search_movies'))
    else:
        return render(request, 'movies/search.html', {'error': 'Could not add movie to favorites.'})
    
API_BASE_URL = "http://127.0.0.1:8000"  # URL de base de l'API FastAPI

def recommend_movies(request):
    if 'token' not in request.session:
        return redirect('login')
    
    token = request.session.get('token')
    user_id = get_user_id_from_token(token)  # Utilisez la fonction pour obtenir l'ID utilisateur
    
    if user_id is None:
        return redirect('login')  # Redirigez vers la page de connexion si le token est invalide
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f"{API_BASE_URL}/recommend/{user_id}", headers=headers)
    
    if response.status_code == 200:
        recommendations = response.json()
    else:
        recommendations = []
    
    return render(request, 'movies/recommend.html', {'recommendations': recommendations})
