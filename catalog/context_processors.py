from django.conf import settings
from django.utils.functional import SimpleLazyObject

from . import editions
from .mine import mine
from .models import Course
from .nav import has_content


def site(request):
    """Variables every template gets. `nav_courses` is lazy: the function inside runs,
    and the database is asked, only if a template actually uses the list. Pages inside
    a course replace that part of the navigation and never do."""

    def current():
        # The courses this person chose. Of a course taught in several years only the
        # latest is listed, only while that one is active, and only once there is
        # something in it to open.
        active = Course.Status.ACTIVE
        latest = mine(request, editions.latest(list(Course.objects.all())))
        return [c for c in latest if c.status == active and has_content(c)]

    return {
        "nav_courses": SimpleLazyObject(current),
        "debug": settings.DEBUG,
    }
