from django.db import models
from django.urls import reverse

from .base import KeyedItem, SluggedItem


class FormulaSection(SluggedItem):
    title = models.CharField(max_length=200)
    topic = models.ForeignKey(
        "catalog.Topic",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="formula_sections",
    )

    def __str__(self):
        return self.title


class Formula(KeyedItem):
    section = models.ForeignKey(FormulaSection, on_delete=models.CASCADE, related_name="formulas")
    name = models.CharField(max_length=200)
    body_html = models.TextField()
    note_html = models.TextField(blank=True)
    search_text = models.TextField(blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"{reverse('catalog:formulas', args=[self.course.slug])}#{self.key}"


class Term(KeyedItem):
    term = models.CharField(max_length=200)
    definition_html = models.TextField()
    topic = models.ForeignKey(
        "catalog.Topic", null=True, blank=True, on_delete=models.SET_NULL, related_name="terms"
    )
    see = models.JSONField(default=list, blank=True)  # [{key, term}]
    search_text = models.TextField(blank=True)

    class Meta(KeyedItem.Meta):
        ordering = ["term"]

    def __str__(self):
        return self.term

    def get_absolute_url(self):
        return f"{reverse('catalog:glossary', args=[self.course.slug])}#{self.key}"
