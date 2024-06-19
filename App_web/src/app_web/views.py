from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import requests

API_BASE_URL = "http://127.0.0.1:8000"  # URL de base de l'API FastAPI

def home(request):
    return render(request, 'home.html')

def login_view(request):
    if request.method == 'POST':
        pseudo = request.POST['pseudo']
        password = request.POST['password']
        response = requests.post(f"{API_BASE_URL}/users/login", json={"pseudo": pseudo, "password": password})
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            request.session['token'] = token  # Stocker le token dans la session
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    
    return render(request, 'login.html')

def create_user(request):
    if request.method == 'POST':
        pseudo = request.POST['pseudo']
        email = request.POST['email']
        password = request.POST['password']
        
        response = requests.post(f"{API_BASE_URL}/users/create", json={"pseudo": pseudo, "email": email, "password": password})
        
        if response.status_code == 200:
            login_response = requests.post(f"{API_BASE_URL}/users/login", json={"pseudo": pseudo, "password": password})
            if login_response.status_code == 200:
                token = login_response.json().get("access_token")
                request.session['token'] = token  # Stocker le token dans la session
                return redirect('home')
            else:
                return render(request, 'login.html', {'error': 'Invalid credentials'})
        else:
            return render(request, 'create_user.html', {'error': 'Could not create user. Try again.'})
    
    return render(request, 'create_user.html')

def logout_view(request):
    if 'token' in request.session:
        del request.session['token']
    return redirect('login')
