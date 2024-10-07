from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.search_movies, name='search_movies'),
    path('add_favorite/<int:movie_id>/', views.add_favorite_movie, name='add_favorite_movie'),
    path('recommend/', views.recommend_movies, name='recommend_movies'),
    path('favorites/', views.favorite_movies, name='favorite_movies'),
    path('remove_favorite/<int:movie_id>/', views.remove_favorite_movie, name='remove_favorite_movie'),
    path('generate-scenario/', views.generate_movie_scenario, name='generate_movie_scenario'),
]
