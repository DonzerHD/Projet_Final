# routers/user.py
from fastapi import APIRouter, Depends, HTTPException, Body , status
from sqlalchemy.orm import Session
from database import get_db_connection
from .utils import generate_new_user_id , get_password_hash , verify_password, create_access_token, get_current_user
from jose import JWTError
from fastapi.security import OAuth2PasswordBearer 
from typing import Optional

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/users/create")
def create_user(pseudo: str = Body(...), email: str = Body(...), password: str = Body(...), db: Session = Depends(get_db_connection)):
    # Vérifier l'unicité du pseudo et de l'email
    existing_user = db.execute(
        "SELECT * FROM appmovieschema.User_Table WHERE pseudo = ? OR email = ?",
        (pseudo, email)
    ).fetchone()
    
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email already exists")
    
    # Générer un nouvel ID utilisateur et hacher le mot de passe
    new_id = generate_new_user_id(db)
    hashed_password = get_password_hash(password)

    # Insérer le nouvel utilisateur dans la base de données
    db.execute(
        "INSERT INTO appmovieschema.User_Table (user_id, pseudo, email, password) VALUES (?, ?, ?, ?)",
        (new_id, pseudo, email, hashed_password)
    )
    db.commit()

    # Retourner les informations de l'utilisateur, sauf le mot de passe
    return {"user_id": new_id, "pseudo": pseudo, "email": email}

@router.post("/users/login")
def login_for_access_token(pseudo: str = Body(...), password: str = Body(...), db: Session = Depends(get_db_connection)):
    # Vérifier que l'utilisateur existe et que le mot de passe est correct
    user = db.execute(
        "SELECT * FROM appmovieschema.User_Table WHERE pseudo = ?",
        (pseudo,)
    ).fetchone()
    if not user or not verify_password(password, user.password):  # Utilisez 'user.password' si la colonne dans la DB s'appelle 'password'
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    # Créer un token d'accès JWT pour l'utilisateur
    access_token = create_access_token(data={"sub": user.email})
    
    # Retourner le token d'accès
    return {"access_token": access_token, "token_type": "bearer"}

@router.put("/users/update/{user_id}")
def update_user(
    user_id: int,
    email: Optional[str] = Body(None),
    pseudo: Optional[str] = Body(None),
    password: Optional[str] = Body(None),
    db: Session = Depends(get_db_connection),
    token: str = Depends(oauth2_scheme)
):
    current_user = get_current_user(token, db)
    if current_user['user_id'] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this user")
    
    # Vérifiez si current_user est un dictionnaire ou convertissez-le si nécessaire
    if isinstance(current_user, dict):
        current_user_id = current_user.get('user_id')
    else:
        current_user_id = current_user.user_id  # ou current_user[0] si user_id est la première colonne

    if current_user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this user")

    # Construire dynamiquement la requête de mise à jour en fonction des valeurs fournies
    update_data = {}
    if pseudo:
        update_data['pseudo'] = pseudo
    if email:
        update_data['email'] = email
    if password:
        update_data['password'] = get_password_hash(password)

    # Générez les composants de la déclaration SQL de mise à jour en fonction des champs qui ne sont pas None
    set_clauses = ", ".join([f"{key} = ?" for key in update_data.keys()])
    values = list(update_data.values())
    values.append(user_id)

    update_stmt = f"UPDATE appmovieschema.User_Table SET {set_clauses} WHERE user_id = ?"
    db.execute(update_stmt, values)
    db.commit()

    return {"message": "User updated successfully."}
