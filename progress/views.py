import json

from django.contrib.auth.decorators import login_not_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .sync import sync


# Opted out of the site-wide login requirement on purpose: that would answer an expired
# session with a redirect to an HTML page. A script needs a plain "401" it can act on.
@login_not_required
@require_POST
def sync_view(request):
    """The one endpoint the browser's progress store talks to. JSON in, JSON out.

    It is a POST from the site's own pages, so Django's CSRF check applies as it does to a
    form: the script sends the token in the X-CSRFToken header.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "signed out"}, status=401)
    try:
        payload = json.loads(request.body)
    except ValueError:
        payload = None
    if not isinstance(payload, dict):
        return JsonResponse({"error": "expected a JSON object"}, status=400)
    return JsonResponse(sync(request.user, payload))
