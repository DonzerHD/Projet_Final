from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db_connection
from .utils import get_current_user, oauth2_scheme

router = APIRouter()

@router.post("/movies/add_favorite/{movie_id}")
def add_favorite_movie(movie_id: int, db: Session = Depends(get_db_connection), token: str = Depends(oauth2_scheme)):
    current_user = get_current_user(token, db)
    user_id = current_user['user_id']

    # Vérifier si le film existe dans la table des films
    movie = db.execute("SELECT * FROM appmovieschema.Movie_Table WHERE movie_id = ?", (movie_id,)).fetchone()
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")

    # Ajouter le film à la liste des favoris de l'utilisateur
    db.execute(
        "INSERT INTO appmovieschema.UserMovieList_Table (user_id, movie_id) VALUES (?, ?)",
        (user_id, movie_id)
    )
    db.commit()

    return {"message": "Movie added to favorites"}

# Pour obtenir les films favoris de l'utilisateur
@router.get("/movies/favorites")
def get_favorite_movies(db: Session = Depends(get_db_connection), token: str = Depends(oauth2_scheme)):
    current_user = get_current_user(token, db)
    user_id = current_user['user_id']

    # Récupérer les films favoris de l'utilisateur
    query = """
    SELECT m.movie_id, m.title, m.release_date, m.poster_link
    FROM appmovieschema.UserMovieList_Table uml
    JOIN appmovieschema.Movie_Table m ON uml.movie_id = m.movie_id
    WHERE uml.user_id = ?
    """
    favorite_movies = db.execute(query, (user_id,)).fetchall()
    
    return [{"movie_id": row.movie_id, "title": row.title, "release_date": row.release_date, "poster_link": row.poster_link} for row in favorite_movies]


@router.get("/movies/search")
def search_movies(query: str, db: Session = Depends(get_db_connection)):
    search_query = f"%{query.lower()}%"  # Préparez la chaîne de recherche pour une correspondance partielle et insensible à la casse
    
    result = db.execute(
        """
        SELECT movie_id, title, release_date, poster_link 
        FROM appmovieschema.Movie_Table 
        WHERE LOWER(title) LIKE ?
        """,
        (search_query,)
    ).fetchall()
    
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No movies found matching the query")

    return [{"movie_id": row.movie_id, "title": row.title, "release_date": row.release_date, "poster_link": row.poster_link} for row in result]
