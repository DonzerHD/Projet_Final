# api/routers/model.py
import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import pandas as pd
import pickle
from api.database import get_db_connection
from api.routers.utils import get_user_favorite_movies, get_current_user, oauth2_scheme

router = APIRouter()

# Définir le chemin absolu du fichier de modèle
model_file_path = os.path.join(os.path.dirname(__file__), '..', 'movie_recommendation_model.pkl')

# Charger le modèle sauvegardé (modèle de recommandation de films)
with open(model_file_path, "rb") as f:
    model_data = pickle.load(f)

# Extraire les données du modèle
movies = model_data["movies"]
cosine_sim = model_data["cosine_sim"]

# Fonction pour obtenir les recommandations de films
def get_recommendations(favorite_movie_titles, cosine_sim=cosine_sim, top_n=3):
    favorite_indices = [movies[movies['title'] == title].index[0] for title in favorite_movie_titles]
    sim_scores = cosine_sim[favorite_indices].mean(axis=0)
    sim_scores = list(enumerate(sim_scores))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    movie_indices = [i[0] for i in sim_scores if i[0] not in favorite_indices][:top_n]
    return movies.iloc[movie_indices]

# Définir une route pour l'API qui recommande des films en fonction des films préférés de l'utilisateur
@router.get("/recommend/{user_id}")
def recommend(user_id: int, db: Session = Depends(get_db_connection), token: str = Depends(oauth2_scheme)):
    current_user = get_current_user(token, db)
    if current_user['user_id'] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view recommendations for this user")
    
    favorite_movie_titles = get_user_favorite_movies(user_id, db)
    recommendations = get_recommendations(favorite_movie_titles)
    
    # Récupérer les détails des films recommandés
    movie_ids = [movie_id for movie_id in recommendations['movie_id']]
    movie_details = db.execute(
        "SELECT movie_id, title, release_date, poster_link FROM appmovieschema.Movie_Table WHERE movie_id IN ({})".format(','.join('?' * len(movie_ids))),
        movie_ids
    ).fetchall()
    
    return [{"movie_id": row.movie_id, "title": row.title, "release_date": row.release_date, "poster_link": row.poster_link} for row in movie_details]
