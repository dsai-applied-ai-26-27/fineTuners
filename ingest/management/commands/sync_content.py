"""Validate the course files and load them into the database.

    manage.py sync_content                 every course
    manage.py sync_content mlpr rl         only these
    manage.py sync_content mlpr --check    validate only, write nothing
    manage.py sync_content --watch         re-sync whenever a file changes
    manage.py sync_content --force         re-import even if nothing changed

Exit status is 1 when any course has errors, so scripts and AI agents can tell.
"""

import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from ingest.sync import sync_all


def safe_streams():
    """Piped output on Windows is not UTF-8; never let a stray character abort the report."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="backslashreplace")


class Command(BaseCommand):
    help = "Validate course content under courses/ and load it into the database."

    def add_arguments(self, parser):
        parser.add_argument("courses", nargs="*", help="Course slugs (default: all).")
        parser.add_argument("--check", action="store_true", help="Validate only; write nothing.")
        parser.add_argument("--force", action="store_true", help="Re-import unchanged courses.")
        parser.add_argument("--watch", action="store_true", help="Keep running; sync on change.")

    def handle(self, *args, **options):
        safe_streams()
        only = options["courses"] or None
        failed = self.run_once(only, options["check"], options["force"])
        if options["watch"]:
            self.watch(only, options["check"])
        elif failed:
            raise CommandError(
                f"{failed} course{'s' * (failed != 1)} with errors. "
                "Fix the files listed above and run again."
            )

    def run_once(self, only, check, force):
        reports = sync_all(only=only, check_only=check, force=force)
        if not reports:
            roots = ", ".join(str(root) for root in settings.CONTENT_ROOTS)
            self.stdout.write(f"No courses found in: {roots}")
        for report in reports:
            text = report.format()
            if report.errors:
                self.stdout.write(self.style.ERROR(text))
            elif report.warnings:
                self.stdout.write(self.style.WARNING(text))
            else:
                self.stdout.write(text)
        return sum(1 for report in reports if report.errors)

    def watch(self, only, check):
        # A development dependency (pyproject.toml), absent from the production image.
        try:
            from watchfiles import watch
        except ImportError as error:
            raise CommandError(
                "--watch needs the development packages: run `uv sync` on your computer."
            ) from error

        roots = [str(root) for root in settings.CONTENT_ROOTS if root.is_dir()]
        self.stdout.write(f"Watching {', '.join(roots)} - Ctrl+C to stop.")
        try:
            for _changes in watch(*roots):
                self.stdout.write("")
                self.run_once(only, check, False)
        except KeyboardInterrupt:
            self.stdout.write("Stopped.")
