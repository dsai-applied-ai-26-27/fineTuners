"""Hand-ins: what educators do to a course, taken in on the site itself.

An educator uploads one zip, made by the educator kit, of their whole course. `take`
checks it and, if it passes, the course on the site becomes that version at once:

1. It must be plainly their course and nothing else (ingest/handin.py).
2. It must be built on the version the site has. The site remembers which version each
   educator last took from it or gave it (`Educator.synced_version`). If the course has
   changed since, someone else's work would be undone by taking this one in, so the
   person is told to fetch the latest and put their work on top of it.
3. It may add, change and remove. But whatever it removes or rewrites is shown to the
   person first, line by line, and taken in only when they have said that it is meant
   (`confirmed`): a slip of an AI assistant should not quietly delete half a course.
4. In course.yaml only the topics and the description are theirs.
5. The site's own validation, all of it, must pass.

Nothing is ever lost by a hand-in. Each one is kept whole in the database
(`HandIn.archive`: the course as it stood after it), so every earlier version can be
fetched again, and a hand-in can be taken back (`withdraw`), which puts the course back
to the version before it.

Where the files go. The owner's course files are a folder the application cannot write
to, replaced as a whole when the owner publishes. A hand-in therefore does not touch it:
the course is unpacked into a folder of its own (settings.HANDINS_DIR) and the site reads
the course from there (`overlay`, registered with ingest.live). When the owner's published
files say that they include a hand-in (the `.merged` file that import_course writes), or
are the very same files, that folder is dropped and the hand-in is marked as merged. If
the owner publishes without it, the site keeps showing the hand-in and the sync report
says so. The folder is only a working copy, rebuilt from the database when missing.
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

from . import notices
from .models import Educator, HandIn

MAX_UPLOAD = 25 * 1024 * 1024  # the zip itself
MAX_UNPACKED = 60 * 1024 * 1024  # what it may unpack to
MARKER = ".handin"  # in the folder of an unpacked course: which hand-in it is
# In the owner's own course folder: the version of the newest hand-in their files include.
# Written by `manage.py import_course`, sent along by `publish`.
MERGED = ".merged"
STALE_LOCK = 300  # seconds after which a lock is taken to be left over from a crash


class Refused(Exception):
    """A hand-in that was not taken in. `kind` says why, `lines` says what exactly.

    conflict   the course changed on the site after this person took their copy
    start      the site does not know which version this person started from
    confirm    it removes or rewrites something, and that was not confirmed
    owner      it changes what is the owner's in course.yaml
    invalid    the site's validation found errors (the lines are its report)
    nothing    it changes nothing
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
    together would each be checked against the same version, and the second to finish
    would undo what the first did.
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


def take(user, course, upload, *, confirmed=False):
    """Check an uploaded zip and, if it passes, make it the course on the site.

    `confirmed` is the person saying that what the zip removes or rewrites is meant.
    Returns the HandIn that records it; raises Refused otherwise, and then nothing at
    all has changed.
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
            raise Refused("bad", ["The site has no files for this course to work on yet."])
        current = handin.files_of(folder)
        now = handin.version_of(current)
        if handin.version_of(files) == now:
            raise Refused("nothing", ["This is exactly what the site already has."])

        # Built on what the site has? Staff are taken at their word; an educator's
        # starting point is on record from their last download or hand-in.
        role = Educator.objects.filter(user=user, series=course.series).first()
        if role is None and not user.is_staff:
            raise Refused("bad", ["You do not write this course."])
        if role is not None and not role.synced_version:
            raise Refused("start", [])
        if role is not None and role.synced_version != now:
            raise Refused("conflict", [])

        theirs = files["course.yaml"].decode("utf-8", errors="replace")
        problems = handin.protected_changes(current["course.yaml"].decode("utf-8"), theirs)
        if problems:
            raise Refused("owner", problems)
        change = handin.compare(current, files)
        if not change.only_adds and not confirmed:
            raise Refused("confirm", change.lost)

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
            base_version=now,
            version=handin.version_of(files),
            new_files=change.added,
            removed_files=change.removed,
            grown=change.grown,
            shrunk=change.shrunk,
            removed_ids=change.ids,
            lines_added=change.lines_added,
            lines_removed=change.lines_removed,
            archive=handin.pack_files(slug, files),
        )
        (target / MARKER).write_text(str(record.pk), encoding="utf-8")
    remember(user, course.series, record.version)
    notices.tell(
        notices.educators_of(course.series, but=user),
        f"{course.title} changed on the site",
        f"{record.summary}. Download the course files again before your next hand-in.",
        url=f"/educators/#course-{slug}",
    )
    notices.tell(
        [owner for owner in notices.owners() if owner.pk != user.pk],
        f"Hand-in on the site: {course.title}",
        f"{record.summary}. It is live.",
        url=f"/admin/desk/handin/{record.pk}/change/",
    )
    return record


def remember(user, series, version):
    """This person now has (or has just given the site) this version of the course.
    Their next hand-in is taken only if the site still has it."""
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


def _included(owner, record, files):
    """Whether the owner's course folder already has this hand-in: it says so itself
    (the file import_course wrote), or it is the very same files, or it holds every
    file and line of it."""
    note = owner / MERGED
    if note.is_file() and note.read_text(encoding="utf-8").strip() == record.version:
        return True
    theirs = handin.files_of(owner)
    return handin.version_of(theirs) == record.version or handin.holds(theirs, files)


def overlay(base, *, settle=False, notes=None):
    """For ingest.live: the folder to read each course from, given the owner's (`base`).

    A course with hand-ins on the site is read from the newest of them, unless the
    owner's files already include it. With `settle` (a real sync, not a check) those
    overtaken hand-ins are marked as merged and their folders removed.
    """
    try:
        rows = list(HandIn.objects.filter(status=HandIn.Status.LIVE).order_by("created_at", "pk"))
    except DatabaseError:  # the table is not there yet: a first migrate is still to come
        return base
    result, newest, count = dict(base), {}, {}
    for row in rows:
        newest[row.slug] = row
        count[row.slug] = count.get(row.slug, 0) + 1

    for slug, row in newest.items():
        owner = base.get(slug)
        if owner is None:
            continue  # the owner has taken the course away; there is nothing to show
        _slug, files = handin.unzip(bytes(row.archive), MAX_UNPACKED)
        if _included(owner, row, files):
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
                f"hand-in{'s' * (n != 1)}. Take the newest in (admin, Hand-ins, download; "
                "then import_course) and publish again."
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


def root_base(record):
    """The version the owner's files had when the hand-ins now on the site began: what
    `import_course` compares the owner's own files with."""
    first = (
        HandIn.objects.filter(slug=record.slug, status=HandIn.Status.LIVE)
        .order_by("created_at", "pk")
        .first()
    )
    return (first or record).base_version


def withdraw(record, by=None):
    """Take a hand-in back, and with it every later one for the same course: each was
    built on the one before. The course returns to the version before it, and that is
    loaded at once. Returns the sync report, or None if the course is gone."""
    later = HandIn.objects.filter(
        slug=record.slug, status=HandIn.Status.LIVE, created_at__gte=record.created_at
    )
    authors = {row.user for row in later.select_related("user") if row.user}
    later.update(status=HandIn.Status.WITHDRAWN, settled_at=timezone.now())
    folder = live.folders(settle=True).get(record.slug)
    report = sync_course(folder, force=True) if folder else None
    # Everyone who writes the course now has a copy that is ahead of the site.
    told = {*authors, *notices.educators_of(record.series)} - {by}
    notices.tell(
        told,
        f"A hand-in for `{record.slug}` was taken back",
        "The course on the site is as it was before it. Download the course files "
        "again before your next hand-in.",
        url=f"/educators/#course-{record.slug}",
    )
    return report
