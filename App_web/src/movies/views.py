from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import requests

API_BASE_URL = "https://4c4d-2a01-cb0c-1096-a600-3638-47b5-4624-2e02.ngrok-free.app/"  # URL de base de l'API FastAPI

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
    token = request.session.get('token')
    headers = {'Authorization': f'Bearer {token}'}
    
    if query:
        response = requests.get(f"{API_BASE_URL}/movies/search", params={'query': query}, headers=headers)
    else:
        response = requests.get(f"{API_BASE_URL}/movies/random", headers=headers)
    
    if response.status_code == 200:
        movies = response.json()
    
    # Récupérer les films favoris de l'utilisateur
    favorite_movies = get_user_favorite_movies_from_api(token)
    favorite_movie_ids = [movie['movie_id'] for movie in favorite_movies]

    return render(request, 'movies/search.html', {'movies': movies, 'query': query, 'favorite_movie_ids': favorite_movie_ids})

def get_user_favorite_movies_from_api(token):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f"{API_BASE_URL}/movies/favorites", headers=headers)
    if response.status_code == 200:
        return response.json()
    return []

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


def favorite_movies(request):
    if 'token' not in request.session:
        return redirect('login')

    token = request.session.get('token')
    headers = {'Authorization': f'Bearer {token}'}
    
    response = requests.get(f"{API_BASE_URL}/movies/favorites", headers=headers)
    
    if response.status_code == 200:
        favorite_movies = response.json()
    else:
        favorite_movies = []
    
    return render(request, 'movies/favorites.html', {'favorite_movies': favorite_movies})

def remove_favorite_movie(request, movie_id):
    if 'token' not in request.session:
        return redirect('login')

    token = request.session.get('token')
    headers = {'Authorization': f'Bearer {token}'}
    
    response = requests.delete(f"{API_BASE_URL}/movies/remove_favorite/{movie_id}", headers=headers)
    
    return redirect('favorite_movies')