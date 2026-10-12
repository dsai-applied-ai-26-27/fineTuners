"""Bring what educators added on the site into your own course files.

    manage.py import_course rl-handin-12.zip

Educators hand their work in on the site, where it is checked and goes live at once
(desk/handins.py). Your course files do not know about it until you take it in here. The
zip is one hand-in, downloaded from the admin (Hand-ins), and holds the whole course as it
stood after it. It is treated as untrusted all the same:

1. It must be plainly one course that exists here: course.yaml and content/, nothing else
   (ingest/handin.py).
2. Its course.yaml may differ from yours only in topics and description.
3. It is unpacked to a temporary folder and run through the full validation.
4. The course folder must have no uncommitted changes, so that what is taken in is a
   diff of its own that you can read and undo.

Then the two are put together file by file, and nothing of yours is ever removed:

    a file you do not have            is added
    a file that only gained lines     is replaced by the longer version
    a file where yours has more       is left alone (you are ahead)
    a file both of you changed        stops everything (--theirs takes the hand-in's)

Nothing is loaded into the database and nothing is published: read the diff, run
sync_content, commit, publish. Once the published files hold everything a hand-in added,
the site lets go of its own copy by itself.
"""

import subprocess
import tempfile
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from ingest import handin
from ingest.discover import find_courses
from ingest.management.commands.sync_content import safe_streams
from ingest.sync import sync_course


def uncommitted(folder):
    """Changed files in `folder` that git knows about; [] when clean or not a repository."""
    try:
        done = subprocess.run(
            ["git", "-C", str(folder), "status", "--porcelain", "--", "."],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return []
    return done.stdout.splitlines() if done.returncode == 0 else []


class Command(BaseCommand):
    help = "Validate a course zip from an educator and merge it into the course folder."

    def add_arguments(self, parser):
        parser.add_argument("zip", help="A hand-in downloaded from the admin, or a kit's zip.")
        parser.add_argument(
            "--check", action="store_true", help="Validate only; change nothing here."
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Go ahead although the course folder has uncommitted changes.",
        )
        parser.add_argument(
            "--theirs",
            action="store_true",
            help="Where you and the hand-in both changed a file, take the hand-in's.",
        )

    def handle(self, *args, **options):
        safe_streams()
        source = Path(options["zip"])
        if not source.is_file():
            raise CommandError(f"{source} is not a file.")
        try:
            slug, files = handin.unzip(source)
        except handin.HandInError as error:
            raise CommandError(f"Refused: {error}. Nothing was changed.") from error

        target = find_courses([settings.COURSES_DIR]).get(slug)
        if target is None:
            raise CommandError(
                f"There is no course `{slug}` here. A hand-in can add to a course, not "
                "create one: make it with startcourse first."
            )
        mine = handin.files_of(target)
        changed = handin.protected_changes(
            mine["course.yaml"].decode("utf-8"),
            files["course.yaml"].decode("utf-8", errors="replace"),
        )
        if changed:
            raise CommandError(
                "Refused: course.yaml changes what is not the educator's to change.\n  "
                + "\n  ".join(changed)
                + "\nNothing was changed."
            )

        with tempfile.TemporaryDirectory(prefix="dsai-handin-") as scratch:
            staged = Path(scratch) / slug
            for name, data in files.items():
                path = staged / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
            report = sync_course(staged, check_only=True)
        if report.errors:
            self.stdout.write(self.style.ERROR(report.format()))
            raise CommandError("The hand-in is not valid (above). Nothing was changed.")
        for issue in report.warnings:
            self.stdout.write(self.style.WARNING(issue.format()))

        added, longer, ahead, both = [], [], [], []
        for name, data in sorted(files.items()):
            if name not in mine:
                added.append(name)
            elif data == mine[name]:
                continue
            elif name == "course.yaml":
                # Its description may be reworded, so lines say little here. What counts
                # is the topics: whoever has all of the other's has the newer file.
                theirs = set(handin.topic_ids(data.decode("utf-8", errors="replace")))
                yours = set(handin.topic_ids(mine[name].decode("utf-8")))
                (longer if yours <= theirs else ahead if theirs <= yours else both).append(name)
            elif handin.extends(mine[name], data, name):
                longer.append(name)
            elif handin.extends(data, mine[name], name):
                ahead.append(name)
            else:
                both.append(name)
        summary = f"{len(added)} new, {len(longer)} longer"
        if ahead:
            summary += f", {len(ahead)} left alone (yours has more)"
        if both and not options["theirs"]:
            raise CommandError(
                "You and the hand-in both changed:\n  "
                + "\n  ".join(both)
                + "\nNothing was changed. Put the two together by hand, or pass --theirs "
                "to take the hand-in's version of these files (git keeps yours)."
            )
        if options["check"]:
            self.stdout.write(f"{slug}: valid. {summary}. Nothing was changed (--check).")
            return
        take = [*added, *longer, *both]
        if not take:
            self.stdout.write(f"{slug}: your files already hold everything in it.")
            return
        dirty = uncommitted(target)
        if dirty and not options["force"]:
            raise CommandError(
                f"{target} has uncommitted changes ({len(dirty)} files). Commit them "
                "first, so that what is taken in can be read and undone on its own, or "
                "pass --force."
            )
        for name in take:
            (target / name).parent.mkdir(parents=True, exist_ok=True)
            (target / name).write_bytes(files[name])

        if both:
            summary += f", {len(both)} replaced by the hand-in's version"
        self.stdout.write(self.style.SUCCESS(f"{slug}: taken in. {summary}."))
        self.stdout.write(
            "Next: read the diff in the courses folder, then\n"
            f"  manage.py sync_content {slug}\n"
            "commit there, and publish. The site then drops its own copy of the hand-in."
        )
