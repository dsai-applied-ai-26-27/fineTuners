"""Course.semester: from a season ("winter") to a semester of the programme (5).

Written by hand as remove + add, where `makemigrations` would propose one AlterField.
SQLite stores whatever it is given, so altering the column in place would carry the old
text over into a number column. Dropping the column first cannot leave such values behind.
Nothing is lost: the column is filled from course.yaml by the next `sync_content`.
"""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(model_name="course", name="semester"),
        migrations.AddField(
            model_name="course",
            name="semester",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]
