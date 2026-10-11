"""Which courses a visitor is shown.

Two narrowings, applied in this order:

    catalogue(request)   every course there is to see: one per series (its latest year),
                         without those the owner has not opened yet (desk.switches)
    mine(request, ...)   of those, the ones this person chose for their dashboard
                         (accounts.Enrollment)

Choosing is about what is put in front of someone, not about permission: a course that
was not chosen can still be opened by its address or found by searching. A course that is
not open cannot.

Where the site runs open, with nobody signed in, there is nothing to choose and every open
course counts as theirs.
"""

from accounts.models import Enrollment
from desk.switches import switches

from . import editions
from .models import Course


def catalogue(request):
    """The open courses, latest year of each, in the usual order.

    The view and the navigation both start from this list while one page is built, so it
    is kept on the request: the courses are read from the database once.
    """
    if not hasattr(request, "_catalogue"):
        gate = switches(request)
        latest = editions.latest(list(Course.objects.all()))
        request._catalogue = [course for course in latest if gate.is_open(course)]
    return request._catalogue


def chosen(request):
    """The series this visitor chose, as a set; None when nobody is signed in.

    Asked for more than once while one page is built (the view, then the navigation), so
    the answer is kept on the request and the database is asked once.
    """
    if not request.user.is_authenticated:
        return None
    if not hasattr(request, "_chosen_series"):
        request._chosen_series = Enrollment.objects.series_of(request.user)
    return request._chosen_series


def mine(request, courses):
    """Those of `courses` that are on this visitor's dashboard, in the same order."""
    picked = chosen(request)
    if picked is None:
        return list(courses)
    return [course for course in courses if course.series in picked]
