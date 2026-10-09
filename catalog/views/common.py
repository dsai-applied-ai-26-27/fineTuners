from django.conf import settings
from django.shortcuts import get_object_or_404

from ingest.discover import find_course, newest_mtime

from ..models import Course
from ..nav import course_data


def load_course(slug, active=""):
    """Fetch a course (404 if unknown) plus the context every page inside it shares.

    `active` is the key of the navigation entry to highlight."""
    course = get_object_or_404(Course, slug=slug)
    data = course_data(course)
    context = {
        "course": course,
        "hue": course.hue,
        "nav": data["nav"],
        "counts": data["counts"],
        "manifest": data["manifest"],
        "active": active,
        "stale": _files_changed(course),
    }
    return course, context


def _files_changed(course):
    """Development aid: true when the course's files are newer than the last sync."""
    if not settings.DEBUG or course.synced_at is None:
        return False
    folder = find_course(course.slug, settings.CONTENT_ROOTS)
    return folder is not None and newest_mtime(folder) > course.synced_at.timestamp() + 1


def scope_topics(request, course):
    """Topics selected by ?scope=<exam> or ?topic=<id>, with a label; (None, "") when absent.

    Lets one page (cards, formulas, hooks…) be narrowed to what an exam covers."""
    scope, topic = request.GET.get("scope"), request.GET.get("topic")
    if scope:
        assessment = get_object_or_404(course.assessments, slug=scope)
        return list(assessment.topics.all()), assessment.title
    if topic:
        found = get_object_or_404(course.topics, key=topic)
        return [found], found.title
    return None, ""
