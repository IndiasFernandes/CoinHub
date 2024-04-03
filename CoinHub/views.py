from django.shortcuts import render

def main_view(request):
    """View function for the main dashboard page."""
    return render(request, 'main.html')