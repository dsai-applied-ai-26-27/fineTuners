"""The two forms of the desk: asking or reporting, and applying to write a course.

Both are ModelForms: Django builds the fields from the model, checks what was sent against
them (a choice that is not one of the choices, a text that is too long), and `save()` makes
the row. What a model cannot know is added here: which courses may be picked, and the
rules that involve more than one field.
"""

import re

from django import forms

from .models import EducatorApplication, Request

PHONE = re.compile(r"^\+?[0-9][0-9 ()/.-]{5,24}$")


def course_choices(courses, empty):
    return [("", empty), *[(c.series, f"{c.code} · {c.title}") for c in courses]]


class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ["kind", "series", "message", "page"]
        widgets = {
            "kind": forms.RadioSelect,
            "message": forms.Textarea(attrs={"rows": 6, "maxlength": 2000}),
            "page": forms.HiddenInput,
        }

    def __init__(self, *args, courses=(), **kwargs):
        super().__init__(*args, **kwargs)
        # The model stores any series; the form only offers, and so only accepts, the
        # courses this person can see.
        self.fields["series"] = forms.ChoiceField(
            choices=course_choices(courses, "No course in particular"), required=False
        )
        self.fields["kind"].choices = Request.Kind.choices  # no empty "---------" option

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("kind") == Request.Kind.CONTENT and not cleaned.get("series"):
            self.add_error("series", "Say which course the content is for.")
        return cleaned


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
