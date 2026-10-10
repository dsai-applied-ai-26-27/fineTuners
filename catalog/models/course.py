from django.db import models
from django.urls import reverse

from .base import KeyedItem

ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]


class Course(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        ARCHIVED = "archived", "Archived"

    slug = models.SlugField(max_length=40, unique=True)
    title = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    year = models.CharField(max_length=20, blank=True)
    # Which semester of the programme (1-12). NULL means "not said", which is different
    # from any number, so the column allows NULL instead of using 0 as a stand-in.
    semester = models.PositiveSmallIntegerField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status, default=Status.ACTIVE)
    hue = models.PositiveSmallIntegerField(default=250)
    order = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)

    # Set by sync_content. The hash lets it skip a course whose files have not changed;
    # the time is when the files were last compared with the database.
    content_hash = models.CharField(max_length=64, blank=True)
    synced_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["status", "-year", "order", "title"]

    def __str__(self):
        return f"{self.code} · {self.title}"

    def get_absolute_url(self):
        return reverse("catalog:course", args=[self.slug])

    @property
    def semester_label(self):
        """ "Semester V", the way the faculty writes it; empty when no semester is set."""
        return f"Semester {ROMAN[self.semester]}" if self.semester else ""


class Topic(KeyedItem):
    """A chapter or unit. Everything else points at topics, which is what lets an exam
    say "I cover these topics" and get its cards, problems and formulas for free."""

    title = models.CharField(max_length=200)
    short = models.CharField(max_length=40, blank=True)

    def __str__(self):
        return self.title

    @property
    def label(self):
        return self.short or self.title

    def get_absolute_url(self):
        return reverse("catalog:topic", args=[self.course.slug, self.key])
