"""A course's duties: the dated things to do or attend, for the owner's bot alone.

    <course>/duties.yaml          beside course.yaml, never under content/

    duties:
      - id: lab-3
        kind: lab
        title: Lab 3, convolution
        due: 2026-11-04T10:00       # or 2026-11-04 for a whole day; Sarajevo time
        place: Lab 1-12
        notes: Bring the prepared report.

Unlike every other file of a course, this one is private to the owner. The site shows it
nowhere. It is not under content/, so it never travels to an educator: a download, a
hand-in, the editor and the history take only course.yaml and content/ (ingest/handin.py),
and a hand-in that carries it is refused. The educator kit carries neither this module
nor such a file (export_authoring). It reaches the server only with the owner's `publish`,
and desk/duties.py tells the owner's bot what changed. docs/DUTIES.md says how to write it.

sync_content checks it with the rest of the course: an error here stops the course, as an
error in any of its files would.
"""

import datetime as dt
import re
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, StringConstraints, ValidationError, field_validator

from . import schemas
from .yamlio import dotted, load_yaml

FILE = "duties.yaml"
KINDS = ("lab", "test", "exam", "project", "seminar", "homework", "presentation", "other")
DUE = re.compile(r"^\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2})?$")
HINT = "see docs/DUTIES.md"

Place = Annotated[str, StringConstraints(strip_whitespace=True, max_length=200)]
Notes = Annotated[str, StringConstraints(strip_whitespace=True, max_length=2000)]


# Its own base, not schemas.Spec: the kit runs schemas.py, and nothing about duties is in it.
class _Spec(BaseModel):
    model_config = ConfigDict(extra="forbid")


class DutySpec(_Spec):
    id: schemas.Id
    kind: Literal["lab", "test", "exam", "project", "seminar", "homework", "presentation", "other"]
    title: schemas.Line
    due: str
    place: Place = ""
    notes: Notes = ""

    @field_validator("due", mode="before")
    @classmethod
    def _due(cls, value):
        # YAML reads 2026-11-04 as a date and 2026-11-04 10:00:00 as a datetime; the text
        # sent on is always one of the two shapes below, in Sarajevo time.
        if isinstance(value, dt.datetime):
            if value.tzinfo or value.second or value.microsecond:
                raise ValueError(
                    "`due` is a date and a time in Sarajevo, to the minute: 2026-11-04T10:00"
                )
            return value.strftime("%Y-%m-%dT%H:%M")
        if isinstance(value, dt.date):
            return value.isoformat()
        if not isinstance(value, str) or not DUE.match(value.strip()):
            raise ValueError(
                f"`due` must be a day (2026-11-04) or a day and a time (2026-11-04T10:00), "
                f"not `{value}`"
            )
        value = value.strip()
        try:
            dt.datetime.fromisoformat(value)
        except ValueError:
            raise ValueError(f"`{value}` is not a date that exists") from None
        return value


class DutiesFile(_Spec):
    duties: list[DutySpec]


def read(course_dir, report):
    """The duties of the course in `course_dir`: [] when it has no such file, None when the
    file has errors (each of them is in `report`)."""
    path = Path(course_dir) / FILE
    if not path.is_file():
        return []
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (UnicodeDecodeError, OSError):
        report.error(FILE, "the file cannot be read as UTF-8 text", hint=HINT)
        return None
    loaded = load_yaml(text, file=FILE, report=report)
    if loaded is None:
        return None
    if not isinstance(loaded.data, dict):
        report.error(FILE, "the file must start with `duties:` and a list below it", hint=HINT)
        return None
    try:
        spec = DutiesFile.model_validate(loaded.data)
    except ValidationError as exc:
        for error in exc.errors():
            where = tuple(part for part in error["loc"] if isinstance(part, (str, int)))
            message, hint = schemas.explain(error, typed=loaded.raw.get(where))
            report.error(
                FILE, message, line=loaded.line(where), where=dotted(where), hint=hint or HINT
            )
        return None
    seen = set()
    twice = False
    for number, duty in enumerate(spec.duties):
        if duty.id in seen:
            twice = True
            report.error(
                FILE,
                f"the id `{duty.id}` is used twice",
                line=loaded.line(("duties", number, "id")),
                where=dotted(("duties", number, "id")),
                hint="each duty needs an id of its own, and keeps it",
            )
        seen.add(duty.id)
    return None if twice else spec.duties
