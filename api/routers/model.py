from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import pandas as pd
import pickle
from database import get_db_connection
from .utils import get_user_favorite_movies, get_current_user, oauth2_scheme

router = APIRouter()

# Charger le modèle sauvegardé (modèle de recommandation de films)
with open("movie_recommendation_model.pkl", "rb") as f:
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
    
    recommended_movies = []
    for _, row in recommendations.iterrows():
        movie_info = db.execute(
            "SELECT movie_id, title, release_date, poster_link FROM appmovieschema.Movie_Table WHERE title = ?",
            (row['title'],)
        ).fetchone()
        if movie_info:
            recommended_movies.append({
                "movie_id": movie_info.movie_id,
                "title": movie_info.title,
                "release_date": movie_info.release_date,
                "poster_link": movie_info.poster_link
            })
    
    return recommended_movies
