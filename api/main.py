# main.py

from fastapi import FastAPI
from routers import user, model, movie  # Utiliser des imports absolus

app = FastAPI()

app.include_router(model.router)
app.include_router(user.router)
app.include_router(movie.router)  # Inclure le nouveau routeur

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
