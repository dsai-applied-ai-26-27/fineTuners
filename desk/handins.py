"""Hand-ins: what educators add to a course, taken in on the site itself.

An educator uploads one zip, made by the educator kit, of their whole course. `take`
checks it and, if it passes, the course on the site becomes that version at once:

1. It must be plainly their course and nothing else (ingest/handin.py).
2. It may only add. Every file the course has must still be there, and every line of
   every file, in order. New files and new lines anywhere are what a hand-in is.
3. That same rule catches a course that has moved on since this person took their copy:
   their copy lacks what was added meanwhile. They are told to fetch the latest and
   put their work on top of it.
4. The site's own validation, all of it, must pass.

Where the files go. The owner's course files are a folder the application cannot write
to, replaced as a whole when the owner publishes. A hand-in therefore does not touch it:
the course is unpacked into a folder of its own (settings.HANDINS_DIR) and the site reads
the course from there (`overlay`, registered with ingest.live). When the owner's published
files contain everything a hand-in added, that folder is dropped and the hand-in is marked
as merged. If the owner publishes without them, the site keeps showing the hand-in, and
the sync report says so: nothing an educator added is lost by a publish.

The folder is only a working copy. Each hand-in is kept whole in the database
(`HandIn.archive`), which is what is backed up, and the folder is rebuilt from it.
"""

import os
import shutil
import time
import uuid
from contextlib import contextmanager
from pathlib import Path

from django.conf import settings
from django.db.utils import DatabaseError
from django.utils import timezone

from ingest import handin, live
from ingest.sync import sync_course

from .models import Educator, HandIn

MAX_UPLOAD = 25 * 1024 * 1024  # the zip itself
MAX_UNPACKED = 60 * 1024 * 1024  # what it may unpack to
MARKER = ".handin"  # in the folder of an unpacked course: which hand-in it is
STALE_LOCK = 300  # seconds after which a lock is taken to be left over from a crash


class Refused(Exception):
    """A hand-in that was not taken in. `kind` says why, `lines` says what exactly.

    conflict   the course changed on the site after this person took their copy
    removal    it removes or rewrites lines, or changes what is the owner's in course.yaml
    invalid    the site's validation found errors (the lines are its report)
    nothing    it adds nothing
    busy       someone else is handing in the same course this very moment
    bad        it is not a zip of this course
    """

    def __init__(self, kind, lines):
        super().__init__(kind)
        self.kind = kind
        self.lines = list(lines)


def root():
    return Path(settings.HANDINS_DIR)


@contextmanager
def lock(slug):
    """One hand-in per course at a time, across the server's worker processes.

    Creating a file with O_EXCL either succeeds or fails as one step, whoever else tries
    at the same moment, which is all a lock needs. Without it two people handing in
    together would each be checked against the same course, and the second to finish
    would wipe out what the first added.
    """
    root().mkdir(parents=True, exist_ok=True)
    path = root() / f".lock-{slug}"
    if path.exists() and time.time() - path.stat().st_mtime > STALE_LOCK:
        path.unlink(missing_ok=True)
    try:
        handle = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise Refused(
            "busy", ["Someone is handing in this course right now. Try again in a minute."]
        ) from None
    try:
        yield
    finally:
        os.close(handle)
        path.unlink(missing_ok=True)


def take(user, course, upload):
    """Check an uploaded zip and, if it only adds to `course`, put it on the site.

    Returns the HandIn that records it; raises Refused otherwise, and then nothing at all
    has changed.
    """
    if upload.size > MAX_UPLOAD:
        raise Refused("bad", [f"The file is larger than {MAX_UPLOAD // 1024 // 1024} MB."])
    try:
        slug, files = handin.unzip(upload, MAX_UNPACKED)
    except handin.HandInError as error:
        raise Refused("bad", [f"{error}."]) from error
    if slug != course.slug:
        raise Refused(
            "bad", [f"This zip is the course `{slug}`. Here it has to be `{course.slug}`."]
        )

    with lock(slug):
        folder = live.folder(slug)
        if folder is None:
            raise Refused("bad", ["The site has no files for this course to add to yet."])
        current = handin.files_of(folder)
        theirs = files["course.yaml"].decode("utf-8", errors="replace")
        problems = handin.protected_changes(current["course.yaml"].decode("utf-8"), theirs)
        change = handin.compare(current, files)
        if problems or not change.ok:
            role = Educator.objects.filter(user=user, series=course.series).first()
            moved = bool(
                role and role.synced_version
            ) and role.synced_version != handin.content_version(folder)
            raise Refused("conflict" if moved else "removal", [*problems, *change.problems])
        if not change.added and not change.grown:
            raise Refused("nothing", ["This is exactly what the site already has."])

        work = root() / f".incoming-{uuid.uuid4().hex}"
        staged = work / slug
        try:
            _write(staged, files)
            # The importer validates first and writes to the database only if nothing
            # is wrong, so this one call is both the check and the going live.
            report = sync_course(staged)
            if report.errors:
                raise Refused("invalid", report.format().splitlines())
            target = root() / slug
            shutil.rmtree(target, ignore_errors=True)
            staged.rename(target)
        finally:
            shutil.rmtree(work, ignore_errors=True)

        record = HandIn.objects.create(
            user=user,
            series=course.series,
            slug=slug,
            version=handin.content_version(target),
            new_files=change.added,
            grown=change.grown,
            lines_added=change.lines,
            archive=handin.pack(target),
        )
        (target / MARKER).write_text(str(record.pk), encoding="utf-8")
    remember(user, course.series, record.version)
    return record


def remember(user, series, version):
    """This person now has (or has just given the site) this version of the course.
    It is what tells a later refusal apart: did they remove something, or did the course
    move on without them?"""
    Educator.objects.filter(user=user, series=series).update(
        synced_version=version, synced_at=timezone.now()
    )


def _write(folder, files):
    for name, data in files.items():
        path = folder / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def _unpacked(record, files):
    """The folder holding this hand-in's course, unpacking it if it is not there."""
    target = root() / record.slug
    marker = target / MARKER
    if not marker.is_file() or marker.read_text(encoding="utf-8").strip() != str(record.pk):
        shutil.rmtree(target, ignore_errors=True)
        _write(target, files)
        marker.write_text(str(record.pk), encoding="utf-8")
    return target


def overlay(base, *, settle=False, notes=None):
    """For ingest.live: the folder to read each course from, given the owner's (`base`).

    A course with hand-ins on the site is read from the newest of them, unless the
    owner's files already hold everything it added. With `settle` (a real sync, not a
    check) those overtaken hand-ins are marked as merged and their folders removed.
    """
    try:
        rows = list(HandIn.objects.filter(status=HandIn.Status.LIVE).order_by("created_at"))
    except DatabaseError:  # the table is not there yet: a first migrate is still to come
        return base
    result, newest, count = dict(base), {}, {}
    for row in rows:
        newest[row.slug] = row
        count[row.slug] = count.get(row.slug, 0) + 1

    for slug, row in newest.items():
        owner = base.get(slug)
        if owner is None:
            continue  # the owner has taken the course away; there is nothing to add to
        _slug, files = handin.unzip(bytes(row.archive), MAX_UNPACKED)
        if handin.holds(handin.files_of(owner), files):
            if settle:
                HandIn.objects.filter(slug=slug, status=HandIn.Status.LIVE).update(
                    status=HandIn.Status.MERGED, settled_at=timezone.now()
                )
            continue
        result[slug] = _unpacked(row, files)
        if notes is not None:
            n = count[slug]
            notes[slug] = (
                f"shown as handed in by its educators: the published files lack {n} "
                f"hand-in{'s' * (n != 1)}. Take them in (admin, Hand-ins, download; then "
                "import_course) and publish again."
            )
    if settle and root().is_dir():
        for folder in root().iterdir():
            # What is left over: courses whose hand-ins were merged or taken back.
            if (
                folder.is_dir()
                and not folder.name.startswith(".")
                and folder not in result.values()
            ):
                shutil.rmtree(folder, ignore_errors=True)
    return result


def withdraw(record):
    """Take a hand-in off the site, and with it every later one for the same course:
    each was built on the one before. The course goes back to what it was, and that is
    loaded at once. Returns the sync report, or None if the course is gone."""
    HandIn.objects.filter(
        slug=record.slug, status=HandIn.Status.LIVE, created_at__gte=record.created_at
    ).update(status=HandIn.Status.WITHDRAWN, settled_at=timezone.now())
    folder = live.folders(settle=True).get(record.slug)
    return sync_course(folder, force=True) if folder else None
