"""The news page, and the address the browser tells when it has shown the tour or the news."""

from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .. import news
from ..welcome import mark_seen, toured_at


def whats_new(request):
    """Every update, newest first. For someone signed in, those that came after their
    tour are marked: that is what changed since they were shown around."""
    toured = toured_at(request.user)
    updates = [
        {"update": update, "fresh": toured is not None and update.number > toured}
        for update in news.UPDATES
    ]
    return render(
        request,
        "catalog/whats_new.html",
        {"updates": updates, "any_fresh": any(row["fresh"] for row in updates), "active": "news"},
    )


@require_POST
def seen(request):
    """Posted by the tour and by the news dialog the moment they open (static/js/seen.js).

    A POST, not something the page does while it is being built: showing a page must not
    change anything, or a browser that fetches pages ahead of time would mark the tour as
    seen for someone who never saw it.
    """
    what = request.POST.get("what")
    if what not in ("tour", "news"):
        return HttpResponseBadRequest()
    try:
        upto = int(request.POST.get("upto", ""))
    except ValueError:
        return HttpResponseBadRequest()
    if request.user.is_authenticated:  # the open site has nobody to remember it for
        mark_seen(request.user, what, upto)
    return HttpResponse(status=204)  # 204: done, and there is nothing to send back
