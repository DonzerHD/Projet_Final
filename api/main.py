# main.py

from fastapi import FastAPI
from api.routers import user, model, movie  # Utiliser des imports absolus

app = FastAPI()

app.include_router(model.router)
app.include_router(user.router)
app.include_router(movie.router)  # Inclure le nouveau routeur
