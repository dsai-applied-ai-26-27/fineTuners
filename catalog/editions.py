"""The same course in different academic years.

One `Course` row is one year of teaching: its own folder, its own content, its own
progress. Rows that share `series` are editions of one course (MLPR 2025/26 and, once it
is written, MLPR 2026/27). This module answers the two questions pages ask about that, so
no view or template works it out for itself:

    latest(courses)   one course per series, the most recent year   dashboard, navigation
    of(course)        every year of this course, newest first        the switch on its page

A new year is a new folder whose course.yaml names the `series`; nothing here changes.
"""

from .models import Course


def _series(course):
    # `series` is filled in by sync_content. A row from before that, or one built by hand
    # in a test, stands for itself.
    return course.series or course.slug


def _recency(course):
    # Years are written "2025-26", so comparing them as text puts them in order, and a
    # course without a year counts as the oldest. The slug only breaks ties.
    return (course.year, course.slug)


def latest(courses):
    """Keep one course per series, the one of the most recent year. Order is preserved."""
    newest = {}
    for course in courses:
        best = newest.get(_series(course))
        if best is None or _recency(course) > _recency(best):
            newest[_series(course)] = course
    return [course for course in courses if newest[_series(course)] is course]


def of(course):
    """Every edition of `course`'s series, newest first. Always includes `course` itself."""
    if not course.series:
        return [course]
    return sorted(Course.objects.filter(series=course.series), key=_recency, reverse=True)
