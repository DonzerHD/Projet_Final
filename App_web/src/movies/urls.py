from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.search_movies, name='search_movies'),
    path('add_favorite/<int:movie_id>/', views.add_favorite_movie, name='add_favorite_movie'),
    path('recommend/', views.recommend_movies, name='recommend_movies'),
]
