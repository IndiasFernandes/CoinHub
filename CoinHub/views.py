from django.shortcuts import render

def main_view(request):
    """View function for the main dashboard page."""
    return render(request, 'main.html')

# add bot view


def login_view(request):
    # Your existing login logic...
    return render(request, 'pages/accounts/login.html', {'section': 'accounts'})

def profile_view(request):
    # Your existing profile logic...
    return render(request, 'pages/accounts/profile.html', {'section': 'accounts'})

def register_view(request):
    # Your existing register logic...
    return render(request, 'pages/accounts/register.html', {'section': 'accounts'})
