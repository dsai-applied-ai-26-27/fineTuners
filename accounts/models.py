"""What the site keeps about a person besides who they are and what they have studied.

One thing: which courses they chose to have on their dashboard. Like progress, these rows
exist nowhere else, so every change to this file needs a migration.
"""

from django.conf import settings
from django.db import models, transaction


class EnrollmentManager(models.Manager):
    """Questions about the table as a whole, kept beside it.

    A manager is what `Enrollment.objects` is. Django gives every model a plain one;
    writing your own is the usual place for operations on many rows, so that views say
    what they want (`Enrollment.objects.replace(user, series)`) and not how to get it.
    """

    def series_of(self, user):
        """The courses on this person's dashboard, as a set of series names."""
        return set(self.filter(user=user).values_list("series", flat=True))

    @transaction.atomic
    def replace(self, user, series):
        """Make `series` exactly what this person has chosen: add what is new, drop the rest."""
        wanted = set(series)
        self.filter(user=user).exclude(series__in=wanted).delete()
        missing = wanted - self.series_of(user)
        self.bulk_create([self.model(user=user, series=name) for name in sorted(missing)])


class Enrollment(models.Model):
    """One course on one person's dashboard."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments"
    )
    # The course's series as text, not a foreign key to catalog.Course, for two reasons.
    # Course rows are a cache of files: they can be rebuilt, or be gone for a moment, and
    # a person's choice must outlive that. And it is the series, not the slug, so that next
    # year's edition of a course takes its place on the dashboard without anyone choosing
    # again (catalog/editions.py).
    series = models.SlugField(max_length=64)
    chosen_at = models.DateTimeField(auto_now_add=True)

    objects = EnrollmentManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "series"], name="accounts_enrollment_unique")
        ]

    def __str__(self):
        return f"{self.user}: {self.series}"
