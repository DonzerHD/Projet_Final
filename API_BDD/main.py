# main.py
from fastapi import FastAPI
from routers import user
from routers import model

app = FastAPI()

app.include_router(model.router)
app.include_router(user.router)
