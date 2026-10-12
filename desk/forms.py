"""The forms of the desk: asking or reporting (one form per kind of thing), and applying
to write a course.

All are ModelForms: Django builds the fields from the model, checks what was sent against
them (a choice that is not one of the choices, a text that is too long), and `save()` makes
the row. What a model cannot know is added here: which courses may be picked, the
questions that suit one kind of request, and the rules that involve more than one field.
"""

import re

from django import forms

from catalog.mine import by_semester

from .models import EducatorApplication, Request

PHONE = re.compile(r"^\+?[0-9][0-9 ()/.-]{5,24}$")


def course_choices(courses, empty):
    """The options of a course dropdown, under one heading per semester.

    A choice is (value, label). Where the second item is a list, Django reads it as a
    group: (heading, [choices]). A <select> draws that as an <optgroup>, a heading that
    cannot be picked itself, and validation looks inside the groups by itself.
    """
    groups = [
        (label, [(c.series, f"{c.code} · {c.title}") for c in members])
        for label, members in by_semester(courses)
    ]
    if len(groups) == 1:  # one heading over everything says nothing
        return [("", empty), *groups[0][1]]
    return [("", empty), *groups]


def lines(*parts):
    """The parts that were filled in, as paragraphs."""
    return "\n\n".join(part.strip() for part in parts if part and part.strip())


def box(rows, example="", limit=1500):
    """A box for a few lines of text. The example shows, greyed, what a good answer is."""
    attrs = {"rows": rows, "maxlength": limit}
    if example:
        attrs["placeholder"] = example
    return forms.Textarea(attrs=attrs)


class RequestForm(forms.ModelForm):
    """What the three forms of Ask or report share: the text, and the page it was sent from.

    Each kind of request is a subclass that asks its own questions. A form's fields need
    not be the model's: the questions a kind adds (where a fault was seen, what should be
    there instead) are form fields only, and `clean()` writes their answers into the one
    text the model keeps, under a word that says which is which. So a new question is a
    field here and a line in `compose`, and never a new column.
    """

    kind = None  # each subclass says which kind it sends

    class Meta:
        model = Request
        fields = ["message", "page"]
        widgets = {"message": box(5), "page": forms.HiddenInput}

    def __init__(self, *args, courses=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.courses = courses

    def compose(self, cleaned):
        """The text that is stored, from this kind's answers."""
        return cleaned.get("message", "")

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("message"):
            cleaned["message"] = self.compose(cleaned)
        return cleaned

    def save(self, commit=True):
        # Not a field of the form, so nothing that is posted can change it.
        self.instance.kind = self.kind
        self.instance.series = self.cleaned_data.get("series", "")
        return super().save(commit)


class ContentForm(RequestForm):
    """Content a course lacks: which course, what kind of thing, and which part."""

    kind = Request.Kind.CONTENT
    WANTS = [
        ("notes", "Lecture notes"),
        ("cards", "Flashcards"),
        ("problems", "Problems with solutions"),
        ("paper", "A past paper"),
        ("exam", "Exam prep"),
    ]

    series = forms.ChoiceField(
        label="Which course?",
        error_messages={"required": "Say which course the content is for."},
    )
    # Several may be ticked: a list of values, each checked against the choices.
    wants = forms.MultipleChoiceField(
        label="What is missing?",
        choices=WANTS,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta(RequestForm.Meta):
        labels = {"message": "Which lecture or topic?"}
        widgets = {
            "message": box(4, "Lecture 5, policy gradients. The slides are out since Monday."),
            "page": forms.HiddenInput,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # The model stores any series; the form only offers, and so only accepts, the
        # courses this person can see.
        self.fields["series"].choices = course_choices(self.courses, "Choose a course")

    def compose(self, cleaned):
        named = dict(self.WANTS)
        wanted = ", ".join(named[value].lower() for value in cleaned.get("wants", []))
        return lines(f"Missing: {wanted}" if wanted else "", cleaned["message"])


class BugForm(RequestForm):
    """Something that is wrong: where, what, and what it should be instead."""

    kind = Request.Kind.BUG

    where = forms.CharField(
        label="Where did you see it?",
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={"placeholder": "Card 4 of the deck on MDPs"}),
    )
    series = forms.ChoiceField(label="Is it in a course?", required=False)
    expected = forms.CharField(
        label="What should it say or do instead?",
        required=False,
        max_length=800,
        widget=box(3, limit=800),
    )

    class Meta(RequestForm.Meta):
        labels = {"message": "What is wrong?"}
        widgets = {
            "message": box(4, "The answer starts the sum at 0. The lecture starts it at 1."),
            "page": forms.HiddenInput,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["series"].choices = course_choices(self.courses, "Not in a course")

    def compose(self, cleaned):
        where, expected = cleaned.get("where", ""), cleaned.get("expected", "")
        return lines(
            f"Where: {where}" if where else "",
            cleaned["message"],
            f"Should be: {expected}" if expected else "",
        )


class IdeaForm(RequestForm):
    """Something the site should be able to do, and what for. It is about no course."""

    kind = Request.Kind.IDEA

    why = forms.CharField(
        label="What would it help you with?",
        required=False,
        max_length=800,
        widget=box(3, limit=800),
    )

    class Meta(RequestForm.Meta):
        labels = {"message": "What should the site be able to do?"}
        widgets = {
            "message": box(4, "Print a deck as one sheet, to study on paper."),
            "page": forms.HiddenInput,
        }

    def compose(self, cleaned):
        why = cleaned.get("why", "")
        return lines(cleaned["message"], f"Why: {why}" if why else "")


# The form for each kind, in the order the page offers them. What the page says about a
# kind (its name comes from the model) sits beside the form that asks for it.
REQUEST_FORMS = {
    Request.Kind.CONTENT: (ContentForm, "a lecture, cards, a past paper"),
    Request.Kind.BUG: (BugForm, "a mistake in the material, a page that breaks"),
    Request.Kind.IDEA: (IdeaForm, "something it should be able to do"),
}


class EducatorApplicationForm(forms.ModelForm):
    class Meta:
        model = EducatorApplication
        # Not every column of the model: a form takes only the fields it names, so
        # whatever else a request carries is ignored.
        fields = ["series", "name", "phone", "year", "tools", "note"]
        # What a field looks like in HTML is its widget. The attributes are hints to the
        # browser: which keyboard a phone shows, what it may fill in by itself.
        widgets = {
            "name": forms.TextInput(attrs={"autocomplete": "name"}),
            "phone": forms.TextInput(
                attrs={"type": "tel", "autocomplete": "tel", "placeholder": "+387 61 123 456"}
            ),
            "note": forms.Textarea(attrs={"rows": 4, "maxlength": 1000}),
        }

    def __init__(self, *args, courses=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["series"] = forms.ChoiceField(
            choices=course_choices(courses, "Choose a course")
        )
        self.fields["year"].choices = EducatorApplication.Year.choices
        self.fields["tools"].choices = EducatorApplication.Tools.choices

    def clean_phone(self):
        phone = " ".join(self.cleaned_data["phone"].split())
        if not PHONE.match(phone):
            raise forms.ValidationError(
                "Write the number with digits, for example +387 61 123 456."
            )
        return phone
