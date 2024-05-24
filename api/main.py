from fastapi import FastAPI
from routers import user, model, movie  # Ajoutez le module movie

app = FastAPI()

app.include_router(model.router)
app.include_router(user.router)
app.include_router(movie.router)  # Inclure le nouveau routeur
