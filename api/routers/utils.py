import bcrypt
from datetime import datetime, timedelta
import jwt  # Assurez-vous que c'est PyJWT qui est importé
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from database import get_db_connection

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

SECRET_KEY = "FAKERLEBOSS"

def get_password_hash(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def generate_new_user_id(db):
    cursor = db.execute("SELECT MAX(user_id) FROM appmovieschema.User_Table")
    result = cursor.fetchone()
    if result:
        max_id = result[0]
    else:
        max_id = None
    return max_id + 1 if max_id else 1

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db_connection)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.execute("SELECT user_id, pseudo, email FROM appmovieschema.User_Table WHERE email = ?", (email,)).fetchone()
    if user is None:
        raise credentials_exception
    return {"user_id": user.user_id, "email": user.email, "pseudo": user.pseudo}

def get_user_favorite_movies(user_id: int, db: Session):
    query = """
    SELECT m.title
    FROM appmovieschema.UserMovieList_Table uml
    JOIN appmovieschema.Movie_Table m ON uml.movie_id = m.movie_id
    WHERE uml.user_id = ?
    """
    result = db.execute(query, (user_id,)).fetchall()
    return [row.title for row in result]
