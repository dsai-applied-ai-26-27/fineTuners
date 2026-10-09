"""Create the folder skeleton for a new course.

    manage.py startcourse rl --title "Reinforcement Learning" --code RL --year 2026-27

Mirrors Django's own `startapp`: copies a template and fills in the blanks.
"""

import json
from pathlib import Path
from string import Template

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from ingest.discover import DOCUMENT_DIRS, SLUG, SOURCE_DIRS, find_courses

TEMPLATE = Path(__file__).resolve().parents[2] / "course_template"
CONTENT_DIRS = [*DOCUMENT_DIRS, "decks", "problems", "exams", "reference", "memory/palaces"]


class Command(BaseCommand):
    help = "Create courses/<slug>/ with course.yaml and the source/ and content/ folders."

    def add_arguments(self, parser):
        parser.add_argument("slug", help="Short address, e.g. rl or mai3.")
        parser.add_argument("--title", required=True)
        parser.add_argument("--code", help="Short code shown on the course card (default: SLUG).")
        parser.add_argument("--year", default="", help='Academic year, e.g. "2026-27".')
        parser.add_argument(
            "--semester", default="", choices=["", "winter", "summer"], help="Optional."
        )
        parser.add_argument("--hue", type=int, help="Course colour, 0-359 (default: spread out).")

    def handle(self, *args, **options):
        slug = options["slug"]
        if not SLUG.match(slug):
            raise CommandError("The slug may only use lowercase letters, digits and hyphens.")
        existing = find_courses(settings.CONTENT_ROOTS)
        target = Path(settings.COURSES_DIR) / slug
        if slug in existing or target.exists():
            raise CommandError(f"{target} already exists.")

        hue = options["hue"]
        if hue is None:
            # The golden angle keeps each new course's colour far from the previous ones.
            hue = round(210 + 137.508 * len(existing)) % 360
        if not 0 <= hue <= 359:
            raise CommandError("--hue must be between 0 and 359.")

        for name in SOURCE_DIRS:
            (target / "source" / name).mkdir(parents=True)
        for name in CONTENT_DIRS:
            (target / "content" / name).mkdir(parents=True)

        values = {
            "title": json.dumps(options["title"], ensure_ascii=False),
            "code": json.dumps(options["code"] or slug.upper(), ensure_ascii=False),
            "year": json.dumps(options["year"], ensure_ascii=False),
            "semester": json.dumps(options["semester"]),
            "hue": hue,
            "order": len(existing),
        }
        for source in TEMPLATE.rglob("*"):
            if source.is_file():
                destination = target / source.relative_to(TEMPLATE)
                destination.parent.mkdir(parents=True, exist_ok=True)
                text = Template(source.read_text(encoding="utf-8")).safe_substitute(values)
                destination.write_text(text, encoding="utf-8", newline="\n")

        self.stdout.write(self.style.SUCCESS(f"Created {target}"))
        self.stdout.write(
            "Next: put lecture slides, labs and homework under source/, then start a content\n"
            "session (see docs/AUTHORING.md) and run: manage.py sync_content " + slug
        )
