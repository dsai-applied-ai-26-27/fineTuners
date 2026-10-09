from django.db import models


class CourseItem(models.Model):
    """Something that belongs to one course and has a position inside it.

    Abstract: no table of its own. Each subclass gets these columns in its own table.
    `%(class)ss` gives every subclass its own reverse accessor (course.cards, course.decks…).
    """

    course = models.ForeignKey(
        "catalog.Course", on_delete=models.CASCADE, related_name="%(class)ss"
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True
        ordering = ["order", "id"]


class KeyedItem(CourseItem):
    """An item content authors address by `id`. The id is permanent: study progress in the
    browser is stored under `<course>/<key>`, so the importer updates rows in place by key."""

    key = models.SlugField(max_length=64)

    class Meta(CourseItem.Meta):
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=["course", "key"], name="%(app_label)s_%(class)s_course_key"
            )
        ]


class SluggedItem(CourseItem):
    """An item with its own page, addressed by the file name it came from."""

    slug = models.SlugField(max_length=80)

    class Meta(CourseItem.Meta):
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=["course", "slug"], name="%(app_label)s_%(class)s_course_slug"
            )
        ]
