"""What the site keeps about a person besides who they are and what they have studied.

Two things: which courses they chose to have on their dashboard, and what the site has
already shown them unasked (the tour, the news). Like progress, these rows exist nowhere
else, so every change to this file needs a migration.
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


class Profile(models.Model):
    """What the site has put in front of one person unasked, so that it does so once.

    A OneToOneField is a foreign key that allows one row per user: the usual Django way
    to keep more about a person without replacing the user model. The row is made the
    first time there is something to record; a person without one has seen nothing yet.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    # When they were walked through the site. Empty until then, which is how a first visit
    # is told from every later one.
    tour_seen_at = models.DateTimeField(null=True, blank=True)
    # The site's latest update at that moment (its number in catalog/news.py). Updates
    # numbered higher are what changed since their tour.
    tour_update = models.PositiveIntegerField(default=0)
    # The latest update the "What's new" dialog has shown them.
    news_seen = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user}: toured {self.tour_seen_at or 'never'}, news {self.news_seen}"
