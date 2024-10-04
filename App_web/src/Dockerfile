# Dockerfile for Django using Gunicorn for production

FROM python:3.11-slim

WORKDIR /app

# Copier les dépendances
COPY requirements.txt requirements.txt

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste de l'application
COPY . .

# Exposer le port 8000 (ou 80 si tu préfères)
EXPOSE 8000

# Commande pour lancer l'application Django avec Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app_web.wsgi:application"]
