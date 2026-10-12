"""Notifications: lines the site leaves for a person, shown under the bell.

    notices.tell([user, ...], "Your request was answered", "Fixed, thank you.", url="/ask/")

They are how people learn of things that happen while they are away: an answer to a
request, a decision on an application, a change to a course they write, a new version of
the educator kit. The owner gets theirs the same way, beside the message to their bot.

A notification is a short title, at most a line of text, and the address of the page to
open. It says what happened and where to look; the thing itself is on that page.
"""

from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Educator, Notification

SHOWN = 12  # how many the bell lists


def tell(users, title, body="", url=""):
    """Leave one notification for each of `users`. Returns how many."""
    # A set of ids: a person who is, say, both the owner and an educator is told once.
    ids = {user.pk for user in users if user is not None and user.is_active}
    Notification.objects.bulk_create(
        Notification(user_id=pk, title=title[:160], body=body[:300], url=url[:300]) for pk in ids
    )
    return len(ids)


def owners():
    """The people who run the site."""
    return list(get_user_model().objects.filter(is_staff=True, is_active=True))


def educators_of(series, but=None):
    """Those who write this course, without `but` (the one who caused the news)."""
    roles = Educator.objects.filter(series=series).select_related("user")
    return [role.user for role in roles if but is None or role.user_id != but.pk]


def all_educators():
    roles = Educator.objects.select_related("user")
    return list({role.user_id: role.user for role in roles}.values())


def latest(user):
    """What the bell shows: the newest few, and how many of those are unread."""
    rows = list(Notification.objects.filter(user=user)[:SHOWN])
    return {"rows": rows, "unread": sum(1 for row in rows if row.read_at is None)}


def mark_read(user):
    return Notification.objects.filter(user=user, read_at__isnull=True).update(
        read_at=timezone.now()
    )
