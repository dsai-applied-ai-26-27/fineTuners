"""Course.series: what ties the years of one course together.

Two steps in one migration. The schema step adds the column, empty. The data step
(RunPython) then gives every existing course a series of its own, named after its slug,
which is exactly what `sync_content` writes for a course.yaml without `series`. So the
rule "series is never empty" holds from the moment this has run, not only after the next
sync.
"""

from django.db import migrations, models
from django.db.models import F


def own_series(apps, schema_editor):
    # apps.get_model gives the model as it looked at this point in history, not the one
    # in catalog/models today. Data migrations must use it, or they break when the model
    # changes later.
    Course = apps.get_model("catalog", "Course")
    Course.objects.filter(series="").update(series=F("slug"))


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0002_course_semester_number"),
    ]

    operations = [
        migrations.AddField(
            model_name="course",
            name="series",
            field=models.SlugField(blank=True, max_length=64),
        ),
        # Nothing to undo when going backwards: the column itself is dropped.
        migrations.RunPython(own_series, migrations.RunPython.noop),
    ]
