"""A signed-in person's study progress.

The browser keeps its own copy of all of this and works from it, so pages never wait for
the server. These tables are the copy that follows the person to another device. The two
are brought together by `progress.sync`, which is the only code that writes here.

Unlike `catalog`, these rows are not derived from files: they exist nowhere else. They are
also not tied to `catalog` rows by a foreign key. An item is named by the course's slug and
the item's permanent id, exactly as the browser names it, so progress survives a course
being re-imported, renamed in the database, or temporarily removed.

`version` on every row is the value of the owner's counter (`Ledger`) when the row last
changed. "What is new since I last asked?" is then one indexed query: version > N.
"""

from django.conf import settings
from django.db import models


class Owned(models.Model):
    """Fields every progress row has. Abstract: it makes no table of its own."""

    # settings.AUTH_USER_MODEL rather than User: the documented way to point at "the user
    # model", whichever one the project uses. CASCADE: deleting an account deletes these.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+")
    version = models.BigIntegerField()

    class Meta:
        abstract = True


class Ledger(models.Model):
    """One row per person: the counter that numbers their changes."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="progress_ledger"
    )
    version = models.BigIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} at version {self.version}"


class Record(Owned):
    """The latest grade or mark for one item: a card, a question, a lecture, a plan phase."""

    class State(models.IntegerChoices):
        CLEARED = 0, "cleared"
        MISSED = 1, "missed"
        SHAKY = 2, "shaky"
        SOLID = 3, "solid"

    course = models.CharField(max_length=80)
    key = models.CharField(max_length=200)
    state = models.PositiveSmallIntegerField(choices=State)
    streak = models.PositiveIntegerField(default=0)  # times in a row it was solid
    count = models.PositiveIntegerField(default=0)  # times it was graded at all
    # When it was graded, by the clock of the device that graded it, in milliseconds.
    # Of two versions of the same record, the one graded later wins.
    graded_at = models.BigIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "course", "key"], name="progress_record_unique")
        ]
        indexes = [models.Index(fields=["user", "version"], name="progress_record_version")]

    def __str__(self):
        return f"{self.course}/{self.key}: {self.get_state_display()}"


class Attempt(Owned):
    """One sitting of a mock exam."""

    course = models.CharField(max_length=80)
    paper = models.CharField(max_length=200)
    score = models.FloatField()
    max_score = models.FloatField()
    seconds = models.PositiveIntegerField(default=0)
    taken_at = models.BigIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "course", "paper", "taken_at"], name="progress_attempt_unique"
            )
        ]
        indexes = [models.Index(fields=["user", "version"], name="progress_attempt_version")]

    def __str__(self):
        return f"{self.course}/{self.paper}: {self.score:g} / {self.max_score:g}"


class Day(Owned):
    """How much was done on one calendar day (the device's own calendar)."""

    day = models.DateField()
    cards = models.PositiveIntegerField(default=0)
    minutes = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "day"], name="progress_day_unique")]
        indexes = [models.Index(fields=["user", "version"], name="progress_day_version")]

    def __str__(self):
        return f"{self.day}: {self.cards} cards, {self.minutes} min"


class Clear(Owned):
    """An instruction to forget everything before a moment: one course, or all ("*").

    Deleting rows is not enough when there are several devices: another one would send its
    old copy straight back. Keeping the moment lets every device drop what is older.
    """

    EVERYTHING = "*"

    scope = models.CharField(max_length=80)
    cleared_at = models.BigIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "scope"], name="progress_clear_unique")
        ]

    def __str__(self):
        return f"{self.scope} cleared"
