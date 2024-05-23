# Importation des modules nécessaires
from fastapi import APIRouter, FastAPI
import pandas as pd
import pickle

#### TO DO FAIRE EN SORTE QUE SA TAPE DIRECTEMENT DANS LA BDD QUAND L'UTILISATEUR EST CONNECTER A FAIRE VENDREDI
router = APIRouter()

# Charger le modèle sauvegardé (modèle de recommandation de films)
with open("movie_recommendation_model.pkl", "rb") as f:
    model_data = pickle.load(f)

# Extraire les données du modèle
movies = model_data["movies"]  # Données sur les films
cosine_sim = model_data["cosine_sim"]  # Matrice de similarité cosinus entre les films

# Fonction pour obtenir les recommandations de films
def get_recommendations(favorite_movie_titles, cosine_sim=cosine_sim, top_n=10):
    # Obtenir les indices des films correspondant aux titres préférés
    favorite_indices = [movies[movies['title'] == title].index[0] for title in favorite_movie_titles]
    
    # Calculer les scores de similarité moyens avec tous les autres films
    sim_scores = cosine_sim[favorite_indices].mean(axis=0)
    
    # Trier les films en fonction des scores de similarité
    sim_scores = list(enumerate(sim_scores))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # Obtenir les indices des films les plus similaires (à l'exclusion des films déjà préférés)
    movie_indices = [i[0] for i in sim_scores if i[0] not in favorite_indices][:top_n]
    
    # Retourner les informations sur les films les plus similaires
    return movies.iloc[movie_indices]

# Définir une route pour l'API qui recommande des films
@router.get("/recommend")
def recommend(favorite_movies: str):
    # Séparer les titres des films préférés fournis en une liste
    favorite_movie_titles = favorite_movies.split(",")
    
    # Obtenir les recommandations de films en fonction des films préférés
    recommendations = get_recommendations(favorite_movie_titles)
    
    # Retourner les recommandations de films avec seulement les titres et les genres
    return recommendations[['title', 'genres']].to_dict(orient="records")