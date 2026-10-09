"""Write the reference docs that are generated from the content schemas.

    manage.py export_schemas

Produces docs/schemas/<type>.schema.json (JSON Schema, for tools and editors) and
docs/content-types/fields.md (the same information as tables, for people and AI agents).
Both come from ingest/schemas.py, the models sync_content validates with, so the
documentation is always what the importer actually accepts. Re-run after changing a schema;
a test fails if the committed files are out of date.
"""

import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from ingest.fields import render_markdown
from ingest.schemas import SCHEMAS

TARGET = Path(settings.BASE_DIR) / "docs" / "schemas"
FIELDS = Path(settings.BASE_DIR) / "docs" / "content-types" / "fields.md"


def render(model):
    return json.dumps(model.model_json_schema(by_alias=True), indent=2, ensure_ascii=False) + "\n"


class Command(BaseCommand):
    help = "Regenerate docs/schemas/ and docs/content-types/fields.md from the Pydantic models."

    def handle(self, *args, **options):
        TARGET.mkdir(parents=True, exist_ok=True)
        for name, model in SCHEMAS.items():
            path = TARGET / f"{name}.schema.json"
            path.write_text(render(model), encoding="utf-8", newline="\n")
            self.stdout.write(f"wrote {path.relative_to(settings.BASE_DIR).as_posix()}")
        FIELDS.parent.mkdir(parents=True, exist_ok=True)
        FIELDS.write_text(render_markdown(), encoding="utf-8", newline="\n")
        self.stdout.write(f"wrote {FIELDS.relative_to(settings.BASE_DIR).as_posix()}")
