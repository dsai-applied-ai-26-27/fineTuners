"""Show what each course contains and what still needs writing up.

    manage.py content_status          every course
    manage.py content_status rl       one course

The most useful part for a content session: files under source/ that no document lists in
its `sources:` field — i.e. material nobody has turned into notes yet.
"""

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from catalog import models
from ingest.discover import content_hash, find_courses
from ingest.management.commands.sync_content import safe_streams


class Command(BaseCommand):
    help = "Per course: what is in the database, and which source files are not covered yet."

    def add_arguments(self, parser):
        parser.add_argument("courses", nargs="*", help="Course slugs (default: all).")

    def handle(self, *args, **options):
        safe_streams()
        folders = find_courses(settings.CONTENT_ROOTS)
        wanted = options["courses"] or sorted(folders)
        for slug in wanted:
            folder = folders.get(slug)
            if folder is None:
                self.stdout.write(self.style.ERROR(f"{slug}: no such course folder"))
                continue
            self.describe(slug, Path(folder))
            self.stdout.write("")

    def describe(self, slug, folder):
        course = models.Course.objects.filter(slug=slug).first()
        if course is None:
            self.stdout.write(
                f"{slug}: not in the database yet -> run: manage.py sync_content {slug}"
            )
        else:
            when = timezone.localtime(course.synced_at).strftime("%Y-%m-%d %H:%M")
            state = "up to date" if course.content_hash == content_hash(folder) else "FILES CHANGED"
            self.stdout.write(f"{slug}: {course.title}  (synced {when}, {state})")
            counts = {
                "lectures": course.documents.filter(kind="lecture").count(),
                "labs": course.documents.filter(kind="lab").count(),
                "homework": course.documents.filter(kind="homework").count(),
                "guides": course.documents.filter(kind="guide").count(),
                "decks": course.decks.count(),
                "cards": course.cards.count(),
                "problem sets": course.questionsets.filter(kind="practice").count(),
                "exams": course.assessments.count(),
                "papers": course.questionsets.exclude(kind="practice").count(),
                "formulas": course.formulas.count(),
                "terms": course.terms.count(),
                "hooks": course.hooks.count(),
                "palaces": course.palaces.count(),
            }
            filled = ", ".join(f"{n} {name}" for name, n in counts.items() if n)
            self.stdout.write("  " + (filled or "no content yet"))
            empty = [name for name, n in counts.items() if not n]
            if empty and filled:
                self.stdout.write("  none yet: " + ", ".join(empty))

        source = folder / "source"
        if not source.is_dir():
            return
        files = sorted(
            path.relative_to(source).as_posix()
            for path in source.rglob("*")
            if path.is_file() and not path.name.startswith(".") and path.name.lower() != "readme.md"
        )
        if not files:
            self.stdout.write("  source/ is empty: add lecture slides, labs, homework there")
            return
        covered = set()
        if course is not None:
            for sources in course.documents.values_list("sources", flat=True):
                covered.update(sources)
        pending = [name for name in files if name not in covered]
        self.stdout.write(
            f"  source files: {len(files)}, referenced by content: {len(files) - len(pending)}"
        )
        if pending:
            self.stdout.write(f"  not written up yet ({len(pending)}):")
            for name in pending:
                self.stdout.write(f"    {name}")
