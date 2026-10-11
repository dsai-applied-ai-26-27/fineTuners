"""Put what educators need into the content repository.

    manage.py export_authoring courses

The course files live in a repository of their own, shared with the people who write
courses. They do not have this application, so that repository carries a copy of
everything needed to write content and to check it:

    README.md  AGENTS.md  CLAUDE.md  .gitignore     from ingest/content_repo/
    docs/                                           the authoring guide, the field reference,
                                                    the schemas and the example course
    tools/check.py                                  the checker
    tools/rules/                                    the part of the importer it runs: the
                                                    modules of ingest/ that need no Django

All of it is generated: the originals are here, where they are tested with the code they
describe. Run this again after changing the authoring docs, a schema or the importer, then
commit the result in the content repository. Course folders are never touched.
"""

import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

KIT = Path(__file__).resolve().parents[2] / "content_repo"
INGEST = KIT.parent
DOCS = Path(settings.BASE_DIR) / "docs"

# The importer's first half: finding files, reading YAML, checking fields. None of these
# modules imports Django, which is what lets them run in a repository that has only Python.
RULES = ["discover.py", "load.py", "report.py", "schemas.py", "yamlio.py"]
# Kit file -> its name in the content repository.
TOP = {
    "README.md": "README.md",
    "AGENTS.md": "AGENTS.md",
    "CLAUDE.md": "CLAUDE.md",
    "gitignore": ".gitignore",
}
GUIDE = ["AUTHORING.md", "content-types", "schemas", "example-course"]

NOTE = """# How content is written

These files are copies. The originals are kept with the application, where they are
tested together with the code they describe, and are copied here by its
`export_authoring` command. Do not edit them here: the next copy would undo it.

- [AUTHORING.md](AUTHORING.md): the guide. Read it first.
- [content-types/](content-types/): one page per kind of file, and
  [fields.md](content-types/fields.md), every field of every file.
- [schemas/](schemas/): the same format as JSON Schema, for editors and tools.
- [example-course/example/](example-course/example/): a complete, valid course.

A few links in the guide lead to pages about running the site (DEPLOYMENT.md,
ARCHITECTURE.md). Those are not part of this repository, and nothing in them is needed to
write content.
"""

HEADER = "# Copied from the application by `manage.py export_authoring`. Do not edit here.\n"


def copy(source, target):
    """Replace `target` with a copy of `source` (a file or a folder)."""
    if target.is_dir():
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", "source"))
    else:
        shutil.copyfile(source, target)


class Command(BaseCommand):
    help = "Copy the authoring docs and the checker into the content repository."

    def add_arguments(self, parser):
        parser.add_argument("target", help="The content repository: the courses folder.")

    def handle(self, *args, **options):
        target = Path(options["target"]).resolve()
        if not target.is_dir():
            raise CommandError(f"{target} is not a folder.")
        if target == Path(settings.BASE_DIR).resolve():
            raise CommandError("That is the application itself. Name the courses folder.")

        for name, published in TOP.items():
            copy(KIT / name, target / published)
        for name in GUIDE:
            copy(DOCS / name, target / "docs" / name)
        (target / "docs" / "README.md").write_text(NOTE, encoding="utf-8", newline="\n")

        copy(KIT / "tools" / "check.py", target / "tools" / "check.py")
        rules = target / "tools" / "rules"
        if rules.is_dir():
            shutil.rmtree(rules)
        rules.mkdir(parents=True)
        (rules / "__init__.py").write_text(HEADER, encoding="utf-8", newline="\n")
        for name in RULES:
            text = (INGEST / name).read_text(encoding="utf-8")
            (rules / name).write_text(HEADER + text, encoding="utf-8", newline="\n")

        self.stdout.write(self.style.SUCCESS(f"Wrote the authoring kit to {target}"))
        self.stdout.write("Commit it there. Course folders were not touched.")
