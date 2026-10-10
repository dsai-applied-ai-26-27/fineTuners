"""Let someone who signs in with Google into the admin.

    manage.py make_admin you@example.com

People are created by their first sign-in, as ordinary users. This marks one of them as
staff and superuser, which is what /admin/ checks. They need no password: the admin accepts
the session they already have from signing in with Google.
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Give the admin to a person who has already signed in, by e-mail address."

    def add_arguments(self, parser):
        parser.add_argument("email")
        parser.add_argument("--revoke", action="store_true", help="Take the admin away again.")

    def handle(self, *args, **options):
        users = get_user_model().objects.filter(email__iexact=options["email"])
        if not users:
            raise CommandError(
                f"Nobody with the address {options['email']} has signed in yet. "
                "Sign in on the site once, then run this again."
            )
        grant = not options["revoke"]
        users.update(is_staff=grant, is_superuser=grant)
        verb = "can now open" if grant else "can no longer open"
        self.stdout.write(f"{options['email']} {verb} /admin/.")
