from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from ..models import Document, QuestionSet
from .common import load_course


def course(request, course):
    course, context = load_course(course, "overview")
    documents = {kind: [] for kind in Document.SECTIONS}
    # defer(): leave the big rendered columns in the database; a list only shows titles.
    listed = course.documents.exclude(kind=Document.Kind.SHEET).defer("body_html", "search_text")
    for document in listed:
        documents[document.kind].append(document)
    context.update(
        sections=[
            {
                "kind": kind,
                "title": title,
                "documents": documents[kind],
                "list_url": reverse(f"catalog:{Document.LIST_URL_NAMES[kind]}", args=[course.slug]),
            }
            for kind, (_segment, title) in Document.SECTIONS.items()
            if documents[kind]
        ],
        # annotate() adds a computed column: here, one COUNT per deck in the same query.
        decks=course.decks.annotate(n_cards=Count("cards")).select_related("topic"),
        problem_sets=course.questionsets.filter(kind=QuestionSet.Kind.PRACTICE).annotate(
            n_questions=Count("questions")
        ),
        assessments=course.assessments.annotate(n_papers=Count("papers")),
        topics=course.topics.all(),
        palaces=course.palaces.all(),
    )
    return render(request, "catalog/course.html", context)


def topic(request, course, key):
    course, context = load_course(course, "overview")
    topic = get_object_or_404(course.topics, key=key)
    context.update(
        topic=topic,
        # Reached through the topic, these rows do not know their course yet; select_related
        # joins it in, so get_absolute_url() costs no extra query per row.
        documents=topic.documents.exclude(kind=Document.Kind.SHEET).select_related("course"),
        # A deck belongs to the topic if it is tagged with it or holds a card that is.
        decks=course.decks.filter(Q(topic=topic) | Q(cards__topic=topic)).distinct(),
        n_cards=topic.cards.count(),
        problem_sets=course.questionsets.filter(kind=QuestionSet.Kind.PRACTICE)
        .filter(Q(topic=topic) | Q(questions__topic=topic))
        .distinct(),
        n_formulas=course.formulas.filter(section__topic=topic).count(),
        n_terms=topic.terms.count(),
        n_hooks=topic.hooks.count(),
        palaces=topic.palaces.select_related("course"),
        assessments=topic.assessments.select_related("course"),
    )
    return render(request, "catalog/topic.html", context)
