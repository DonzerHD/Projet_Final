from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import requests

API_BASE_URL = "https://4c4d-2a01-cb0c-1096-a600-3638-47b5-4624-2e02.ngrok-free.app/"  # URL de base de l'API FastAPI

def home(request):
    token = request.session.get('token')
    print("Token in session:", token)  # Message de debug
    return render(request, 'home.html')


def login_view(request):
    if request.method == 'POST':
        pseudo = request.POST['pseudo']
        password = request.POST['password']
        response = requests.post(f"{API_BASE_URL}/users/login", json={"pseudo": pseudo, "password": password})
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            request.session['token'] = token  # Stocker le token dans la session
            print("Token:", token)  # Message de debug
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
