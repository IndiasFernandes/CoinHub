from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return render(request, 'pages/general/dashboard.html')
        else:
            # Return an 'invalid login' error message.
            return render(request, 'pages/accounts/login.html', {'error': 'Invalid username or password.'})
    else:
        return render(request, 'pages/accounts/login.html')

def logout_view(request):
    logout(request)
    return render(request, 'pages/accounts/login.html')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # log the user in
            return render(request, 'pages/accounts/login.html')
    else:
        form = UserCreationForm()
    return render(request, 'pages/accounts/register.html', {'form': form})
