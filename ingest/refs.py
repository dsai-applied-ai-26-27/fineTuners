"""Internal links.

Authors never write site URLs. They write a reference — `card:fisher-01`,
`lecture:05-features`, `paper:final/past-2026` — and sync turns it into the real URL with
Django's `reverse()`. Because every reference is looked up in an index of what the course
actually contains, a link to something that does not exist is an error at sync time instead
of a dead link on the site.
"""

import difflib
import re
from dataclasses import dataclass, field

from django.urls import reverse

DOC_KINDS = {
    "lecture": "lecture",
    "lab": "lab",
    "hw": "homework",
    "homework": "homework",
    "guide": "guide",
}
DECK_FILTERS = {
    "all",
    "unseen",
    "due",
    "weak",
    "missed",
    "shaky",
    "solid",
    "key",
    "steps",
    "cloze",
}
# Bare words that name a whole section of the course.
SECTIONS = {"course", "cards", "problems", "exams", "formulas", "glossary", "cheatsheet", "memory"}

EXAMPLES = (
    "lecture:05-name, guide:name, deck:name, card:id, problems:set#id, paper:exam/paper, "
    "exam:name, formula:id, term:id, hook:id, palace:name, topic:id"
)

_REF = re.compile(
    r"^(?P<kind>[a-z]+)(?::(?P<target>[^#?]*))?(?P<query>\?[^#]*)?(?P<fragment>#.*)?$"
)


class RefError(ValueError):
    def __init__(self, message, hint=""):
        super().__init__(message)
        self.hint = hint


@dataclass
class Index:
    """Everything in one course that can be linked to, by the name authors use."""

    course: str
    topics: dict[str, str] = field(default_factory=dict)  # id -> title
    documents: dict[tuple[str, str], str] = field(default_factory=dict)  # (kind, slug) -> title
    lecture_numbers: dict[int, str] = field(default_factory=dict)  # number -> slug
    decks: dict[str, str] = field(default_factory=dict)  # slug -> title
    cards: dict[str, tuple[str, str]] = field(default_factory=dict)  # id -> (deck slug, label)
    sets: dict[str, str] = field(default_factory=dict)  # slug -> title
    questions: dict[str, tuple[str, str]] = field(default_factory=dict)  # id -> (set, label)
    assessments: dict[str, str] = field(default_factory=dict)  # slug -> title
    papers: dict[tuple[str, str], str] = field(default_factory=dict)  # (exam, paper) -> title
    formulas: dict[str, str] = field(default_factory=dict)  # id -> name
    terms: dict[str, str] = field(default_factory=dict)  # id -> term
    hooks: dict[str, str] = field(default_factory=dict)  # id -> target
    palaces: dict[str, str] = field(default_factory=dict)  # slug -> title
    has_cheatsheet: bool = False


def _missing(what, name, known):
    close = difflib.get_close_matches(name, [str(k) for k in known], n=3, cutoff=0.5)
    hint = "did you mean " + ", ".join(f"`{c}`" for c in close) + "?" if close else ""
    return RefError(f"no {what} named `{name}` in this course", hint)


class Resolver:
    def __init__(self, index):
        self.index = index
        self.course = index.course

    def resolve(self, ref):
        """Return (url, label) for a reference, or raise RefError."""
        ref = ref.strip()
        match = _REF.match(ref)
        if not match:
            raise RefError(
                f"`{ref}` is not a link the site understands",
                f"link with a reference ({EXAMPLES}) or a full https:// address",
            )
        kind = match["kind"]
        target = (match["target"] or "").strip()
        query = match["query"] or ""
        fragment = match["fragment"] or ""
        index, course = self.index, self.course

        if kind in SECTIONS and not target:
            return self._section(kind, query, fragment)

        if kind in DOC_KINDS:
            doc_kind = DOC_KINDS[kind]
            title = index.documents.get((doc_kind, target))
            if title is None:
                known = [slug for (k, slug) in index.documents if k == doc_kind]
                raise _missing(doc_kind, target, known)
            return reverse(f"catalog:{doc_kind}", args=[course, target]) + fragment, title

        if kind == "deck":
            if target not in index.decks:
                raise _missing("deck", target, index.decks)
            return (
                reverse("catalog:deck", args=[course, target]) + self._filter(query),
                index.decks[target],
            )

        if kind == "card":
            if target not in index.cards:
                raise _missing("card", target, index.cards)
            deck, label = index.cards[target]
            return reverse("catalog:deck", args=[course, deck]) + f"?card={target}", label

        if kind == "problems":
            if target not in index.sets:
                raise _missing("problem set", target, index.sets)
            label = index.sets[target]
            if fragment:
                owner, label = index.questions.get(fragment[1:], (None, ""))
                if owner != target:
                    raise _missing(f"question in `{target}`", fragment[1:], index.questions)
            return reverse("catalog:problem_set", args=[course, target]) + fragment, label

        if kind == "paper":
            exam, _, paper = target.partition("/")
            if (exam, paper) not in index.papers:
                known = [f"{e}/{p}" for e, p in index.papers]
                raise _missing("paper", target, known)
            if query not in ("", "?mode=sit", "?mode=study"):
                raise RefError(f"unknown option `{query}` on a paper link", "use ?mode=sit")
            return (
                reverse("catalog:paper", args=[course, exam, paper]) + query + fragment,
                index.papers[(exam, paper)],
            )

        if kind == "exam":
            if target not in index.assessments:
                raise _missing("exam", target, index.assessments)
            return (
                reverse("catalog:assessment", args=[course, target]) + fragment,
                index.assessments[target],
            )

        simple = {
            "formula": (index.formulas, "formula", "catalog:formulas"),
            "term": (index.terms, "glossary term", "catalog:glossary"),
            "hook": (index.hooks, "hook", "catalog:memory"),
        }
        if kind in simple:
            known, what, url_name = simple[kind]
            if target not in known:
                raise _missing(what, target, known)
            return reverse(url_name, args=[course]) + f"#{target}", known[target]

        if kind == "palace":
            if target not in index.palaces:
                raise _missing("palace", target, index.palaces)
            return reverse("catalog:palace", args=[course, target]), index.palaces[target]

        if kind == "topic":
            if target not in index.topics:
                raise _missing("topic", target, index.topics)
            return reverse("catalog:topic", args=[course, target]), index.topics[target]

        if kind == "source":
            if not target or target.startswith("/") or ".." in target.split("/"):
                raise RefError(f"`{target}` is not a path inside source/")
            return reverse("catalog:source", args=[course, target]), target.rsplit("/", 1)[-1]

        raise RefError(
            f"`{ref}` is not a link the site understands",
            f"link with a reference ({EXAMPLES}) or a full https:// address",
        )

    def links(self, refs):
        """Resolve a list of references into [{label, url}] (raises on the first bad one)."""
        return [dict(zip(("url", "label"), self.resolve(ref), strict=True)) for ref in refs]

    def _filter(self, query):
        if not query:
            return ""
        match = re.fullmatch(r"\?filter=([a-z]+)", query)
        if not match or match.group(1) not in DECK_FILTERS:
            raise RefError(
                f"unknown option `{query}` on a card link",
                "use ?filter= with one of: " + ", ".join(sorted(DECK_FILTERS)),
            )
        return query

    def _section(self, kind, query, fragment):
        index, course = self.index, self.course
        if kind == "course":
            return reverse("catalog:course", args=[course]), "Course home"
        if kind == "cards":
            if query:
                return reverse("catalog:review", args=[course]) + self._filter(query), "Flashcards"
            return reverse("catalog:cards", args=[course]), "Flashcards"
        if kind == "formulas":
            if fragment and fragment[1:] not in index.formulas:
                raise _missing("formula", fragment[1:], index.formulas)
            label = index.formulas.get(fragment[1:], "Formula sheet")
            return reverse("catalog:formulas", args=[course]) + fragment, label
        if kind == "glossary":
            if fragment and fragment[1:] not in index.terms:
                raise _missing("glossary term", fragment[1:], index.terms)
            return reverse("catalog:glossary", args=[course]) + fragment, "Glossary"
        if kind == "memory":
            return reverse("catalog:memory", args=[course]) + fragment, "Memory hooks"
        if kind == "cheatsheet":
            if not index.has_cheatsheet:
                raise RefError("this course has no cheat sheet (content/reference/cheatsheet.md)")
            return reverse("catalog:cheatsheet", args=[course]) + fragment, "Cheat sheet"
        if kind == "exams":
            return reverse("catalog:exams", args=[course]), "Exams"
        return reverse("catalog:problems", args=[course]), "Problems"
