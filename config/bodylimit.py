"""A ceiling on how large a request may be, applied before anything reads it.

Django already refuses form data above DATA_UPLOAD_MAX_MEMORY_SIZE, but that number does
not count uploaded files: those are written to a temporary folder as they arrive, however
large. And they arrive early. The CSRF check reads the form to find its token, which
parses the whole body, files included, before the site has asked who is sending it. So
without this, anyone could have the server store an upload of any size on any address.

One page takes a file: the hand-in of a course by its educator. Everything else is a
small form or a little JSON. So:

    a request larger than DATA_UPLOAD_MAX_MEMORY_SIZE is refused with 413 ...
    ... unless its path is listed in settings.BODY_LIMITS and the sender is signed in

The size is the one the sender declares in Content-Length. That is enough: the server in
front (gunicorn) hands Django exactly that many bytes, and a request without the header
is read as empty.
"""

import logging

from django.conf import settings
from django.http import HttpResponse, JsonResponse

logger = logging.getLogger(__name__)


def declared(request):
    """The size of the body in bytes, as Content-Length says. Nonsense counts as none."""
    try:
        return max(int(request.META.get("CONTENT_LENGTH") or 0), 0)
    except ValueError:
        return 0


def allowed(request):
    """How many bytes this request may carry."""
    for prefix, limit in settings.BODY_LIMITS:
        # Only for someone the site knows. A visitor gets the small limit everywhere, so
        # the pages that take files cannot be used to fill the disk from outside.
        if request.path.startswith(prefix) and request.user.is_authenticated:
            return limit
    return settings.DATA_UPLOAD_MAX_MEMORY_SIZE


class BodyLimitMiddleware:
    """Runs after AuthenticationMiddleware (it needs request.user) and before the views.

    It has to answer in __call__. The CSRF check that reads the body is a `process_view`
    hook, and those run later, once every middleware has let the request through.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        size = declared(request)
        # Nearly every request is small: the comparison below is all it costs them, and
        # request.user (a database query the first time) is not touched.
        if size > settings.DATA_UPLOAD_MAX_MEMORY_SIZE:
            limit = allowed(request)
            if size > limit:
                return self.refuse(request, limit)
        return self.get_response(request)

    @staticmethod
    def refuse(request, limit):
        logger.warning("Request body over the limit refused on %s", request.path)
        megabytes = max(limit // (1024 * 1024), 1)
        if request.path.startswith("/api/"):
            return JsonResponse({"error": "request too large"}, status=413)
        return HttpResponse(
            f"That is more than this page accepts ({megabytes} MB at most).",
            status=413,
            content_type="text/plain; charset=utf-8",
        )
