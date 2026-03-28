"""
-- AMW Django ERP - Accounts Views --

Authentication views: login, logout
"""

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    Employee login view.
    
    GET: Display login form
    POST: Authenticate and log in
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    error_message = None
    
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if email and password:
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                next_url = request.POST.get('next', request.GET.get('next', 'dashboard'))
                return redirect(next_url)
            else:
                error_message = "Invalid email or password"
        else:
            error_message = "Please provide both email and password"
    
    return render(request, 'accounts/login.html', {'error_message': error_message})


@login_required
@require_http_methods(["POST"])
def logout_view(request):
    """
    Employee logout view.
    
    POST: Log out and redirect to login page
    """
    logout(request)
    return redirect('login')


@login_required
def dashboard_view(request):
    """
    Simple dashboard view - requires authentication.
    """
    return render(request, 'accounts/dashboard.html')
