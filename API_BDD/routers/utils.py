import bcrypt
from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from ..database import get_db_connection  # Assurez-vous que ce chemin d'importation est correct

# Le chemin vers l'endpoint de connexion pour obtenir un nouveau jeton
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")


# Exception de validation des credentials
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
    result = cursor.fetchone()  # Récupère la première ligne du résultat
    if result:
        max_id = result[0]  # La première colonne de la ligne
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
        expire = datetime.utcnow() + timedelta(minutes=15)  # La durée de vie du token
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
    return {"user_id": user.user_id, "email": user.email, "pseudo": user.pseudo}  # Assurez-vous que les noms des champs correspondent à ceux de votre DB