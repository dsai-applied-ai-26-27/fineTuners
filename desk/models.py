"""The owner's desk: what people send in, who writes which course, and the owner's switches.

Like accounts and progress, these rows exist nowhere else. A course is named by its
`series`, as text, for the same reasons as in accounts.Enrollment: the course tables are a
cache of files that can be rebuilt, and a series outlives one academic year of a course.
"""

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone


class Request(models.Model):
    """Something a person sent to whoever runs the site."""

    class Kind(models.TextChoices):
        CONTENT = "content", "Content for a course"
        BUG = "bug", "Something is wrong"
        IDEA = "idea", "An idea for the site"

    class Status(models.TextChoices):
        NEW = "new", "New"
        DONE = "done", "Done"
        DECLINED = "declined", "Not planned"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="requests"
    )
    kind = models.CharField(max_length=10, choices=Kind)
    series = models.SlugField(max_length=64, blank=True)  # the course it is about, if any
    message = models.TextField(max_length=2000)
    # The page they were on when they opened the form: where a fault was seen.
    page = models.CharField(max_length=300, blank=True)
    status = models.CharField(max_length=10, choices=Status, default=Status.NEW)
    # A line back from the owner (or the course's educator), shown to the person.
    answer = models.TextField(max_length=1000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        about = f" ({self.series})" if self.series else ""
        return f"{self.get_kind_display()}{about}"


class EducatorApplication(models.Model):
    """Someone offering to write a course. One per person and course; sending the form
    again updates it."""

    class Year(models.TextChoices):
        FIRST = "1", "1st year"
        SECOND = "2", "2nd year"
        THIRD = "3", "3rd year"
        OTHER = "other", "Finished, or other"

    class Tools(models.TextChoices):
        PAID = "paid", "A paid AI assistant (Claude, ChatGPT, Gemini or similar)"
        FREE = "free", "A free AI assistant"
        HAND = "hand", "By hand"
        UNSURE = "unsure", "Not sure yet"

    class Status(models.TextChoices):
        PENDING = "pending", "Waiting for an answer"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="educator_applications"
    )
    series = models.SlugField(max_length=64)
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=40)
    year = models.CharField(max_length=10, choices=Year)
    github = models.CharField(max_length=40, blank=True)
    tools = models.CharField(max_length=10, choices=Tools, default=Tools.UNSURE)
    note = models.TextField(max_length=1000, blank=True)
    status = models.CharField(max_length=10, choices=Status, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    decided_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "series"], name="desk_application_unique")
        ]

    def __str__(self):
        return f"{self.name} for {self.series}"

    @transaction.atomic
    def decide(self, status):
        """Answer the application. Accepting it is what makes the person the educator of
        the course; taking an acceptance back takes the role back with it.

        Both changes happen together or not at all (`transaction.atomic`), so there is
        never an accepted application without its educator.
        """
        self.status = status
        self.decided_at = None if status == self.Status.PENDING else timezone.now()
        self.save(update_fields=["status", "decided_at"])
        role = Educator.objects.filter(user=self.user, series=self.series)
        if status == self.Status.ACCEPTED:
            Educator.objects.get_or_create(user=self.user, series=self.series)
        else:
            role.delete()


class Educator(models.Model):
    """The role: this person writes this course."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="educating"
    )
    series = models.SlugField(max_length=64)
    since = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "series"], name="desk_educator_unique")
        ]

    def __str__(self):
        return f"{self.user} writes {self.series}"


class CourseSetting(models.Model):
    """The owner's switches for one course. Each has three positions: empty means "as the
    course's own file says", and yes or no overrides the file until it is emptied again.

    They live here and not on catalog.Course because that table is rebuilt from files.
    """

    series = models.SlugField(max_length=64, unique=True)
    # Whether students see the course at all (course.yaml: `enabled`).
    enabled = models.BooleanField(null=True, blank=True)
    # Whether someone is writing it, so its page need not ask (course.yaml: `has_educator`).
    has_educator = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return self.series
