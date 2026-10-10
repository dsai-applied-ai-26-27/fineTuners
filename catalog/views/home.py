from itertools import groupby

from django.conf import settings
from django.contrib.auth.decorators import login_not_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

from .. import editions
from ..models import Card, Course, Document, Formula, Hook, Question, Term
from ..nav import course_data


def landing(request):
    """What a visitor sees before signing in: what the site is, and the way in.

    It is given nothing about the courses. The page says what the site is for, and the
    database is not asked anything on behalf of someone who has not signed in.
    """
    return render(
        request,
        "catalog/landing.html",
        {
            # Where they were heading; the sign-in sends them on afterwards.
            "next": request.GET.get("next", ""),
            "google": settings.GOOGLE_SIGN_IN,
            "dev_login": settings.DEBUG,
        },
    )


@login_not_required
def privacy(request):
    """What the site stores about a person. Public, so it can be read before signing in."""
    return render(request, "catalog/privacy.html", {"contact": settings.CONTACT_EMAIL})


def dashboard_groups(courses):
    """Sort courses into the sections of the dashboard.

    A course that names its semester sits with that semester, finished or not. One that
    does not falls back to its academic year, or to the Archived fold once it is finished.
    Sections with something still being studied come first, latest semester on top.
    """
    active = Course.Status.ACTIVE
    archived = [c for c in courses if c.semester is None and c.status != active]
    shown = [c for c in courses if c.semester is not None or c.status == active]

    def section(course):
        return (course.semester or 0, "" if course.semester else course.year)

    groups = []
    # groupby only joins neighbours, so the list is sorted by the same key first.
    for (semester, year), members in groupby(sorted(shown, key=section), key=section):
        members = sorted(members, key=lambda c: (c.order, c.title))
        years = sorted({c.year_label for c in members if c.year})
        groups.append(
            {
                "title": members[0].semester_label or members[0].year_label or "Courses",
                "note": " and ".join(years) if semester else "",
                "courses": members,
                "current": any(c.status == active for c in members),
                "rank": (semester, year),
            }
        )
    groups.sort(key=lambda g: g["rank"], reverse=True)  # latest first...
    groups.sort(key=lambda g: not g["current"])  # ...and finished sections after the rest
    return groups, archived


# `/` is two pages at one address: the landing page for a visitor, the dashboard for
# someone signed in. So the view itself must be reachable without a login, and decides.
@login_not_required
def home(request):
    if settings.REQUIRE_LOGIN and not request.user.is_authenticated:
        return landing(request)
    # One card per course: of a course taught in several years, the latest. Earlier
    # years are reached from the year switch on the course's own page.
    courses = editions.latest(list(Course.objects.all()))
    for course in courses:
        data = course_data(course)
        course.counts = data["counts"]
    groups, archived = dashboard_groups(courses)
    return render(
        request,
        "catalog/home.html",
        {
            "groups": groups,
            "archived": archived,
            "manifests": [course_data(c)["manifest"] for c in courses],
            "active": "home",
        },
    )


def _snippet(text, query, radius=70):
    position = text.lower().find(query.lower())
    if position < 0:
        return text[: radius * 2].strip()
    start, end = max(0, position - radius), min(len(text), position + len(query) + radius)
    return ("…" if start else "") + text[start:end].strip() + ("…" if end < len(text) else "")


def search(request):
    query = request.GET.get("q", "").strip()
    course_slug = request.GET.get("course", "")
    results = []
    if len(query) >= 2:
        scope = {"course__slug": course_slug} if course_slug else {}

        def found(model, *fields, related=()):
            condition = Q()
            for name in fields:
                # Q objects combine with | (OR) and & (AND) to build one WHERE clause.
                condition |= Q(**{f"{name}__icontains": query})
            return model.objects.filter(condition, **scope).select_related("course", *related)[:40]

        for doc in found(Document, "title", "search_text"):
            results.append((doc.get_kind_display(), doc.label, doc, doc.search_text))
        for card in found(Card, "search_text", related=("deck",)):
            results.append(("Flashcard", card.deck.title, card, card.search_text))
        for question in found(
            Question, "title", "search_text", related=("question_set__assessment",)
        ):
            label = question.title or f"Question {question.number}"
            results.append(
                (question.question_set.get_kind_display(), label, question, question.search_text)
            )
        for formula in found(Formula, "name", "search_text"):
            results.append(("Formula", formula.name, formula, formula.search_text))
        for term in found(Term, "term", "search_text"):
            results.append(("Glossary", term.term, term, term.search_text))
        for hook in found(Hook, "target", "search_text"):
            results.append(("Memory hook", hook.target, hook, hook.search_text))

    rows = [
        {
            "kind": kind,
            "title": title,
            "url": obj.get_absolute_url(),
            "course": obj.course,
            "snippet": _snippet(text, query),
        }
        for kind, title, obj, text in results
    ]
    page = Paginator(rows, 25).get_page(request.GET.get("page"))
    return render(
        request,
        "catalog/search.html",
        {
            "query": query,
            "course_slug": course_slug,
            "page": page,
            "total": len(rows),
            "courses": Course.objects.all(),
            "active": "search",
        },
    )


def settings_page(request):
    courses = list(Course.objects.all())
    for course in courses:
        course.counts = course_data(course)["counts"]
    return render(
        request,
        "catalog/settings.html",
        {
            "courses": courses,
            "manifests": [course_data(c)["manifest"] for c in courses],
            "active": "settings",
        },
    )
