"""Bring one device's copy of a person's progress and the server's copy together.

A device sends what it changed since its last visit, plus the number (`cursor`) it was given
back then. The server folds that in and answers with everything that changed after that
number, from any device, and the new number. Both sides apply the same four rules, so it
does not matter who talks to whom first, or how often:

    records    the copy graded later wins
    attempts   kept if not already known (one sitting = one moment in time)
    activity   per day, the larger count wins
    clears     the later moment wins, and everything older than it is dropped

The browser's half is static/js/store/progress.js. Nothing else writes to these tables.
"""

import re
import time
from collections import defaultdict
from datetime import UTC, date, datetime, timedelta

from django.db import transaction
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from ingest.schemas import SLUG_PATTERN

from .models import Attempt, Clear, Day, Ledger, Record

SLUG = re.compile(SLUG_PATTERN)
# A device whose clock runs ahead must not win every comparison from then on.
CLOCK_SLACK_MS = 5 * 60 * 1000
# Above this many keys, load the whole course instead of naming each key in the query.
MANY = 500
# The most one account may store. Anyone with a Google account can sign in and post to
# the sync address, so without a ceiling one person could fill the server's disk. The
# numbers are far above honest use: every item of every course is a few thousand
# records, and 4000 days is eleven years of studying daily.
LIMITS = {"records": 20_000, "attempts": 2_000, "days": 4_000}


class RecordIn(BaseModel):
    model_config = ConfigDict(extra="ignore")

    s: int = Field(ge=0, le=3)
    t: int = Field(ge=0)
    k: int = Field(default=0, ge=0, le=100_000)
    n: int = Field(default=0, ge=0, le=10_000_000)


# allow_inf_nan=False: JSON as Python reads it accepts NaN and Infinity, which the
# database and the browser's JSON parser do not. One such number would make every later
# sync of that account fail.
class AttemptIn(BaseModel):
    model_config = ConfigDict(extra="ignore", allow_inf_nan=False)

    score: float = Field(ge=-100_000, le=100_000)
    max: float = Field(ge=0, le=100_000)
    seconds: float = Field(default=0, ge=0, le=10_000_000)
    t: int = Field(ge=0)


class DayIn(BaseModel):
    model_config = ConfigDict(extra="ignore", allow_inf_nan=False)

    cards: float = Field(default=0, ge=0, le=1_000_000)
    minutes: float = Field(default=0, ge=0, le=1_000_000)


def _split(key):
    """ "mlpr/fisher-01" -> ("mlpr", "fisher-01"); None when it is not an item's name."""
    if not isinstance(key, str):
        return None
    course, _, item = key.partition("/")
    if len(course) > 80 or not SLUG.fullmatch(course) or not 0 < len(item) <= 200:
        return None
    return course, item


def _entries(payload, name, model, many=False):
    """The well-formed entries of one section of the payload (`many`: each is a list).

    One malformed entry (an old browser, a hand-edited file) is skipped rather than
    refusing the lot: a device must never get stuck unable to save.
    """
    section = payload.get(name)
    if not isinstance(section, dict):
        return
    for key, raw in section.items():
        if isinstance(raw, list) != many:
            continue
        try:
            if many:
                yield key, [model.model_validate(item) for item in raw]
            else:
                yield key, model.model_validate(raw)
        except ValidationError:
            continue


def _scope_filter(scope):
    return {} if scope == Clear.EVERYTHING else {"course": scope}


def forget(user, scope=Clear.EVERYTHING):
    """Clear a person's progress from the server's side: everything, or one course.

    It is the instruction a device sends when its owner presses Reset, given the server's
    own clock. So it travels like any other change: the person's devices receive it at
    their next sync and drop their copies, instead of sending the old grades back.
    """
    sync(user, {"clears": {scope: int(time.time() * 1000)}})


@transaction.atomic
def sync(user, payload):
    """Fold `payload` into `user`'s progress; return what changed since `payload["cursor"]`.

    One transaction: either all of a device's changes are stored, or none.
    """
    now = int(time.time() * 1000)
    latest = now + CLOCK_SLACK_MS
    ledger, _ = Ledger.objects.get_or_create(user=user)
    stamp = ledger.version + 1
    changed = False
    room = {}

    def fits(kind, model, wanted):
        """Trim `wanted` new rows to what this account may still store (see LIMITS).

        Counting costs a query, so it happens once per kind, and only when a device
        actually brings something new. Rows already stored can always be updated.
        """
        if not wanted:
            return wanted
        if kind not in room:
            room[kind] = max(0, LIMITS[kind] - model.objects.filter(user=user).count())
        kept = wanted[: room[kind]]
        room[kind] -= len(kept)
        return kept

    # -- clears, first: they decide what else is still welcome ---------------------------
    clears = {row.scope: row for row in Clear.objects.filter(user=user)}
    wanted = payload.get("clears") if isinstance(payload.get("clears"), dict) else {}
    for scope, moment in wanted.items():
        valid_scope = scope == Clear.EVERYTHING or (
            isinstance(scope, str) and len(scope) <= 80 and SLUG.fullmatch(scope)
        )
        if not valid_scope or not isinstance(moment, int) or moment <= 0:
            continue
        moment = min(moment, latest)
        row = clears.get(scope)
        if row is not None and moment <= row.cleared_at:
            continue
        if row is None:
            row = clears[scope] = Clear(user=user, scope=scope)
        row.cleared_at, row.version = moment, stamp
        row.save()
        Record.objects.filter(user=user, graded_at__lte=moment, **_scope_filter(scope)).delete()
        Attempt.objects.filter(user=user, taken_at__lte=moment, **_scope_filter(scope)).delete()
        if scope == Clear.EVERYTHING:
            Day.objects.filter(user=user).delete()
        changed = True

    everything = clears[Clear.EVERYTHING].cleared_at if Clear.EVERYTHING in clears else 0

    def floor(course):
        """Nothing of this course graded at or before this moment is kept."""
        return max(everything, clears[course].cleared_at if course in clears else 0)

    # -- records: the later grade wins ---------------------------------------------------
    by_course = defaultdict(dict)
    for key, record in _entries(payload, "records", RecordIn):
        if parts := _split(key):
            by_course[parts[0]][parts[1]] = record
    for course, items in by_course.items():
        rows = Record.objects.filter(user=user, course=course)
        if len(items) <= MANY:
            rows = rows.filter(key__in=items)
        known = {row.key: row for row in rows}
        new, newer = [], []
        for key, record in items.items():
            graded_at = min(record.t, latest)
            if graded_at <= floor(course):
                continue
            row = known.get(key)
            if row is None:
                row = Record(user=user, course=course, key=key)
                new.append(row)
            elif graded_at > row.graded_at:
                newer.append(row)
            else:
                continue
            row.state, row.streak, row.count = record.s, record.k, record.n
            row.graded_at, row.version = graded_at, stamp
        # Two statements for the whole course, however many items it has.
        new = fits("records", Record, new)
        Record.objects.bulk_create(new)
        Record.objects.bulk_update(newer, ["state", "streak", "count", "graded_at", "version"])
        changed = changed or bool(new or newer)

    # -- attempts: add the sittings not seen before --------------------------------------
    for key, attempts in _entries(payload, "attempts", AttemptIn, many=True):
        parts = _split(key)
        if not parts:
            continue
        course, paper = parts
        seen = set(
            Attempt.objects.filter(user=user, course=course, paper=paper).values_list(
                "taken_at", flat=True
            )
        )
        new = []
        for attempt in attempts:
            taken_at = min(attempt.t, latest)
            if taken_at <= floor(course) or taken_at in seen:
                continue
            seen.add(taken_at)
            new.append(
                Attempt(
                    user=user,
                    course=course,
                    paper=paper,
                    score=attempt.score,
                    max_score=attempt.max,
                    seconds=round(attempt.seconds),
                    taken_at=taken_at,
                    version=stamp,
                )
            )
        new = fits("attempts", Attempt, new)
        Attempt.objects.bulk_create(new)
        changed = changed or bool(new)

    # -- activity: per day, the larger count wins ----------------------------------------
    # Days are the device's own calendar days, so "before the clear" is only known to
    # within a day; anything clearly older than a full clear is not taken back.
    oldest = (
        datetime.fromtimestamp(everything / 1000, UTC).date() - timedelta(days=1)
        if everything
        else date.min
    )
    days = {}
    for key, value in _entries(payload, "activity", DayIn):
        try:
            day = date.fromisoformat(key)
        except (TypeError, ValueError):
            continue
        if day >= oldest:
            days[day] = value
    known = {row.day: row for row in Day.objects.filter(user=user, day__in=days)}
    for day, value in days.items():
        cards, minutes = round(value.cards), round(value.minutes)
        row = known.get(day)
        if row is None:
            if not fits("days", Day, [day]):
                continue
            Day.objects.create(user=user, day=day, cards=cards, minutes=minutes, version=stamp)
        elif cards > row.cards or minutes > row.minutes:
            row.cards, row.minutes = max(row.cards, cards), max(row.minutes, minutes)
            row.version = stamp
            row.save()
        else:
            continue
        changed = True

    if changed:
        ledger.version = stamp
        ledger.save()

    # -- the answer: everything newer than what this device has seen ---------------------
    cursor = payload.get("cursor")
    cursor = cursor if isinstance(cursor, int) and cursor >= 0 else 0
    # A number from the future means this database was rebuilt since. Send everything,
    # and ask the device to send everything too, so nothing it holds is lost.
    resync = cursor > ledger.version
    if resync:
        cursor = 0

    def since(model):
        return model.objects.filter(user=user, version__gt=cursor)

    attempts = defaultdict(list)
    for row in since(Attempt).order_by("taken_at"):
        attempts[f"{row.course}/{row.paper}"].append(
            {"score": row.score, "max": row.max_score, "seconds": row.seconds, "t": row.taken_at}
        )
    return {
        "cursor": ledger.version,
        "resync": resync,
        "records": {
            f"{row.course}/{row.key}": {
                "s": row.state,
                "t": row.graded_at,
                "k": row.streak,
                "n": row.count,
            }
            for row in since(Record)
        },
        "attempts": attempts,
        "activity": {
            row.day.isoformat(): {"cards": row.cards, "minutes": row.minutes} for row in since(Day)
        },
        "clears": {row.scope: row.cleared_at for row in since(Clear)},
    }
