from django.conf import settings

from .models import Course


def site(request):
    """Variables every template gets. Querysets are lazy: nothing hits the database
    unless a template actually loops over `nav_courses`."""
    return {
        "nav_courses": Course.objects.filter(status=Course.Status.ACTIVE),
        "debug": settings.DEBUG,
    }
