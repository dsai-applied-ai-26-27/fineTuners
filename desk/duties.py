"""Tell the owner's bot (BMO) when the duties of a course change.

    push()          after a real sync_content: send what changed since BMO was last told
    push(["dms"])   the same, for these courses only

A course's duties (labs, tests, exams, project defences and the like, with their dates)
are the owner's own: `duties.yaml` beside course.yaml (ingest/duties.py). The site shows
them nowhere; this module is the one place they leave the server, to the bot alone.

What the bot has been told is kept, one `ToldDuty` per duty, so that a sync sends only what
is new, changed or gone. A row changes only once the bot has taken the batch it was in:
a batch that was not delivered is worked out again, and sent, by the next sync.

Delivery is the one of desk/notify.py (deliver): the bot's token in a header, https only,
one try and at most two more for a failure that may pass, a refusal final, and every
failure a log line, never an exception. Two differences. It is sent while the command
waits, since sync_content is a command and a thread would end with it. And none of it is
a message for the phone, so the ceiling and the quiet period of notifications do not
count it: what the bot tells the owner about a duty is the bot's to decide.
"""

import hashlib
import json
import logging
from dataclasses import dataclass, field

import yaml
from django.conf import settings
from django.db import transaction
from django.urls import reverse

from ingest import duties
from ingest.discover import clashes, find_courses
from ingest.report import Report

from . import notify
from .models import ToldDuty

logger = logging.getLogger(__name__)

BATCH = 50  # items in one POST, at most


def address():
    """Where the bot takes duties, or "" when there is no such address."""
    url = settings.BMO_DUTIES_URL or settings.BMO_NOTIFY_URL.replace("bmo-notify", "bmo-duties")
    # Never post duties where notifications go: the bot would read them as one.
    return "" if url == settings.BMO_NOTIFY_URL else url


def configured():
    return bool(settings.BMO_NOTIFY_TOKEN) and address().startswith("https://")


@dataclass
class Told:
    """What one push did, in numbers only: the command prints it."""

    new: int = 0
    changed: int = 0
    removed: int = 0
    waiting: int = 0  # changes the bot did not take; the next sync sends them again
    skipped: list = field(default_factory=list)  # courses whose duties.yaml has errors

    def __str__(self):
        parts = [f"{count} {name}" for name, count in self.counts() if count]
        said = "told about " + ", ".join(parts) if parts else "nothing new to tell"
        if self.waiting:
            said += f"; {self.waiting} not delivered, sent again at the next sync"
        return said

    def counts(self):
        return [("new", self.new), ("changed", self.changed), ("removed", self.removed)]


def push(only=None):
    """Send the bot every duty that is new, changed or gone. None when it is not set up."""
    if not configured():
        return None
    told = Told()
    folders = find_courses([settings.COURSES_DIR])
    for slug in clashes([settings.COURSES_DIR]):
        # Which of the two folders is the course is a guess; the sync says so already.
        folders.pop(slug, None)
        told.skipped.append(slug)
    if only:
        folders = {slug: folder for slug, folder in folders.items() if slug in only}

    now = {}
    read = set()
    for slug, folder in sorted(folders.items()):
        found = duties.read(folder, Report(course=slug))
        if found is None:
            # The sync reports the errors; until they are fixed the bot keeps what it has.
            told.skipped.append(slug)
            continue
        read.add(slug)
        code, title = _course(folder, slug)
        url = settings.SITE_URL.rstrip("/") + reverse("catalog:course", args=[slug])
        for duty in found:
            key = f"{slug}/{duty.id}"
            now[key] = {
                "key": key,
                "course": code,
                "course_title": title,
                "kind": duty.kind,
                "title": duty.title,
                "due": duty.due,
                "place": duty.place,
                "notes": duty.notes,
                "url": url,
            }

    known = {row.key: row for row in ToldDuty.objects.all()}

    def in_scope(row):
        # A course that was read, or, in a sync of everything, one whose folder is gone.
        return row.course in read or (not only and row.course not in folders)

    changes = []
    for key, item in now.items():
        if key not in known:
            changes.append(("new", item, None))
        elif known[key].sent != item:
            changes.append(("changed", item, known[key].sent))
    for key, row in known.items():
        if key not in now and in_scope(row) and row.course not in told.skipped:
            changes.append(("removed", row.sent, row.sent))
    changes.sort(key=lambda change: (change[1]["key"].split("/")[0], change[1]["due"]))

    for start in range(0, len(changes), BATCH):
        batch = changes[start : start + BATCH]
        if not _send(batch):
            told.waiting = len(changes) - start
            break
        _remember(batch)
        for change, _item, _before in batch:
            setattr(told, change, getattr(told, change) + 1)
    return told


def _course(folder, slug):
    """The code and the title of a course, from its course.yaml (already checked)."""
    try:
        data = yaml.safe_load((folder / "course.yaml").read_text(encoding="utf-8-sig")) or {}
    except (OSError, yaml.YAMLError):
        data = {}
    return str(data.get("code") or slug), str(data.get("title") or slug)


def _send(batch):
    items = [{**item, "change": change} for change, item, _before in batch]
    # The same changes from the same state are the same batch, so a batch sent again after
    # an answer that was lost has the id the bot already saw. One that comes back to an
    # earlier state starts from another one, so its id is new.
    state = [[change, item, before] for change, item, before in batch]
    digest = hashlib.sha256(json.dumps(state, sort_keys=True).encode()).hexdigest()
    payload = {"source": notify.SOURCE, "batch_id": f"dsai-duties-{digest[:32]}", "items": items}
    return notify.deliver(payload, url=address(), what="a list of duties")


@transaction.atomic
def _remember(batch):
    for change, item, _before in batch:
        if change == "removed":
            ToldDuty.objects.filter(key=item["key"]).delete()
        else:
            ToldDuty.objects.update_or_create(
                key=item["key"], defaults={"course": item["key"].split("/")[0], "sent": item}
            )
