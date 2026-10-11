"""Everyone who had an account before profiles existed has already been shown around.

Until now "has seen the tour" was remembered by each browser. From here on it is a fact
about the account (accounts.Profile), and an account without a profile is taken to be new
and is offered the tour. Without this migration that would be every existing person, on
their next visit.

So each of them gets a profile saying they took the tour when they joined, at update 0:
they are not shown the tour again, and everything announced since then reaches them as
"What's new".
"""

from django.conf import settings
from django.db import migrations


def mark_as_toured(apps, schema_editor):
    # apps.get_model gives the models as they were at this point in the history, which
    # is what a data migration must use: the real classes may have changed since.
    app_label, model_name = settings.AUTH_USER_MODEL.split(".")
    User = apps.get_model(app_label, model_name)
    Profile = apps.get_model("accounts", "Profile")
    have = set(Profile.objects.values_list("user_id", flat=True))
    Profile.objects.bulk_create(
        Profile(user_id=pk, tour_seen_at=joined, tour_update=0, news_seen=0)
        for pk, joined in User.objects.values_list("pk", "date_joined")
        if pk not in have
    )


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_profile"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Undoing it needs no code: the profiles go when 0002 is undone.
        migrations.RunPython(mark_as_toured, migrations.RunPython.noop),
    ]
