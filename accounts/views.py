"""
-- AMW Django ERP - Accounts Views --

Authentication views: login, logout

Security:
- CSRF protection enabled on all forms
- POST-only logout to prevent CSRF attacks
- Open redirect protection using Django's built-in validator
"""

# -- Standard Library --

# -- Third-Party (Django) --
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods

# -- Local Imports --


@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    Employee login view.

    GET: Display login form
    POST: Authenticate and log in

    Security:
    - Validates 'next' parameter using Django's url_has_allowed_host_and_scheme
    - Uses CSRF protection
    - Generic error messages to prevent user enumeration
    """
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    error_message = None

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        next_url = request.POST.get("next", request.GET.get("next", ""))

        # Validate next URL using Django's built-in validator
        # This prevents open redirect attacks
        if next_url and not url_has_allowed_host_and_scheme(
            url=next_url, allowed_hosts={request.get_host()}, require_https=False
        ):
            next_url = ""

        if email and password:
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                # Safe redirect after login
                redirect_to = next_url if next_url else "accounts:dashboard"
                return redirect(redirect_to)
            else:
                # Generic error message (doesn't reveal if user exists)
                error_message = "Invalid email or password"
        else:
            error_message = "Please provide both email and password"

    # Preserve next parameter for GET requests
    next_url = request.GET.get("next", "")

    return render(request, "accounts/pages/login.html", {"error_message": error_message, "next": next_url})


@login_required
@require_http_methods(["POST"])
def logout_view(request):
    """
    Employee logout view.

    POST: Log out and redirect to login page

    Security:
    - POST-only to prevent CSRF attacks
    - Uses namespaced URL for login redirect
    """
    logout(request)
    return redirect("accounts:login")


@login_required
def dashboard_view(request):
    """
    Simple dashboard view - requires authentication.

    Template: accounts/pages/dashboard.html (centralized in templates/)
    """
    return render(request, "accounts/pages/dashboard.html")
