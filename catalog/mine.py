"""Whose courses: narrowing the catalogue to what one person chose.

A signed-in person picks the courses they are taking (accounts.models.Enrollment); the
dashboard, the list in the navigation and Next up then show those and nothing else. It is
a matter of what is put in front of them, not of permission: any course can still be
opened by its address or found by searching.

Where the site runs open, with nobody signed in, there is nothing to choose and every
course counts as theirs.
"""

from accounts.models import Enrollment


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
