"""Views, grouped by area. urls.py refers to them as `views.<name>`."""

from .course import course, topic
from .documents import document, document_list
from .exams import assessment, exams, paper
from .home import home, privacy, search, settings_page, terms
from .memory import memory, palace
from .mine import choose, enroll
from .practice import cards, deck, problem_set, problems, review
from .reference import cheatsheet, formulas, glossary
from .source import source_file
from .welcome import seen, whats_new

__all__ = [
    "assessment",
    "cards",
    "cheatsheet",
    "choose",
    "course",
    "deck",
    "document",
    "document_list",
    "enroll",
    "exams",
    "formulas",
    "glossary",
    "home",
    "memory",
    "palace",
    "paper",
    "privacy",
    "problem_set",
    "problems",
    "review",
    "search",
    "seen",
    "settings_page",
    "source_file",
    "terms",
    "topic",
    "whats_new",
]
