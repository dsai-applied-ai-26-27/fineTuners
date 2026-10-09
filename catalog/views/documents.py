from pathlib import PurePosixPath

from django.conf import settings
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from ..models import Document, QuestionSet
from .common import load_course


def document_list(request, course, kind):
    segment, title = Document.SECTIONS[kind]
    course, context = load_course(course, segment)
    context.update(
        kind=kind,
        section_title=title,
        # prefetch_related: one extra query fetches the topics of all documents at once,
        # instead of one query per document inside the template loop (the "N+1" problem).
        documents=course.documents.filter(kind=kind)
        .defer("body_html", "search_text")
        .prefetch_related("topics"),
    )
    return render(request, "catalog/document_list.html", context)


def document(request, course, slug, kind):
    segment, section_title = Document.SECTIONS[kind]
    course, context = load_course(course, segment)
    doc = get_object_or_404(course.documents, kind=kind, slug=slug)
    topics = list(doc.topics.all())

    siblings = list(course.documents.filter(kind=kind).only("slug", "title", "kind", "course"))
    position = next(i for i, sibling in enumerate(siblings) if sibling.pk == doc.pk)
    sources = [
        {
            "name": PurePosixPath(path).name,
            "url": reverse("catalog:source", args=[course.slug, path])
            if settings.SERVE_SOURCE_FILES
            else "",
        }
        for path in doc.sources
    ]
    context.update(
        doc=doc,
        kind=kind,
        section_title=section_title,
        list_url=reverse(f"catalog:{Document.LIST_URL_NAMES[kind]}", args=[course.slug]),
        topics=topics,
        sources=sources,
        previous=siblings[position - 1] if position > 0 else None,
        next=siblings[position + 1] if position + 1 < len(siblings) else None,
        decks=course.decks.filter(Q(lecture=doc) | Q(topic__in=topics)).distinct(),
        problem_sets=course.questionsets.filter(kind=QuestionSet.Kind.PRACTICE)
        .filter(Q(topic__in=topics) | Q(questions__topic__in=topics))
        .distinct(),
        assessments=doc.assessments.all() if kind == Document.Kind.LECTURE else [],
    )
    return render(request, "catalog/document.html", context)
