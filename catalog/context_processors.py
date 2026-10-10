from django.conf import settings
from django.utils.functional import SimpleLazyObject

from . import editions
from .models import Course


def site(request):
    """Variables every template gets. `nav_courses` is lazy: the function inside runs,
    and the database is asked, only if a template actually uses the list. Pages inside
    a course replace that part of the navigation and never do."""

    def current():
        # Of a course taught in several years only the latest is listed, and only
        # while that one is active.
        active = Course.Status.ACTIVE
        return [c for c in editions.latest(list(Course.objects.all())) if c.status == active]

    return {
        "nav_courses": SimpleLazyObject(current),
        "debug": settings.DEBUG,
    }
