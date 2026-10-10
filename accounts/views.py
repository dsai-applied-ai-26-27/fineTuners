"""The few account pages that are ours. Signing in and out is django-allauth's
(config/urls.py mounts it under /accounts/); the landing page is catalog.views.home."""

from django.conf import settings
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_not_required
from django.http import Http404
from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST


def safe_next(request):
    """Where to go after signing in: the ?next= address if it is on this site, else home.

    Without the check, a link to the sign-in page could bounce people to any website.
    """
    target = request.POST.get("next") or request.GET.get("next") or ""
    allowed = url_has_allowed_host_and_scheme(
        target, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    )
    return target if allowed else "catalog:home"


@login_not_required
@require_POST
def dev_login(request):
    """Sign in as a local test user, without Google. Development only.

    On a server DEBUG is off, and this answers "no such page" like any unknown address.
    """
    if not settings.DEBUG:
        raise Http404
    user, _ = get_user_model().objects.get_or_create(
        username="dev",
        defaults={"first_name": "Dev", "last_name": "User", "email": "dev@localhost"},
    )
    # Two authentication backends are configured, so login() must be told which one
    # vouches for this user.
    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    return redirect(safe_next(request))


@require_POST
def delete_account(request):
    """Delete the signed-in person and, by cascade, everything stored about them."""
    user = request.user
    logout(request)
    user.delete()
    return redirect("catalog:home")
