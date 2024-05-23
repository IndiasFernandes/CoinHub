from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views import View

# Mixin for setting the current section in context
class CurrentSectionMixin:
    current_section = 'accounts'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_section'] = self.current_section
        context['show_sidebar'] = False  # Sidebar not shown for account views
        return context

class LoginView(CurrentSectionMixin, View):
    def get(self, request):
        return render(request, 'pages/accounts/login.html', {
            'section': 'login',
            'current_section': 'accounts',
            'show_sidebar': False
        })

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You are now logged in.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
        return render(request, 'pages/accounts/login.html', {
            'section': 'login',
            'current_section': 'accounts',
            'show_sidebar': False
        })

class LogoutView(View):
    @login_required
    def get(self, request):
        logout(request)
        messages.info(request, 'You have been logged out.')
        return redirect('accounts:login')

class RegisterView(CurrentSectionMixin, View):
    def get(self, request):
        form = UserCreationForm()
        return render(request, 'pages/accounts/register.html', {
            'form': form,
            'section': 'register',
            'current_section': 'accounts',
            'show_sidebar': False
        })

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful.')
            return redirect('dashboard')
        return render(request, 'pages/accounts/register.html', {
            'form': form,
            'section': 'register',
            'current_section': 'accounts',
            'show_sidebar': False
        })
